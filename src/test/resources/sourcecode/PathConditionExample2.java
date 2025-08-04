
public class PathConditionExample2 {
    public String getFullName(String firstName) {
        String fullName = "";
        if (firstName != "vinayak") {
            throw new RuntimeException("wrong name");
        }

        String lastName = "sharma";
        fullName = firstName + lastName;
        return fullName;
    }
}
