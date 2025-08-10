package org.vinayak;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

public class CheckingExceptionTest {
  // @Test
  // public void testAnalyzeBinaryAsmOld() {
  // String pathToBinary = "resources/asm-5.1.jar";
  // String classTypeStr = "asm-5.1";
  // Main.callgraphBasedLibraryAnalysis(pathToBinary, classTypeStr);
  // }

  // @Test
  // public void testAnalyzeBinaryKryoNewFaulty() {
  // String pathToBinary = "resources/kryo-5.6.2.jar";
  // String classTypeStr = "kryo-5.6.2";
  // List<String> additonalJars = new ArrayList<>();
  // additonalJars.add("resources/minlog-1.3.1.jar");
  // additonalJars.add("resources/objenesis-3.4.jar");
  // additonalJars.add("resources/reflectasm-1.11.9.jar");
  // Main.callgraphBasedLibraryAnalysis(pathToBinary, classTypeStr,
  // additonalJars);
  // }

  @Test
  public void testAnalyzeClientReflectasm() {
    String pathToBinary = "client/client_jar/reflectasm-1.11.10-SNAPSHOT.jar";
    String classTypeStr = "reflectasm-1.11.10";
    Main.analyzeClientJAR(pathToBinary, classTypeStr);
  }

  @Test
  public void testAnalyzeClientReflectasmMain() {
    String pathToBinary = "client_jar/reflectasm-1.11.10-SNAPSHOT.jar";
    String classTypeStr = "reflectasm-1.11.10-SNAPSHOT";
    Main.main(new String[] {pathToBinary, classTypeStr, "client"});
  }

  // @Test
  // public void sootCrash() {
  // String pathToBinary = "resources/kryo-5.6.2.jar";
  // Main.methodBodyAnalysis(pathToBinary);
  // }

  @Test
  public void getPackageNameOfJar() {
    String pathToBinary = "resources/kryo-5.6.2.jar";
    Main.recordMethodSignaturesForJar(pathToBinary, "kryo-5.6.2");
  }

  @Test
  public void kryoJavaLibraryAnalysis() {
    String pathToJar =
        "/Users/vinayaksh42/Desktop/Research/BBC Research/unexpectedException/client/dep_old/kryo-3.0.3.jar";
    String libraryName = "kryo-3.0.3";
    String MatchesMethods =
        "/Users/vinayaksh42/Desktop/Research/BBC Research/unexpectedException/client/matched_methods/kryo-3.0.3#MatchedMethods.json";
    Main.callgraphBasedLibraryAnalysis(pathToJar, libraryName, MatchesMethods);
  }

  @Test
  public void testKyroOnMainTool() {
    String pathToJar =
        "/Users/vinayaksh42/Desktop/Research/BBC Research/unexpectedException/client/dep_old/kryo-3.0.3.jar";
    String LibrarName = "kryo-3.0.3";
    String MatchedMethods =
        "/Users/vinayaksh42/Desktop/Research/BBC Research/unexpectedException/client/matched_methods/kryo-3.0.3#MatchedMethods.json";
    Main.callgraphBasedLibraryAnalysis(pathToJar, LibrarName, MatchedMethods);
  }

  @Test
  public void testRealWorldScenrio() {
    String pathToJar =
        "/Users/vinayaksh42/Desktop/Research/BBC Research/unexpectedException/client/dep_new/httpcore-4.4.16.jar";
    String libraryName = "httpcore-4.4.16";
    String MatchesMethods =
        "/Users/vinayaksh42/Desktop/Research/BBC Research/unexpectedException/client/matched_methods/httpcore-4.4.6#MatchedMethods.json";
    Main.callgraphBasedLibraryAnalysis(pathToJar, libraryName, MatchesMethods);
  }
}
