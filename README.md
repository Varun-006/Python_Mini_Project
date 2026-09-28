# Banking System – Python Mini Project

A comprehensive Python-based, menu-driven banking application simulating core real-world banking operations.

---

## 🌟 Main Features

1. **• Create a bank account**
   - Enter name, phone number (10 digits) & create 4-digit PIN.
   - Generates a unique 6-digit Account Number using `random`.
   - Supports optional initial deposit ($0 by default).
   - Offers instant login transition.

2. **• Login using Account Number & PIN**
   - Enter Account Number & PIN to securely authenticate.

3. **• Check account balance**
   - Displays current account balance and account holder information.

4. **• ➕ Deposit money**
   - Enter amount → Adds to current balance → Records timestamped transaction.

5. **• ➖ Withdraw money**
   - Enter amount → Checks available balance → Deducts amount → Records timestamped transaction.

6. **• Transfer money between accounts**
   - Enter receiver account number & transfer amount.
   - Validates receiver existence and checks sender's balance.
   - Updates balances and transaction logs on both accounts simultaneously.

7. **• View transaction history**
   - Displays formatted list of deposits, withdrawals, and transfers with dates and times from `datetime`.

8. **• Change PIN**
   - Enter old PIN → Enter & confirm new PIN.

9. **• Logout**
   - Ends current session & returns safely to the Main Menu.

10. **• Persistent Storage**
    - Automatically loads and saves accounts in `accounts.json`.

---

## 🔄 Project Flow Structure

```text
               CREATE ACCOUNT
                     ↓
             Account Number + PIN
                     ↓
                   LOGIN
                     ↓
       ┌───────────────────────────────┐
       │         ACCOUNT MENU          │
       ├───────────────────────────────┤
       │ 1. Check Balance              │
       │ 2. ➕ Deposit Money           │
       │ 3. ➖ Withdraw Money          │
       │ 4. Transfer Money             │
       │ 5. View Transaction History   │
       │ 6. Change PIN                 │
       │ 7. Logout                     │
       └───────────────────────────────┘
                     ↓
                   LOGOUT
                     ↓
                 MAIN MENU
```

---

## 📚 Python Concepts Used

- **Variables & Data Types**: Strings, integers, floats, and booleans.
- **Conditional Statements**: `if`, `elif`, and `else` for validation, credentials authentication, and balance checking.
- **Loops**: `while` loops for interactive menus and input retry logic.
- **Functions**: Clean, modular functions for each operation.
- **Lists & Dictionaries**: Dictionary mapping account numbers to account info; list of transaction dictionaries.
- **String Operations**: Formatting strings, `.strip()`, `.isdigit()`, and alignment.
- **Modules**:
  - `random`: Generates unique 6-digit account numbers.
  - `datetime`: Records exact date and time for transactions.
  - `json`: Persists all account data between sessions.

---

## 💻 How to Run

1. Open your terminal in the project directory:
   ```powershell
   python banking_system.py
   ```
2. Follow the on-screen menu prompts.
