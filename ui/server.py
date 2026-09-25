import os

from flask import Flask, render_template, redirect, url_for, request, flash, abort
from werkzeug.utils import secure_filename

from Primary.money import Money
from Primary.project import Project
from Primary.acc_balance import Acc_balance
from Algorithms.settlement import pair_first_settle
from Algorithms.allocation import allocate_proportional
from OCR.OCR_text_extraction import read_receipt

app = Flask(__name__)
app.secret_key = "local-only"
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

projects = []
project_seq = 0


def find_project(project_id):
    for project in projects:
        if project.id == project_id:
            return project
    abort(404)


def find_member(project, member_id):
    for member in project.members:
        if member.id == member_id:
            return member
    return None


@app.route("/")
def index():
    return render_template("projects.html", projects=projects)


@app.route("/projects/new", methods=["POST"])
def create_project():
    global project_seq
    name = request.form.get("name", "").strip()
    if name == "":
        flash("Type a name for the new project", "error")
    else:
        project_seq += 1
        projects.append(Project(f"p{project_seq}", name))
        flash(f"Created {name}")
    return redirect(url_for("index"))


@app.route("/projects/<project_id>/delete", methods=["POST"])
def delete_project(project_id):
    project = find_project(project_id)
    projects.remove(project)
    flash(f"Deleted {project.name}")
    return redirect(url_for("index"))


@app.route("/projects/<project_id>")
def dashboard(project_id):
    project = find_project(project_id)
    tab = request.args.get("tab", "members")
    ledger = Acc_balance(project)
    balances = ledger.compute_balances()
    transfers = pair_first_settle(ledger.debtors(), ledger.creditors())

    plan_text = request.args.get("plan", "").strip()
    payers = request.args.get("payers", "all")
    plan = None
    if plan_text != "":
        try:
            num_payers = "all"
            if payers != "all":
                num_payers = int(payers)
            plan = allocate_proportional(Money.from_display(plan_text), balances, num_payers=num_payers)
        except ValueError as error:
            flash(str(error), "error")

    return render_template("dashboard.html", project=project, tab=tab, balances=balances,
                           transfers=transfers, plan=plan, plan_text=plan_text, payers=payers)


@app.route("/projects/<project_id>/member", methods=["POST"])
def add_member(project_id):
    project = find_project(project_id)
    try:
        member = project.add_member(request.form.get("name", "").strip())
        flash(f"Added {member.name}")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("dashboard", project_id=project_id, tab="members"))


@app.route("/projects/<project_id>/purchase", methods=["POST"])
def add_purchase(project_id):
    project = find_project(project_id)
    payer = find_member(project, request.form.get("payer_id", ""))
    amount_text = request.form.get("amount", "").strip()
    date = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()
    receipt = request.files.get("receipt")

    try:
        proof = None
        if receipt is not None and receipt.filename != "":
            path = os.path.join(UPLOAD_FOLDER, f"{project.id}_{project.expense_seq + 1}_{secure_filename(receipt.filename)}")
            receipt.save(path)
            proof = read_receipt(path)
            if amount_text == "" and proof.extr_total is not None:
                amount_text = proof.extr_total.to_display()
            if date == "" and proof.extr_date is not None:
                date = proof.extr_date

        if amount_text == "":
            raise ValueError("Type the amount, or attach a receipt with a readable total")
        amount = Money.from_display(amount_text)
        project.add_expense(amount, payer, date, description, proof)

        message = f"Added {amount.to_display()} paid by {payer.name}"
        if proof is not None and proof.status == "unreadable":
            message += ", but the receipt could not be read"
        flash(message)
    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for("dashboard", project_id=project_id, tab="purchases"))


@app.route("/projects/<project_id>/close", methods=["POST"])
def close_project(project_id):
    project = find_project(project_id)
    try:
        project.close()
        flash(f"{project.name} is closed and marked as settled")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("dashboard", project_id=project_id, tab="settle"))