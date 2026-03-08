from models import EmployeeProfile

class WorkforceAI:

    def turnover_prediction(self):

        employees = EmployeeProfile.query.all()

        if len(employees) > 50:
            risk = "Moderate"
        else:
            risk = "Low"

        return {
            "employees": len(employees),
            "turnover_risk": risk,
        }