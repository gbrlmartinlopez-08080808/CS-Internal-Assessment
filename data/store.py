import os
import json

from Primary.money import Money
from Primary.member import Member
from Primary.proof import Proof
from Primary.expense import Expense
from Primary.project import Project

STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "projects.json")


def proof_to_dict(proof):
    extr_total = None
    if proof.extr_total is not None:
        extr_total = proof.extr_total.cents

    return {"file_path": proof.file_path, "image_hash": proof.image_hash, "ocr_text": proof.ocr_text,
            "extr_total": extr_total, "extr_date": proof.extr_date, "status": proof.status}


def proof_from_dict(data):
    extr_total = None
    if data["extr_total"] is not None:
        extr_total = Money(data["extr_total"])

    return Proof(data["file_path"], data["image_hash"], data["ocr_text"],
                 extr_total, data["extr_date"], data["status"])


def project_to_dict(project):
    members = []
    for member in project.members:
        members.append({"id": member.id, "name": member.name})

    expenses = []
    for expense in project.expenses:
        proof = None
        if expense.proof is not None:
            proof = proof_to_dict(expense.proof)
        expenses.append({"id": expense.id, "amount": expense.amount.cents, "payer_id": expense.payer.id,
                         "date": expense.date, "description": expense.description, "proof": proof})

    return {"id": project.id, "name": project.name, "status": project.status,
            "member_seq": project.member_seq, "expense_seq": project.expense_seq,
            "members": members, "expenses": expenses}


def project_from_dict(data):
    project = Project(data["id"], data["name"], data["status"])
    project.member_seq = data["member_seq"]
    project.expense_seq = data["expense_seq"]

    members_by_id = {}
    for item in data["members"]:
        member = Member(item["id"], item["name"])
        members_by_id[member.id] = member
        project.members.append(member)

    for item in data["expenses"]:
        proof = None
        if item["proof"] is not None:
            proof = proof_from_dict(item["proof"])
        payer = members_by_id[item["payer_id"]]
        project.expenses.append(Expense(item["id"], Money(item["amount"]), payer,
                                        item["date"], item["description"], proof))

    return project


def save_all(projects):
    saved = []
    for project in projects:
        saved.append(project_to_dict(project))

    with open(STORE_PATH, "w") as file:
        json.dump(saved, file, indent=2)


def load_all():
    if not os.path.exists(STORE_PATH):
        return []

    with open(STORE_PATH) as file:
        saved = json.load(file)

    projects = []
    for data in saved:
        projects.append(project_from_dict(data))
    return projects