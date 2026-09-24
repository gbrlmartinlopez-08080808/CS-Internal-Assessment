import os
import time

from flask import Flask, render_template, redirect, url_for, request, flash, abort
from werkzeug.utils import secure_filename

from Primary.money import Money
from Primary.project import Project
from Primary.proof import Proof
from Primary.acc_balance import Acc_balance
from Algorithms.settlement import balance_settle, pair_first_settle, brute_force_settle
from Algorithms.allocation import allocate_proportional
from OCR.OCR_text_extraction import read_receipt, file_hash

app = Flask(__name__)
app.secret_key = "local-only"
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
BRUTE_FORCE_LIMIT = 9

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


def read_amount(text):
    try:
        return Money.from_display(text.replace(",", "."))
    except ValueError:
        raise ValueError(f"{text} is not an amount, write it like 12.50")


@app.route("/")
def index():
    show = request.args.get("show", "all")
    shown = []
    open_count = 0
    for project in projects:
        if project.status == "open":
            open_count += 1
        if show == "all" or project.status == show:
            shown.append(project)

    editing = None
    if request.args.get("edit") is not None:
        editing = find_project(request.args.get("edit"))

    return render_template("projects.html", shown=shown, total=len(projects),
                           open_count=open_count, show=show, editing=editing)


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


@app.route("/projects/<project_id>/rename", methods=["POST"])
def rename_project(project_id):
    project = find_project(project_id)
    name = request.form.get("name", "").strip()
    if name == "":
        flash("A project needs a name", "error")
        return redirect(url_for("index", edit=project_id))
    project.name = name
    flash(f"Renamed to {name}")
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

    paid = {}
    for member in project.members:
        paid[member] = Money(0)
    for expense in project.expenses:
        paid[expense.payer] = paid[expense.payer] + expense.amount

    plan_text = request.args.get("plan", "").strip()
    plan = None
    if plan_text != "":
        try:
            plan = allocate_proportional(read_amount(plan_text), ledger.debtors())
        except ValueError as error:
            flash(str(error), "error")

    results = []
    if tab == "settle":
        methods = [("Greedy", balance_settle), ("Pair-first", pair_first_settle), ("Brute force", brute_force_settle)]
        for name, method in methods:
            if method == brute_force_settle and len(project.members) > BRUTE_FORCE_LIMIT:
                results.append((name, None, 0))
            else:
                start = time.perf_counter()
                transfers = method(ledger.debtors(), ledger.creditors())
                results.append((name, transfers, (time.perf_counter() - start) * 1000))

    return render_template("dashboard.html", project=project, tab=tab, balances=balances,
                           paid=paid, plan=plan, plan_text=plan_text, results=results,
                           limit=BRUTE_FORCE_LIMIT)


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
        if payer is None:
            raise ValueError("Add a member first, then choose who paid")

        proof = None
        if receipt is not None and receipt.filename != "":
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            path = os.path.join(UPLOAD_FOLDER, f"{project.id}_{project.expense_seq + 1}_{secure_filename(receipt.filename)}")
            receipt.save(path)

            if amount_text == "":
                proof = read_receipt(path)
                amount_text = proof.extr_total.to_display()
                if date == "" and proof.extr_date is not None:
                    date = proof.extr_date
            else:
                proof = Proof(path, file_hash(path))

            for expense in project.expenses:
                if expense.proof is not None and expense.proof.image_hash == proof.image_hash:
                    raise ValueError("This receipt has already been added")

        if amount_text == "":
            raise ValueError("Type the amount, or attach a receipt to read it from")
        amount = read_amount(amount_text)
        project.add_expense(amount, payer, date, description, proof)
        flash(f"Added {amount.to_display()} paid by {payer.name}")
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