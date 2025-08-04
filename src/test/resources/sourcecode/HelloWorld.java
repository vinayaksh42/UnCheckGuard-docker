import java.io.IOException;

public class HelloWorld {
  public HelloWorld() {
  }

  public static void main(String[] var0) throws IOException {
    System.out.println("Hello World!");
    throw new IOException("IO exception");
  }
}
