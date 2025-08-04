package org.vinayak;

import java.io.File;
import java.io.IOException;

public class JavaCompilerUtil {
  public static boolean compileJavaFile(
      String javaFilePath, String classOutputFolder, String libraryJarPath) {

    // Ensure output folder exists
    File outputDir = new File(classOutputFolder);
    if (!outputDir.exists()) {
      outputDir.mkdirs();
    }

    System.out.println("Compiling Java File: " + javaFilePath);
    System.out.println("Compiling Output Dir: " + classOutputFolder);

    String java11Javac = ConfigLoader.getProperty("java11_path");

    try {
      ProcessBuilder pb =
          new ProcessBuilder(
              java11Javac, "-classpath", libraryJarPath, "-d", classOutputFolder, javaFilePath);
      pb.inheritIO(); // Show output in console
      Process process = pb.start();
      int exitCode = process.waitFor();
      System.out.println("Java 11 compiler exited with code: " + exitCode);
      return exitCode == 0;
    } catch (IOException | InterruptedException e) {
      e.printStackTrace();
      return false;
    }
  }
}
