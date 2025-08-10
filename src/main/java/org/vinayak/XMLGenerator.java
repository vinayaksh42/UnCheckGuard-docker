package org.vinayak;

import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

public class XMLGenerator {

  public static void generateSourcesAndSinksXML(
      String[] paramTypes, List<String> sinkSignatures, String outputPath) {
    StringBuilder sb = new StringBuilder();
    sb.append("<sinkSources>\n");
    sb.append("  <category id=\"NO_CATEGORY\">\n");

    for (int i = 0; i < paramTypes.length; i++) {
      String returnType = mapTypeToJavaType(paramTypes[i]);
      sb.append("    <method signature=\"DriverStub: ")
          .append(returnType)
          .append(" source")
          .append(i)
          .append("()\">\n");
      sb.append("      <return>\n");
      sb.append("        <accessPath isSource=\"true\" isSink=\"false\"/>\n");
      sb.append("      </return>\n");
      sb.append("    </method>\n");
    }

    for (String sinkSignature : sinkSignatures) {
      sb.append("    <method signature=\"").append(sinkSignature).append("\">\n");
      sb.append("      <return>\n");
      sb.append("        <accessPath isSource=\"false\" isSink=\"true\"/>\n");
      sb.append("      </return>\n");
      sb.append("    </method>\n");
    }

    sb.append("  </category>\n");
    sb.append("</sinkSources>\n");

    try (FileWriter writer = new FileWriter(outputPath)) {
      writer.write(sb.toString());
    } catch (IOException e) {
      e.printStackTrace();
      System.out.println("Error writing SourcesAndSinks.xml");
    }
  }

  private static String mapTypeToJavaType(String type) {
    switch (type) {
      case "int":
      case "short":
      case "byte":
      case "long":
      case "float":
      case "double":
      case "boolean":
      case "char":
        return type;
      case "java.lang.String":
        return "java.lang.String";
      case "java.lang.Object":
        return "java.lang.Object";
      default:
        return type;
    }
  }
}
