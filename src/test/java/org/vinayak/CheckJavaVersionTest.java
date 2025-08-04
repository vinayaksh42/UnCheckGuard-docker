package org.vinayak;

import org.junit.jupiter.api.Test;

public class CheckJavaVersionTest {
  @Test
  public void testJavaVersion() {
    System.out.println("Java Version: " + System.getProperty("java.version"));
    System.out.println("Java Vendor: " + System.getProperty("java.vendor"));
    System.out.println("Java Home: " + System.getProperty("java.home"));
  }
}
