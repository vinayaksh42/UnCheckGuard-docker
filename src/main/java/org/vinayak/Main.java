package org.vinayak;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import sootup.callgraph.CallGraph;
import sootup.callgraph.ClassHierarchyAnalysisAlgorithm;
import sootup.core.inputlocation.AnalysisInputLocation;
import sootup.core.jimple.common.stmt.Stmt;
import sootup.core.model.Body;
import sootup.core.model.SootClass;
import sootup.core.model.SootMethod;
import sootup.core.model.SourceType;
import sootup.core.signatures.MethodSignature;
import sootup.core.typehierarchy.ViewTypeHierarchy;
import sootup.core.views.View;
import sootup.java.bytecode.inputlocation.JavaClassPathAnalysisInputLocation;
import sootup.java.bytecode.inputlocation.JrtFileSystemAnalysisInputLocation;
import sootup.java.bytecode.inputlocation.PathBasedAnalysisInputLocation;
import sootup.java.core.JavaSootMethod;
import sootup.java.core.views.JavaView;

public class Main {
  private static String getLibraryResultPath() {
    return ConfigLoader.getProperty(
        "library_result_path",
        "../LibraryResult/");
  }

  private static String getClientResultPath() {
    return ConfigLoader.getProperty("client_result_path", "../client/client_results/");
  }

  private static String getClientTempPath() {
    return ConfigLoader.getProperty("client_temp_path", ".../client/client_temp/");
  }

  public static void main(String[] args) {
    if (args.length < 1) {
      System.err.println(
          "Specify mode: analyzeLibraryMethods | analyzeClient | callgraphBasedLibraryAnalysis");
      System.exit(1);
    }

    String mode = args[0];

    switch (mode) {
      case "analyzeLibraryMethods":
        analyzeLibraryMethods(Arrays.copyOfRange(args, 1, args.length));
        break;

      case "analyzeClient":
        analyzeClient(Arrays.copyOfRange(args, 1, args.length));
        break;

      case "callgraphBasedLibraryAnalysis":
        if (args.length < 4) {
          System.err.println(
              "Usage: callgraphBasedLibraryAnalysis <path-to-JAR> <library-name> <MatchedMethods.json File> <additionalJars>");
          System.exit(1);
        }
        callgraphBasedLibraryAnalysis(
            args[1], args[2], Arrays.asList(Arrays.copyOfRange(args, 4, args.length)), args[3]);
        break;

      default:
        System.err.println("Unknown mode: " + mode);
        System.exit(1);
    }
  }

  public static void analyzeClient(String[] args) {
    if (args.length < 2) {
      System.err.println("Usage: analyzeClient <path-to-JAR> <client-name>");
      System.exit(1);
    }
    analyzeClientJAR(args[0], args[1]);
  }

  public static void analyzeLibraryMethods(String[] args) {
    if (args.length < 2) {
      System.err.println("Usage: analyzeLibraryMethods <path-to-JAR> <library-name>");
      System.exit(1);
    }
    recordMethodSignaturesForJar(args[0], args[1]);
  }

  public static void recordMethodSignaturesForJar(String pathToJAR, String libraryName) {
    Path path = Paths.get(pathToJAR);
    AnalysisInputLocation inputLocation =
        PathBasedAnalysisInputLocation.create(path, SourceType.Application);
    View view = new JavaView(inputLocation);
    JSONArray methodNameArray = new JSONArray();
    for (SootClass sootClass : view.getClasses()) {
      // save the package name in json
      for (SootMethod method : sootClass.getMethods()) {
        methodNameArray.put(method.getSignature());
      }
    }
    try (FileWriter file = new FileWriter(getClientTempPath() + libraryName + ".json")) {
      file.write(methodNameArray.toString(4));
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

  public static void analyzeClientJAR(String pathToJAR, String clientName) {
    JSONArray classArray = new JSONArray();

    Path path = Paths.get(pathToJAR);
    AnalysisInputLocation inputLocation =
        PathBasedAnalysisInputLocation.create(path, SourceType.Application);
    View view = new JavaView(inputLocation);

    for (SootClass sootClass : view.getClasses()) {
      JSONArray methodsArray = new JSONArray();

      for (SootMethod method : sootClass.getMethods()) {
        List<String> externalMethodCalls = new ArrayList<>();

        if (method.isAbstract() || method.isNative()) {
          continue;
        }

        Body body = method.getBody();

        List<Stmt> stmts = body.getStmts();
        StmtClientVisitor stmtVisitor = new StmtClientVisitor(view, externalMethodCalls);

        for (Stmt stmt : stmts) {
          stmt.accept(stmtVisitor);
        }

        JSONObject methodObject = new JSONObject();
        methodObject.put("methodSignature", method.getSignature());
        methodObject.put("external_method_calls", externalMethodCalls.toArray());
        methodsArray.put(methodObject);
      }
      classArray.put(new JSONObject().put(sootClass.getName(), methodsArray));
    }

    try (FileWriter file = new FileWriter(getClientResultPath() + clientName + ".json")) {
      file.write(classArray.toString(4));
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

  public static void callgraphBasedLibraryAnalysis(
      String pathToJAR, String library, String MatchedMethods) {
    List<String> additonalJars = new ArrayList<>();
    callgraphBasedLibraryAnalysis(pathToJAR, library, additonalJars, MatchedMethods);
  }

  public static void callgraphBasedLibraryAnalysis(
      String pathToJAR, String libraryName, List<String> additionalJars, String MatchedMethods) {
    JSONArray classArray = new JSONArray();

    // Read the JSON file and store the contents of the array in a list of strings
    List<String> matchedMethodsList = new ArrayList<>();
    try {
      String content =
          new String(Files.readAllBytes(Paths.get(MatchedMethods)), StandardCharsets.UTF_8);
      JSONArray matchedMethodsArray = new JSONArray(content);
      for (int i = 0; i < matchedMethodsArray.length(); i++) {
        matchedMethodsList.add(matchedMethodsArray.getString(i));
      }
    } catch (IOException e) {
      e.printStackTrace();
    } catch (JSONException e) {
      System.err.println("Error parsing JSON content: " + e.getMessage());
    }

    AnalysisInputLocation inputlocationJARToAnalyze =
        new JavaClassPathAnalysisInputLocation(pathToJAR, SourceType.Application);

    List<AnalysisInputLocation> inputLocations = new ArrayList<>();
    inputLocations.add(inputlocationJARToAnalyze);
    inputLocations.add(new JrtFileSystemAnalysisInputLocation(SourceType.Library));

    JavaView view = new JavaView(inputLocations);
    View viewJar = new JavaView(inputlocationJARToAnalyze);

    List<String> SootmethodList = new ArrayList<>();

    for (SootClass sootclass : viewJar.getClasses()) {
      for (SootMethod sootMethod : sootclass.getMethods()) {
        SootmethodList.add(sootMethod.toString());
      }
    }

    for (SootClass sootClass : viewJar.getClasses()) {
      JSONArray methodsArray = new JSONArray();

      if (sootClass.isLibraryClass() == true) {
        continue;
      }

      for (SootMethod method : sootClass.getMethods()) {
        List<String> uncheckedExceptions = new ArrayList<>();
        List<String> sinkForFlowDroid = new ArrayList<>();

        // check if method is part of matchedMethodsList
        // removed it for doing a libary only analysis
        if (!matchedMethodsList.contains(method.getSignature().toString())) {
          continue;
        }

        if (method.getParameterCount() == 0) {
          // FlowDroid implementation does not support methods with no parameters,
          // moreover it won't produce any results
          continue;
        }

        if (method.isAbstract() || method.isNative()) {
          continue;
        }

        try {
          Body bodychecker = method.getBody();
        } catch (Exception e) {
          continue;
        }

        // Create type hierarchy and RTA
        final ViewTypeHierarchy typeHierarchy = new ViewTypeHierarchy(view);
        ClassHierarchyAnalysisAlgorithm cha = new ClassHierarchyAnalysisAlgorithm(viewJar);

        // Create CG by initializing RTA with entry method(s)
        MethodSignature entryMethodSignature = method.getSignature();

        CallGraph cg;
        try {
          cg = cha.initialize(Collections.singletonList(entryMethodSignature));
        } catch (AssertionError ae) {
          System.err.println("AssertionError while processing method: " + method.getSignature());
          ae.printStackTrace();
          continue;
        } catch (Exception e) {
          System.err.println("Exception while processing method: " + method.getSignature());
          e.printStackTrace();
          continue;
        }

        for (MethodSignature methodSignature : cg.getMethodSignatures()) {
          Optional<? extends SootMethod> calledMethod = viewJar.getMethod(methodSignature);
          Optional<JavaSootMethod> actualMethod = view.getMethod(methodSignature);
          // iterate over all the methods in calledMethod
          if (calledMethod.isPresent()) {
            SootMethod sootMethod = calledMethod.get();
            if (sootMethod.isAbstract() || sootMethod.isNative()) {
              continue;
            }
            if (actualMethod.isPresent()) {
              SootMethod methodToCheck = actualMethod.get();
              if (methodToCheck.isAbstract() || methodToCheck.isNative()) {
                continue;
              }

              Body body;

              try {
                body = methodToCheck.getBody();
              } catch (Exception e) {
                continue;
              }

              Body.BodyBuilder bodyBuilder = Body.builder(body, Collections.emptySet());

              List<Stmt> stmts = body.getStmts();
              StmtCallGraphVisitor stmtVisitor =
                  new StmtCallGraphVisitor(
                      typeHierarchy,
                      bodyBuilder,
                      uncheckedExceptions,
                      methodSignature.toString(),
                      sinkForFlowDroid);
              for (Stmt stmt : stmts) {
                stmt.accept(stmtVisitor);
              }
            }
          }
        }
        List<String> uncheckedExceptionsResults = new ArrayList<>();
        if (!uncheckedExceptions.isEmpty()) {
          System.out.println("CHA sootup has found some unchecked Exceptions");
          uncheckedExceptionsResults =
          RunFlowDroid.flowDroidExceptionAnalysis(
            method.getSignature().toString(),
            pathToJAR,
            sinkForFlowDroid,
            uncheckedExceptionsResults,
            method,
            viewJar,
            SootmethodList);
          if (uncheckedExceptionsResults != null) {
            System.out.println("FlowDroid has found some unchecked Exceptions");
            JSONObject methodObject = new JSONObject();
            methodObject.put("methodSignature", method.getSignature());
            methodObject.put("unchecked_exceptions",
            uncheckedExceptionsResults.stream().toArray());
            methodsArray.put(methodObject);
          }
        } else {
          System.out.println("CHA sootup has not found any unchecked Exceptions");
          JSONObject methodObject = new JSONObject();
          methodObject.put("methodSignature", method.getSignature());
          methodObject.put("unchecked_exceptions",
          uncheckedExceptions.stream().toArray());
          methodsArray.put(methodObject);
        }
        JSONObject methodObject = new JSONObject();
        methodObject.put("methodSignature", method.getSignature());
        methodObject.put("unchecked_exceptions", uncheckedExceptions.stream().toArray());
        methodsArray.put(methodObject);
      }
      classArray.put(new JSONObject().put(sootClass.getName(), methodsArray));
    }
    try (FileWriter file = new FileWriter(getLibraryResultPath() + libraryName + ".json")) {
      file.write(classArray.toString(4));
    } catch (IOException e) {
      e.printStackTrace();
    }
  }
}
