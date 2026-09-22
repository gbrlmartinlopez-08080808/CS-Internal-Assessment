from flask import Flask, render_template, redirect, url_for, request

from Primary.money import Money
from Primary.member import Member
from Primary.expense import Expense
from Primary.project import Project
from Primary.acc_balance import Acc_balance
from Algorithms.settlement import balance_settle, optimal_settle
current_project = Project("p1", "Untitled Project")
app = Flask(__name__)
last_message = ""
member_count = 0
expense_count = 0


def find_member_by_id(member_id):
    for member in current_project.members:
        if member.id == member_id:
            return member
    return None


@app.route("/")
def index():
    global last_message
    message = last_message
    last_message = ""
    return render_template("project.html", project=current_project, message=message)


@app.route("/dashboard")
def dashboard():
    global last_message

    ledger = Acc_balance(current_project)
    balances = ledger.compute_balances()

    net_cents = 0
    for amount in balances.values():
        net_cents += amount.cents

    greedy_transfers = balance_settle(ledger.debtors(), ledger.creditors())
    optimal_transfers = optimal_settle(ledger.debtors(), ledger.creditors())

    message = last_message
    last_message = ""

    return render_template(
        "dashboard.html",
        project=current_project,
        balances=balances,
        net_cents=net_cents,
        greedy_transfers=greedy_transfers,
        optimal_transfers=optimal_transfers,
        message=message,
    )


@app.route("/project", methods=["POST"])
def set_project_name():
    global last_message

    name = request.form.get("name", "").strip()
    if name == "":
        last_message = "Project name cannot be empty"
    else:
        current_project.name = name
        last_message = f"Project renamed to {name}"

    return redirect(url_for("index"))


@app.route("/member", methods=["POST"])
def add_member():
    global last_message, member_count

    name = request.form.get("name", "").strip()
    if name == "":
        last_message = "Member name cannot be empty"
        return redirect(url_for("index"))

    for existing in current_project.members:
        if existing.name == name:
            last_message = f"{name} is already a member"
            return redirect(url_for("index"))

    try:
        current_project.add_member(name)
        last_message = f"Added member {name}"
    except ValueError as error:
        last_message = str(error)

    return redirect(url_for("index"))


@app.route("/expense", methods=["POST"])
def add_expense():
    global last_message, expense_count

    amount_text = request.form.get("amount", "").strip()
    date = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()

    payer = find_member_by_id(request.form.get("payer_id", ""))
    if payer is None:
        last_message = "Add a member first, then choose who paid"
        return redirect(url_for("index"))

    try:
        amount = Money.from_display(amount_text)
    except ValueError:
        last_message = f"Could not read the amount: {amount_text}"
        return redirect(url_for("index"))

    if amount.cents <= 0:
        last_message = "Amount must be greater than zero"
        return redirect(url_for("index"))

    try:
        current_project.add_expense(amount, payer, date, description)
        last_message = f"Added {amount.to_display()} paid by {payer.name}"
    except ValueError as error:
        last_message = str(error)

    return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset_project():
    global current_project, last_message, member_count, expense_count

    current_project = Project("p1", "Untitled Project")
    member_count = 0
    expense_count = 0
    last_message = "Project reset"

    return redirect(url_for("index"))
