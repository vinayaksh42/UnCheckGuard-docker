package org.vinayak;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class ConfigLoader {
  private static Properties properties;
  private static final String CONFIG_FILE = "config.properties";

  static {
    loadConfig();
  }

  private static void loadConfig() {
    properties = new Properties();
    try (InputStream in = ConfigLoader.class.getClassLoader().getResourceAsStream(CONFIG_FILE)) {
      if (in == null) {
        throw new FileNotFoundException("config.properties not found on classpath");
      }
      properties.load(in);
    } catch (IOException ex) {
      System.err.println("Error loading config: " + ex.getMessage());
    }
  }

  public static String getProperty(String key) {
    return properties.getProperty(key);
  }

  public static String getProperty(String key, String defaultValue) {
    return properties.getProperty(key, defaultValue);
  }
}
