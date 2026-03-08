from models import EmployeeProfile, Client, FinanceEntry

class AnalyticsEngine:

    def __init__(self, db):
        self.db = db

    def workforce_metrics(self):

        employees = EmployeeProfile.query.all()

        departments = {}
        for e in employees:
            dept = e.department or "Unassigned"
            departments[dept] = departments.get(dept, 0) + 1

        return {
            "employee_total": len(employees),
            "departments": departments,
        }

    def crm_metrics(self):

        clients = Client.query.count()

        return {
            "client_total": clients
        }

    def finance_metrics(self):

        revenue = (
            self.db.session.query(self.db.func.sum(FinanceEntry.amount))
            .filter(FinanceEntry.entry_type == "Revenue")
            .scalar() or 0
        )

        expenses = (
            self.db.session.query(self.db.func.sum(FinanceEntry.amount))
            .filter(FinanceEntry.entry_type == "Expense")
            .scalar() or 0
        )

        return {
            "revenue": revenue,
            "expenses": expenses,
            "profit": revenue - expenses,
        }