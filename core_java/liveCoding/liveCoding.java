import java.util.List;

public class liveCoding {
    
    /**
     * Question 1
     * @param transactions
     * @param threshold
     * @return
     */
    private List<Integer> detectFraud(List<Integer> transactions, int threshold){
        return transactions.stream()
            .filter(x -> x > threshold).toList();
    }

    public static void main(String[] args) {
        liveCoding lc = new liveCoding();

        List<Integer> transactions = List.of(20,30,50,5000);

        System.out.println(lc.detectFraud(transactions, 30));
    }
}
