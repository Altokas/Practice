import java.util.ArrayList;
import java.util.Scanner;

class Expense {
    String category;
    double amount;

    Expense(String category, double amount) {
        this.category = category;
        this.amount = amount;
    }7
}

public class ExpenseTracker {

    static ArrayList<Expense> expenses = new ArrayList<>();

    public static void addExpense(String category, double amount) {
        expenses.add(new Expense(category, amount));
        System.out.println("Expense added!");
    }

    public static void showExpenses() {
        double total = 0;
        if (expenses.isEmpty()) {
            System.out.println("No expenses yet.");
            return;
        }

        for (int i = 0; i < expenses.size(); i++) {
            Expense e = expenses.get(i);
            System.out.println((i + 1) + ". " + e.category + " - " + e.amount + "₸");
            total += e.amount;
        }

        System.out.println("Total: " + total + "₸");
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        while (true) {
            System.out.println("\n=== Expense Tracker (Java) ===");
            System.out.println("1. Add expense");
            System.out.println("2. Show expenses");
            System.out.println("3. Exit");
            System.out.print("Choose option: ");

            int choice = scanner.nextInt();

            if (choice == 1) {
                System.out.print("Category: ");
                String category = scanner.next();
                System.out.print("Amount: ");
                double amount = scanner.nextDouble();

                addExpense(category, amount);

            } else if (choice == 2) {
                showExpenses();

            } else if (choice == 3) {
                break;
            }
        }

        scanner.close();
    }
}