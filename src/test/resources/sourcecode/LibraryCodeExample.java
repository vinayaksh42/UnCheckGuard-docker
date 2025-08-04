
public class LibraryCodeExample {
    public static int source() {
        return 1;
    }

    private void checkForNull(int a) {
        if (a == 0) {
            throw new NullPointerException("Null value found");
        }
    }

    public void foo() {
        int temp = add(5, 6);
        System.out.println(temp);
    }

    public int add(int a, int b) {
        checkForNull(source());
        checkForNull(a);
        checkForNull(b);
        int sum = a + b;
        return sum;
    }
}
