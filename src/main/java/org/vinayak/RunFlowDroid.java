package org.vinayak;

import java.io.IOException;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import soot.jimple.Stmt;
import soot.jimple.infoflow.Infoflow;
import soot.jimple.infoflow.InfoflowConfiguration;
import soot.jimple.infoflow.InfoflowConfiguration.PathReconstructionMode;
import soot.jimple.infoflow.android.source.parsers.xml.XMLSourceSinkParser;
import soot.jimple.infoflow.config.IInfoflowConfig;
import soot.jimple.infoflow.entryPointCreators.DefaultEntryPointCreator;
import soot.jimple.infoflow.results.InfoflowResults;
import soot.jimple.infoflow.results.ResultSinkInfo;
import soot.jimple.infoflow.solver.cfg.InfoflowCFG;
import soot.jimple.infoflow.sourcesSinks.definitions.ISourceSinkDefinition;
import soot.jimple.infoflow.sourcesSinks.manager.BaseSourceSinkManager;
import soot.jimple.infoflow.sourcesSinks.manager.ISourceSinkManager;
import soot.options.Options;
import sootup.core.model.SootMethod;
import sootup.core.views.View;

public class RunFlowDroid {

  static class SimpleSourceSinkManager extends BaseSourceSinkManager {
    public SimpleSourceSinkManager(
        Collection<? extends ISourceSinkDefinition> sources,
        Collection<? extends ISourceSinkDefinition> sinks,
        InfoflowConfiguration config) {
      super(sources, sinks, config);
    }

    @Override
    protected boolean isEntryPointMethod(soot.SootMethod method) {
      return false;
    }
  }

  private static String[] parseParamTypes(String methodSignature) {
    Pattern p = Pattern.compile("<(.+?): (.+?) (.+?)\\((.*?)\\)>");
    Matcher m = p.matcher(methodSignature);
    if (!m.matches()) {
      throw new IllegalArgumentException("Invalid method signature: " + methodSignature);
    }
    String params = m.group(4);
    return params.isEmpty() ? new String[0] : params.split(",");
  }

  public static List<String> flowDroidExceptionAnalysis(
      String MethodSignature,
      String LibraryJarPath,
      List<String> sinkSignatures,
      List<String> uncheckedExceptionsResults,
      SootMethod method,
      View viewJar,
      List<String> SootmethodList) {
    System.out.println(LibraryJarPath);
    String driverJavaPath = ConfigLoader.getProperty("driver_java_path");
    String driverClassFolder = ConfigLoader.getProperty("driver_class_folder");
    String xmlPath = ConfigLoader.getProperty("xml_path");

    String[] paramTypes = parseParamTypes(MethodSignature);

    Boolean driverStubGenerated =
        DriverStubGenerator.generateDriverStub(driverJavaPath, method, viewJar);

    if (!driverStubGenerated) {
      System.out.println("Driver stub generation failed");
      return uncheckedExceptionsResults;
    }
    System.out.println("Generated DriverStub.java");

    XMLGenerator.generateSourcesAndSinksXML(paramTypes, sinkSignatures, xmlPath);
    System.out.println("Generated SourcesAndSinks.xml");

    boolean compileSuccess =
        JavaCompilerUtil.compileJavaFile(driverJavaPath, driverClassFolder, LibraryJarPath);
    if (!compileSuccess) {
      System.out.println("Failed to compile DriverStub.java");
      return null;
    }
    System.out.println("Compiled DriverStub.class");

    Infoflow infoflow = new Infoflow();

    XMLSourceSinkParser parser;
    try {
      parser = XMLSourceSinkParser.fromFile(xmlPath);
    } catch (IOException e) {
      throw new RuntimeException("Failed to parse XML file: " + xmlPath, e);
    }
    ISourceSinkManager ssm =
        new SimpleSourceSinkManager(parser.getSources(), parser.getSinks(), infoflow.getConfig());

    DefaultEntryPointCreator entryCreator =
        new DefaultEntryPointCreator(Collections.singletonList("<DriverStub: void run()>"));

    infoflow
        .getConfig()
        .setImplicitFlowMode(InfoflowConfiguration.ImplicitFlowMode.AllImplicitFlows);
    infoflow.getConfig().setInspectSinks(false);
    infoflow.getConfig().setInspectSinks(true);

    infoflow.getConfig().setOneSourceAtATime(false);
    infoflow.getConfig().setFlowSensitiveAliasing(true);

    infoflow.getConfig().setCallgraphAlgorithm(InfoflowConfiguration.CallgraphAlgorithm.CHA);
    infoflow
        .getConfig()
        .setStaticFieldTrackingMode(
            InfoflowConfiguration.StaticFieldTrackingMode.ContextFlowSensitive);
    infoflow
        .getConfig()
        .getPathConfiguration()
        .setPathReconstructionMode(PathReconstructionMode.Fast);

    infoflow.setSootConfig(
        new IInfoflowConfig() {
          @Override
          public void setSootOptions(Options options, InfoflowConfiguration config) {
            options.set_prepend_classpath(true);
            options.set_allow_phantom_refs(true);
          }
        });

    infoflow.computeInfoflow(driverClassFolder, LibraryJarPath, entryCreator, ssm);

    InfoflowResults results = infoflow.getResults();
    InfoflowCFG iCfg = new InfoflowCFG();

    if (!results.isEmpty()) {
      for (ResultSinkInfo sink : results.getResults().keySet()) {
        Stmt stmt = sink.getStmt();
        String exceptionMethodname = iCfg.getMethodOf(stmt).getSignature();
        if (!SootmethodList.contains(exceptionMethodname)) {
          break;
        }

        uncheckedExceptionsResults.add(
            stmt.getInvokeExpr().getMethod().getDeclaringClass().toString()
                + " "
                + iCfg.getMethodOf(stmt).getSignature());
      }
    }
    return uncheckedExceptionsResults;
  }
}
