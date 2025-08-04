import java.lang.reflect.Method;

public class FaultyCode {
    public Object DoNothing(Object object) {
        return object;
    }

    private String someMethod(Object object) {
        Object temp;
        try {
            // Some operation on 'object' that may throw an exception
            temp = DoNothing(object);
        } catch (Exception e) {
            throw new RuntimeException("Object must implement SomeInterface.");
        }

        try {
            return (String) temp;
        } catch (Exception e) {
            throw new RuntimeException("Operation must return a SomeType instance: ");
        }
    }

}
