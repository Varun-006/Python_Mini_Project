"""
Flask Web Application for Banking System
Serves the modern frontend and provides REST API endpoints for all banking operations.
Reads and writes directly to accounts.json (shared with CLI banking_system.py).
"""

import json
import os
import random
from datetime import datetime
from flask import Flask, jsonify, render_template, request, send_from_directory

app = Flask(__name__, static_folder="static", template_folder="static")

DATA_FILE = os.path.join(os.path.dirname(__file__), "accounts.json")


def load_accounts():
    """Load accounts from accounts.json."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_accounts(accounts):
    """Save accounts to accounts.json."""
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(accounts, file, indent=4)
        return True
    except IOError:
        return False


def generate_account_number(accounts):
    """Generate a unique 6-digit account number."""
    while True:
        acc_num = str(random.randint(100000, 999999))
        if acc_num not in accounts:
            return acc_num


def record_transaction(account, trans_type, amount, details=""):
    """Record a transaction entry with current timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "type": trans_type,
        "amount": round(amount, 2),
        "balance_after": round(account["balance"], 2),
        "details": details
    }
    if "transactions" not in account:
        account["transactions"] = []
    account["transactions"].append(entry)


# ==========================================
# Frontend Route
# ==========================================

@app.route("/")
def index():
    """Serve the single-page modern banking web app."""
    return send_from_directory("static", "index.html")


# ==========================================
# REST API Endpoints
# ==========================================

@app.route("/api/register", methods=["POST"])
def register():
    """
    Create a bank account:
    Expects JSON: { name, phone, pin, initial_deposit }
    """
    data = request.get_json() or {}
    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    pin = str(data.get("pin", "")).strip()
    initial_deposit_raw = data.get("initial_deposit", 0)

    # Validations
    if not name or len(name) < 2:
        return jsonify({"success": False, "message": "Full Name must be at least 2 characters."}), 400

    if not phone.isdigit() or len(phone) != 10:
        return jsonify({"success": False, "message": "Phone number must be exactly 10 digits."}), 400

    if not pin.isdigit() or len(pin) != 4:
        return jsonify({"success": False, "message": "PIN must be exactly 4 numeric digits."}), 400

    try:
        initial_deposit = max(0.0, round(float(initial_deposit_raw), 2))
    except (ValueError, TypeError):
        initial_deposit = 0.0

    accounts = load_accounts()
    acc_num = generate_account_number(accounts)

    account = {
        "account_number": acc_num,
        "name": name,
        "phone": phone,
        "pin": pin,
        "balance": initial_deposit,
        "transactions": []
    }

    if initial_deposit > 0:
        record_transaction(
            account,
            trans_type="Deposit",
            amount=initial_deposit,
            details="Initial opening deposit"
        )

    accounts[acc_num] = account
    save_accounts(accounts)

    return jsonify({
        "success": True,
        "message": "Account created successfully!",
        "account": {
            "account_number": acc_num,
            "name": name,
            "phone": phone,
            "balance": initial_deposit,
            "transactions": account["transactions"]
        }
    })


@app.route("/api/login", methods=["POST"])
def api_login():
    """
    Login using Account Number & PIN:
    Expects JSON: { account_number, pin }
    """
    data = request.get_json() or {}
    acc_num = str(data.get("account_number", "")).strip()
    pin = str(data.get("pin", "")).strip()

    accounts = load_accounts()
    if acc_num not in accounts:
        return jsonify({"success": False, "message": "Account number not found."}), 404

    account = accounts[acc_num]
    if account.get("pin") != pin:
        return jsonify({"success": False, "message": "Incorrect PIN. Access denied."}), 401

    return jsonify({
        "success": True,
        "message": f"Welcome back, {account['name']}!",
        "account": {
            "account_number": account["account_number"],
            "name": account["name"],
            "phone": account.get("phone", ""),
            "balance": account.get("balance", 0.0),
            "transactions": account.get("transactions", [])
        }
    })


@app.route("/api/account/<acc_num>", methods=["GET"])
def get_account(acc_num):
    """Fetch refreshed account details (requires pin check or session)."""
    pin = request.args.get("pin", "").strip()
    accounts = load_accounts()

    if acc_num not in accounts:
        return jsonify({"success": False, "message": "Account not found."}), 404

    account = accounts[acc_num]
    if pin and account.get("pin") != pin:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    return jsonify({
        "success": True,
        "account": {
            "account_number": account["account_number"],
            "name": account["name"],
            "phone": account.get("phone", ""),
            "balance": account.get("balance", 0.0),
            "transactions": account.get("transactions", [])
        }
    })


@app.route("/api/lookup/<acc_num>", methods=["GET"])
def lookup_recipient(acc_num):
    """Check if recipient account exists and return receiver's name."""
    accounts = load_accounts()
    if acc_num in accounts:
        return jsonify({
            "exists": True,
            "name": accounts[acc_num]["name"]
        })
    return jsonify({"exists": False, "message": "Recipient not found."})


@app.route("/api/deposit", methods=["POST"])
def deposit():
    """
    Deposit money:
    Expects JSON: { account_number, pin, amount }
    """
    data = request.get_json() or {}
    acc_num = str(data.get("account_number", "")).strip()
    pin = str(data.get("pin", "")).strip()
    try:
        amount = round(float(data.get("amount", 0)), 2)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid amount."}), 400

    if amount <= 0:
        return jsonify({"success": False, "message": "Deposit amount must be greater than zero."}), 400

    accounts = load_accounts()
    if acc_num not in accounts or accounts[acc_num].get("pin") != pin:
        return jsonify({"success": False, "message": "Authentication failed."}), 401

    account = accounts[acc_num]
    account["balance"] = round(account["balance"] + amount, 2)

    record_transaction(
        account,
        trans_type="Deposit",
        amount=amount,
        details="Online Cash Deposit"
    )

    save_accounts(accounts)

    return jsonify({
        "success": True,
        "message": f"Successfully deposited ${amount:,.2f}!",
        "balance": account["balance"],
        "transactions": account["transactions"]
    })


@app.route("/api/withdraw", methods=["POST"])
def withdraw():
    """
    Withdraw money:
    Expects JSON: { account_number, pin, amount }
    """
    data = request.get_json() or {}
    acc_num = str(data.get("account_number", "")).strip()
    pin = str(data.get("pin", "")).strip()
    try:
        amount = round(float(data.get("amount", 0)), 2)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid amount."}), 400

    if amount <= 0:
        return jsonify({"success": False, "message": "Withdrawal amount must be greater than zero."}), 400

    accounts = load_accounts()
    if acc_num not in accounts or accounts[acc_num].get("pin") != pin:
        return jsonify({"success": False, "message": "Authentication failed."}), 401

    account = accounts[acc_num]
    if amount > account["balance"]:
        return jsonify({
            "success": False,
            "message": f"Insufficient funds! Available balance is ${account['balance']:,.2f}."
        }), 400

    account["balance"] = round(account["balance"] - amount, 2)

    record_transaction(
        account,
        trans_type="Withdrawal",
        amount=amount,
        details="ATM / Online Withdrawal"
    )

    save_accounts(accounts)

    return jsonify({
        "success": True,
        "message": f"Successfully withdrew ${amount:,.2f}!",
        "balance": account["balance"],
        "transactions": account["transactions"]
    })


@app.route("/api/transfer", methods=["POST"])
def transfer():
    """
    Transfer money between accounts:
    Expects JSON: { sender_account, pin, receiver_account, amount }
    """
    data = request.get_json() or {}
    sender_acc = str(data.get("sender_account", "")).strip()
    receiver_acc = str(data.get("receiver_account", "")).strip()
    pin = str(data.get("pin", "")).strip()

    try:
        amount = round(float(data.get("amount", 0)), 2)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid transfer amount."}), 400

    if amount <= 0:
        return jsonify({"success": False, "message": "Transfer amount must be greater than zero."}), 400

    if sender_acc == receiver_acc:
        return jsonify({"success": False, "message": "Cannot transfer to your own account."}), 400

    accounts = load_accounts()

    if sender_acc not in accounts or accounts[sender_acc].get("pin") != pin:
        return jsonify({"success": False, "message": "Authentication failed."}), 401

    if receiver_acc not in accounts:
        return jsonify({"success": False, "message": "Receiver account number not found."}), 404

    sender = accounts[sender_acc]
    receiver = accounts[receiver_acc]

    if amount > sender["balance"]:
        return jsonify({
            "success": False,
            "message": f"Insufficient balance! You have ${sender['balance']:,.2f} available."
        }), 400

    # Deduct from sender
    sender["balance"] = round(sender["balance"] - amount, 2)
    record_transaction(
        sender,
        trans_type="Transfer Sent",
        amount=amount,
        details=f"Transfer to {receiver['name']} (Acc: {receiver_acc})"
    )

    # Add to receiver
    receiver["balance"] = round(receiver["balance"] + amount, 2)
    record_transaction(
        receiver,
        trans_type="Transfer Received",
        amount=amount,
        details=f"Transfer from {sender['name']} (Acc: {sender_acc})"
    )

    save_accounts(accounts)

    return jsonify({
        "success": True,
        "message": f"Successfully transferred ${amount:,.2f} to {receiver['name']}!",
        "balance": sender["balance"],
        "transactions": sender["transactions"]
    })


@app.route("/api/change-pin", methods=["POST"])
def change_pin():
    """
    Change PIN:
    Expects JSON: { account_number, old_pin, new_pin }
    """
    data = request.get_json() or {}
    acc_num = str(data.get("account_number", "")).strip()
    old_pin = str(data.get("old_pin", "")).strip()
    new_pin = str(data.get("new_pin", "")).strip()

    if not new_pin.isdigit() or len(new_pin) != 4:
        return jsonify({"success": False, "message": "New PIN must be exactly 4 numeric digits."}), 400

    if new_pin == old_pin:
        return jsonify({"success": False, "message": "New PIN cannot be the same as your old PIN."}), 400

    accounts = load_accounts()
    if acc_num not in accounts or accounts[acc_num].get("pin") != old_pin:
        return jsonify({"success": False, "message": "Incorrect old PIN. Verification failed."}), 401

    accounts[acc_num]["pin"] = new_pin
    save_accounts(accounts)

    return jsonify({
        "success": True,
        "message": "PIN updated successfully!"
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
