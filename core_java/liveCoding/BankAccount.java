import java.util.List;
import java.util.stream.Stream;

public class BankAccount {
    
    private String accountNumber;
    private String ownerName;
    private double balance;


    public BankAccount(String accountNumber, String ownerName, double balance){
        
        this.accountNumber = accountNumber;
        this.ownerName = ownerName;
        setBalance(balance);

    }

    private void setBalance(double balance){
        if (balance < 0) throw new IllegalArgumentException("Balance must be > 0");
        this.balance = balance;
    }

    public double getBalance(){
        return balance;
    }

    public String getAccountNumber(){
        return accountNumber;
    }

    public String getOwnerName(){
        return ownerName;
    }

    public void deposit(double amount){
        if (amount < 0) throw new IllegalArgumentException("Amount must be > 0");
        this.balance+=amount;
    }

    public double withdraw(double amount){
        if (amount > this.balance) throw new IllegalArgumentException("Amount can not be > balance");
        this.balance -= amount;
        return amount;
    }

    public String getAccountInfo(){
        return String.format("Account: %s%nOwner: %s%nBalance: %.2f%n", getAccountNumber(),getOwnerName(),getBalance());
    }

    public double totalAmountDepositedStream(List<Double> transactions){
        return transactions.stream()
            .filter(x -> x>0).mapToDouble(Double::doubleValue).sum();
    } 

    public double totalAmountWithdrawnStream(List<Double> transactions){
        return transactions.stream()
            .filter(x -> x<0).mapToDouble(Double::doubleValue).sum();
    } 

    public double largestTransaction(List<Double> transactions){
        return transactions.stream()
            .mapToDouble(Math::abs).max().orElse(0.0);
    }

    public List<Double> listDeposits(List<Double> transactions){
        return transactions.stream()
            .filter(x -> x>0).toList();
    }



    public static void main(String[] args) {
        BankAccount ba = new BankAccount("12345", "Basil", 100);
        List<Double> transactions = List.of(120.00,130.00,50.00,-50.00,-100.00);

        ba.deposit(50);
        System.out.println(ba.getBalance());

        ba.withdraw(30);
        System.out.println(ba.getBalance());

        System.out.println(ba.getAccountInfo());

        System.out.println(ba.totalAmountDepositedStream(transactions));
        System.out.println(ba.totalAmountWithdrawnStream(transactions));
        System.out.println(ba.largestTransaction(transactions));
        System.out.println(ba.listDeposits(transactions));
    }

}
