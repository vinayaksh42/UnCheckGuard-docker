package org.vinayak;

import java.io.FileWriter;
import sootup.core.IdentifierFactory;
import sootup.core.model.SootMethod;
import sootup.core.views.View;

public class DriverStubGenerator {

  public static Boolean generateDriverStub(String outputFilePath, SootMethod method, View viewJar) {

    System.out.println("[INFO] Generating driver stub for: " + method.getSignature());

    boolean isStatic = method.isStatic();
    boolean isAbstract = method.isAbstract();
    String returnType = method.getReturnType().toString();
    IdentifierFactory factory = viewJar.getIdentifierFactory();
    boolean isConstructor = factory.isConstructorSignature(method.getSignature());
    String fqClassName = method.getDeclaringClassType().getFullyQualifiedName();

    if (isAbstract) {
      System.out.println("[INFO] Skipping abstract method: " + method.getSignature());
      return false;
    }

    StringBuilder sb = new StringBuilder();
    sb.append("public class DriverStub {\n\n");

    // Generate source methods
    for (int i = 0; i < method.getParameterCount(); i++) {
      String type = method.getParameterType(i).toString().replace('$', '.');
      sb.append("    public static ")
          .append(type)
          .append(" source")
          .append(i)
          .append("() {\n")
          .append("        return ")
          .append(dummyReturn(type))
          .append(";\n")
          .append("    }\n\n");
    }

    // Generate run method
    sb.append("    public static void run() {\n");
    StringBuilder args = new StringBuilder();
    for (int i = 0; i < method.getParameterCount(); i++) {
      if (i > 0) args.append(", ");
      args.append("source").append(i).append("()");
    }

    if (isConstructor) {
      sb.append("        new ")
          .append(fqClassName.replace('$', '.'))
          .append("(")
          .append(args)
          .append(");\n");
    } else if (isStatic) {
      if (!"void".equals(returnType)) {
        sb.append("        ").append(returnType).append(" result = ");
      } else {
        sb.append("        ");
      }
      sb.append(fqClassName.replace('$', '.'))
          .append(".")
          .append(method.getName())
          .append("(")
          .append(args)
          .append(");\n");
    } else {
      if (!"void".equals(returnType)) {
        sb.append("        ").append(returnType).append(" result = ");
      } else {
        sb.append("        ");
      }
      sb.append("new ")
          .append(fqClassName.replace('$', '.'))
          .append("().")
          .append(method.getName())
          .append("(")
          .append(args)
          .append(");\n");
    }

    sb.append("    }\n");
    sb.append("}\n");

    try (FileWriter writer = new FileWriter(outputFilePath)) {
      writer.write(sb.toString());
      System.out.println("[INFO] Driver stub written to: " + outputFilePath);
      return true;
    } catch (Exception e) {
      System.err.println("[ERROR] Failed to write stub file.");
      e.printStackTrace();
      return false;
    }
  }

  private static String dummyReturn(String type) {
    switch (type) {
      case "int":
      case "short":
      case "byte":
        return "0";
      case "long":
        return "0L";
      case "float":
        return "0.0f";
      case "double":
        return "0.0";
      case "boolean":
        return "false";
      case "char":
        return "'a'";
      default:
        return "null";
    }
  }
}
