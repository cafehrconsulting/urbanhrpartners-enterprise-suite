from models import FinanceEntry

class FinanceAI:

    def revenue_trend(self):

        entries = FinanceEntry.query.all()

        revenue = sum(
            e.amount for e in entries
            if e.entry_type == "Revenue"
        )

        expenses = sum(
            e.amount for e in entries
            if e.entry_type == "Expense"
        )

        return {
            "revenue": revenue,
            "expenses": expenses,
            "profit": revenue - expenses,
        }