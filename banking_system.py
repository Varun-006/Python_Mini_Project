"""
Banking System – Mini Project
A menu-driven Python application simulating core banking operations.

Main Features:
• Create a bank account ----- Enter name, phone number & create PIN
• Login using Account Number & PIN ----- Enter account number & PIN
• Check account balance ----- Display current account balance
• ➕ Deposit money ----- Enter amount → Add to balance
• ➖ Withdraw money ----- Enter amount → Check balance → Deduct amount
• Transfer money between accounts ----- Enter receiver acc number & transfer
• View transaction history ----- Display deposits, withdrawals & transfers
• Change PIN ----- Enter old PIN → Enter & confirm new PIN
• Logout ----- End current session & return to main menu

Python Modules:
• random: Generate unique account numbers
• datetime: Record transaction date and time
• json: Persistent data storage
"""

import json
import os
import random
from datetime import datetime

DATA_FILE = "accounts.json"


# ==========================================
# Data Persistence Functions (JSON)
# ==========================================

def load_accounts():
    """Load accounts from accounts.json if it exists; return dict."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            print("\n[!] Notice: Could not parse existing accounts.json. Starting fresh.")
            return {}
    return {}


def save_accounts(accounts):
    """Save all account dictionaries to accounts.json."""
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(accounts, file, indent=4)
    except IOError as e:
        print(f"\n[!] Error saving account data: {e}")


# ==========================================
# Helper & Validation Functions
# ==========================================

def generate_account_number(accounts):
    """Generate a unique 6-digit account number using random."""
    while True:
        acc_num = str(random.randint(100000, 999999))
        if acc_num not in accounts:
            return acc_num


def record_transaction(account, trans_type, amount, details=""):
    """
    Record a transaction entry with timestamp from datetime module.
    Types: 'Deposit', 'Withdrawal', 'Transfer Sent', 'Transfer Received'
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": now,
        "type": trans_type,
        "amount": round(amount, 2),
        "balance_after": round(account["balance"], 2),
        "details": details
    }
    account["transactions"].append(entry)


def validate_pin(prompt="Enter 4-digit PIN: "):
    """Validate that PIN is exactly 4 numerical digits."""
    while True:
        pin = input(prompt).strip()
        if len(pin) == 4 and pin.isdigit():
            return pin
        print("Invalid PIN! PIN must be exactly 4 numeric digits. Try again.")


def validate_phone(prompt="Enter 10-digit Phone Number: "):
    """Validate that phone number is exactly 10 numerical digits."""
    while True:
        phone = input(prompt).strip()
        if len(phone) == 10 and phone.isdigit():
            return phone
        print("Invalid Phone Number! Must be exactly 10 digits. Try again.")


def get_positive_amount(prompt):
    """Safely input a strictly positive numerical amount."""
    while True:
        val = input(prompt).strip()
        try:
            amount = float(val)
            if amount <= 0:
                print("Amount must be greater than zero. Try again.")
                continue
            return round(amount, 2)
        except ValueError:
            print("Invalid input! Please enter a valid number.")


# ==========================================
# Feature 1: Create a Bank Account
# ==========================================

def create_account(accounts):
    """
    • Create a bank account ----- Enter name, phone number & create PIN
    Generates Account Number and allows optional initial deposit.
    """
    print("\n" + "=" * 50)
    print("           CREATE A BANK ACCOUNT                  ")
    print("=" * 50)

    # 1. Enter Name
    name = input("Enter Name: ").strip()
    while not name or any(char.isdigit() for char in name):
        print("Name cannot be empty and should not contain numbers.")
        name = input("Enter Name: ").strip()

    # 2. Enter Phone Number
    phone = validate_phone("Enter 10-digit Phone Number: ")

    # 3. Create PIN
    pin = validate_pin("Create 4-digit PIN: ")

    # Optional initial deposit (default 0 if blank)
    initial_deposit = 0.0
    dep_input = input("Enter Initial Deposit Amount (optional, press Enter for $0): ").strip()
    if dep_input:
        try:
            dep_val = float(dep_input)
            if dep_val > 0:
                initial_deposit = round(dep_val, 2)
        except ValueError:
            print("Invalid initial deposit entered. Starting balance set to $0.00.")

    # Generate unique account number
    account_number = generate_account_number(accounts)

    accounts[account_number] = {
        "account_number": account_number,
        "name": name,
        "phone": phone,
        "pin": pin,
        "balance": initial_deposit,
        "transactions": []
    }

    if initial_deposit > 0:
        record_transaction(
            accounts[account_number],
            trans_type="Deposit",
            amount=initial_deposit,
            details="Initial opening deposit"
        )

    save_accounts(accounts)

    print("\n" + "-" * 50)
    print(">>> Bank Account Created Successfully! <<<")
    print(f" Account Holder : {name}")
    print(f" Phone Number   : {phone}")
    print(f" Account Number : {account_number}")
    print(f" Security PIN   : {pin}")
    print(f" Initial Balance: ${initial_deposit:,.2f}")
    print("-" * 50)
    print("Note: Use your Account Number and PIN to log in.\n")

    # Convenience prompt: Log in right away
    auto_login = input("Would you like to log in to this account now? (y/n): ").strip().lower()
    if auto_login in ["y", "yes"]:
        account_menu(accounts, account_number)


# ==========================================
# Feature 2: Login using Account Number & PIN
# ==========================================

def login(accounts):
    """
    • Login using Account Number & PIN ----- Enter account number & PIN
    """
    print("\n" + "=" * 50)
    print("                     LOGIN                        ")
    print("=" * 50)

    acc_num = input("Enter Account Number: ").strip()
    pin = input("Enter 4-digit PIN: ").strip()

    if acc_num not in accounts:
        print("\n[!] Error: Account Number not found. Please create an account first.")
        return

    account = accounts[acc_num]

    if account["pin"] != pin:
        print("\n[!] Error: Incorrect PIN! Access Denied.")
        return

    print(f"\n[✓] Login successful! Welcome back, {account['name']}!")
    account_menu(accounts, acc_num)


# ==========================================
# Feature 3: Check Account Balance
# ==========================================

def check_balance(account):
    """
    • Check account balance ---- Display current account balance
    """
    print("\n" + "-" * 45)
    print("            CHECK ACCOUNT BALANCE            ")
    print("-" * 45)
    print(f" Account Number : {account['account_number']}")
    print(f" Account Holder : {account['name']}")
    print(f" Current Balance: ${account['balance']:,.2f}")
    print("-" * 45)


# ==========================================
# Feature 4: ➕ Deposit Money
# ==========================================

def deposit_money(accounts, account):
    """
    • ➕ Deposit money ---- Enter amount → Add to balance
    """
    print("\n" + "-" * 45)
    print("               ➕ DEPOSIT MONEY              ")
    print("-" * 45)

    amount = get_positive_amount("Enter amount to deposit ($): ")
    account["balance"] += amount

    record_transaction(
        account,
        trans_type="Deposit",
        amount=amount,
        details="Cash Deposit"
    )

    save_accounts(accounts)

    print("\n[✓] Deposit Successful!")
    print(f" Added to balance : ${amount:,.2f}")
    print(f" Updated Balance  : ${account['balance']:,.2f}")


# ==========================================
# Feature 5: ➖ Withdraw Money
# ==========================================

def withdraw_money(accounts, account):
    """
    • ➖ Withdraw money --- Enter amount → Check balance → Deduct amount
    """
    print("\n" + "-" * 45)
    print("              ➖ WITHDRAW MONEY             ")
    print("-" * 45)
    print(f" Current Available Balance: ${account['balance']:,.2f}")

    amount = get_positive_amount("Enter amount to withdraw ($): ")

    # Check balance
    if amount > account["balance"]:
        print("\n[!] Withdrawal Failed: Insufficient balance!")
        print(f" Requested : ${amount:,.2f}")
        print(f" Available : ${account['balance']:,.2f}")
        return

    # Deduct amount
    account["balance"] -= amount

    record_transaction(
        account,
        trans_type="Withdrawal",
        amount=amount,
        details="Cash Withdrawal"
    )

    save_accounts(accounts)

    print("\n[✓] Withdrawal Successful!")
    print(f" Deducted Amount  : ${amount:,.2f}")
    print(f" Remaining Balance: ${account['balance']:,.2f}")


# ==========================================
# Feature 6: Transfer Money Between Accounts
# ==========================================

def transfer_money(accounts, account):
    """
    • Transfer money between accounts --- Enter receiver acc number & transfer
    """
    print("\n" + "-" * 45)
    print("       TRANSFER MONEY BETWEEN ACCOUNTS       ")
    print("-" * 45)
    print(f" Your Available Balance: ${account['balance']:,.2f}")

    receiver_acc = input("Enter Receiver's Account Number: ").strip()

    if receiver_acc == account["account_number"]:
        print("\n[!] Error: You cannot transfer money to your own account.")
        return

    if receiver_acc not in accounts:
        print("\n[!] Error: Receiver Account Number does not exist!")
        return

    receiver = accounts[receiver_acc]
    print(f" Receiver Name: {receiver['name']}")

    amount = get_positive_amount("Enter amount to transfer ($): ")

    # Check balance
    if amount > account["balance"]:
        print("\n[!] Transfer Failed: Insufficient balance.")
        print(f" Requested: ${amount:,.2f} | Available: ${account['balance']:,.2f}")
        return

    # Deduct from sender
    account["balance"] -= amount
    record_transaction(
        account,
        trans_type="Transfer Sent",
        amount=amount,
        details=f"Transfer to {receiver['name']} (Acc: {receiver_acc})"
    )

    # Add to receiver
    receiver["balance"] += amount
    record_transaction(
        receiver,
        trans_type="Transfer Received",
        amount=amount,
        details=f"Transfer from {account['name']} (Acc: {account['account_number']})"
    )

    save_accounts(accounts)

    print("\n[✓] Transfer Completed Successfully!")
    print(f" Transferred : ${amount:,.2f} to {receiver['name']} ({receiver_acc})")
    print(f" Your Balance: ${account['balance']:,.2f}")


# ==========================================
# Feature 7: View Transaction History
# ==========================================

def view_transaction_history(account):
    """
    • View transaction history --- Display deposits, withdrawals & transfers
    """
    print("\n" + "=" * 72)
    print(f" TRANSACTION HISTORY: {account['name']} (Acc: {account['account_number']})")
    print("=" * 72)

    transactions = account.get("transactions", [])

    if not transactions:
        print(" No transactions found.")
        print("=" * 72)
        return

    print(f"{'Date & Time':<20} | {'Type':<18} | {'Amount ($)':<12} | {'Balance ($)':<12}")
    print("-" * 72)

    for tx in transactions:
        sign = "+" if "Deposit" in tx["type"] or "Received" in tx["type"] else "-"
        amt_str = f"{sign}{tx['amount']:,.2f}"
        bal_str = f"${tx['balance_after']:,.2f}"
        print(f"{tx['timestamp']:<20} | {tx['type']:<18} | {amt_str:<12} | {bal_str:<12}")
        if tx.get("details"):
            print(f"   ↳ {tx['details']}")

    print("=" * 72)


# ==========================================
# Feature 8: Change PIN
# ==========================================

def change_pin(accounts, account):
    """
    • Change PIN ---- Enter old PIN → Enter & confirm new PIN
    """
    print("\n" + "-" * 45)
    print("                  CHANGE PIN                 ")
    print("-" * 45)

    old_pin = input("Enter Old 4-digit PIN: ").strip()
    if old_pin != account["pin"]:
        print("\n[!] Error: Old PIN is incorrect! PIN change cancelled.")
        return

    new_pin = validate_pin("Enter New 4-digit PIN: ")

    if new_pin == old_pin:
        print("\n[!] Error: New PIN cannot be the same as your old PIN.")
        return

    confirm_pin = input("Confirm New 4-digit PIN: ").strip()
    if new_pin != confirm_pin:
        print("\n[!] Error: PIN confirmation does not match! PIN change cancelled.")
        return

    account["pin"] = new_pin
    save_accounts(accounts)
    print("\n[✓] Success: PIN changed successfully!")


# ==========================================
# Account Menu (Logged In)
# ==========================================

def account_menu(accounts, acc_num):
    """
    Account Menu displaying all operations:
    1. Check Balance
    2. ➕ Deposit Money
    3. ➖ Withdraw Money
    4. Transfer Money Between Accounts
    5. View Transaction History
    6. Change PIN
    7. Logout
    """
    while True:
        account = accounts[acc_num]

        print("\n" + "┌" + "─" * 43 + "┐")
        print("│               ACCOUNT MENU                │")
        print("├" + "─" * 43 + "┤")
        print("│ 1. Check Balance                          │")
        print("│ 2. ➕ Deposit Money                       │")
        print("│ 3. ➖ Withdraw Money                      │")
        print("│ 4. Transfer Money Between Accounts        │")
        print("│ 5. View Transaction History               │")
        print("│ 6. Change PIN                             │")
        print("│ 7. Logout                                 │")
        print("└" + "─" * 43 + "┘")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            check_balance(account)
        elif choice == "2":
            deposit_money(accounts, account)
        elif choice == "3":
            withdraw_money(accounts, account)
        elif choice == "4":
            transfer_money(accounts, account)
        elif choice == "5":
            view_transaction_history(account)
        elif choice == "6":
            change_pin(accounts, account)
        elif choice == "7":
            # • Logout --- End current session & return to main menu
            print(f"\n[✓] Logged out successfully. Ending session for {account['name']}...")
            break
        else:
            print("[!] Invalid option. Please enter a number between 1 and 7.")


# ==========================================
# Main Menu
# ==========================================

def main_menu():
    """Main application loop."""
    accounts = load_accounts()

    while True:
        print("\n" + "=" * 50)
        print("             BANKING SYSTEM                  ")
        print("=" * 50)
        print(" 1. Create a Bank Account")
        print(" 2. Login using Account Number & PIN")
        print(" 3. Exit Application")
        print("=" * 50)

        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            create_account(accounts)
        elif choice == "2":
            login(accounts)
        elif choice == "3":
            save_accounts(accounts)
            print("\nThank you for using the Banking System. Goodbye!\n")
            break
        else:
            print("[!] Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main_menu()
