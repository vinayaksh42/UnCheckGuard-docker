import java.util.Random;

public class UncheckedException {
  private Random random = new Random();

  // Method with 1 unchecked exceptions
  public void methodWithTwoUncheckedExceptions() {
    // This will throw an IllegalArgumentException
    // randomise the condition to throw the exception
    if (random.nextBoolean()) {
      throw new IllegalArgumentException("Illegal argument exception");
    } else {
      // This will throw an IllegalStateException
      throw new IllegalStateException("Illegal state exception");
    }
  }

  // Method with 3 unchecked exceptions
  public void methodWithThreeUncheckedExceptions() {
    // randomise the condition to throw the exception
    if (random.nextBoolean()) {
      // This will throw a NullPointerException
      throw new NullPointerException("Null pointer exception");
    } else if (random.nextBoolean()) {
      // This will throw an IndexOutOfBoundsException
      throw new IndexOutOfBoundsException("Index out of bounds exception");
    } else {
      // This will throw a ClassCastException
      throw new ClassCastException("Class cast exception");
    }
  }

  // Method with 1 unchecked exception
  public void methodWithOneUncheckedException() {
    // This will throw an ArithmeticException
    throw new ArithmeticException("Arithmetic exception");
  }
}
