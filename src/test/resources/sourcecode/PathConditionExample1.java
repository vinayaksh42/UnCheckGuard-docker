
public class PathConditionExample1 {
    public String getFullName(String firstName) {
        String fullName = "";
        if (firstName != "vinayak") {
            firstName = "vinayak";
        }

        String lastName = "sharma";
        if (lastName == "sharma") {
            if (lastName.length() == 6) {
                throw new RuntimeException("Last name is too long");
            }
        }
        fullName = firstName + lastName;
        return fullName;
    }
}
