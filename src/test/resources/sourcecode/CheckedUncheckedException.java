import java.io.IOException;
import java.util.Random;

public class CheckedUncheckedException {
    private Random random = new Random();

    // Method with both checked and unchecked exceptions
    public void methodWithMixedExceptions() throws IOException {
        // This will throw an IOException (checked exception)
        if (random.nextBoolean()) {
            throw new IOException("IO exception");
        } else if (random.nextBoolean()) {
            // This will throw an IllegalArgumentException (unchecked exception)
            throw new IllegalArgumentException("Illegal argument exception");
        } else {
            // This will throw an IllegalStateException (unchecked exception)
            throw new IllegalStateException("Illegal state exception");
        }
    }

    // Method with only checked exceptions
    public void methodWithCheckedExceptions() throws IOException, ClassNotFoundException {
        // This will throw an IOException (checked exception)
        if (random.nextBoolean()) {
            throw new IOException("IO exception");
        } else {
            // This will throw a ClassNotFoundException (checked exception)
            throw new ClassNotFoundException("Class not found exception");
        }
    }

    // Method with only unchecked exceptions
    public void methodWithUncheckedExceptions() {
        // This will throw a NullPointerException (unchecked exception)
        if (random.nextBoolean()) {
            throw new NullPointerException("Null pointer exception");
        } else {
            // This will throw an ArithmeticException (unchecked exception)
            throw new ArithmeticException("Arithmetic exception");
        }
    }
}
