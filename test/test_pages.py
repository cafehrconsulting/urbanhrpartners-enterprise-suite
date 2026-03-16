import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_app():
    """
    Supports either:
    - create_app()
    - create_app(testing=True)
    - app object
    """
    import app as app_module

    flask_app = None

    if hasattr(app_module, "create_app"):
        try:
            flask_app = app_module.create_app(testing=True)
        except TypeError:
            flask_app = app_module.create_app()
    elif hasattr(app_module, "app"):
        flask_app = app_module.app
    else:
        raise RuntimeError(
            "Could not find Flask application. Expected either `create_app()` or `app` in app.py"
        )

    return flask_app


class UrbanHRPartnersPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = load_app()

        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False

        if "SQLALCHEMY_DATABASE_URI" in cls.app.config:
            cls.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

        cls.client = cls.app.test_client()

    def assert_route_safe(self, route: str):
        """
        We accept:
        - 200 OK
        - 302 redirect (common if login/auth is enabled)
        - 301 redirect
        - 401 unauthorized
        - 403 forbidden

        We fail on:
        - 500 internal server error
        - 404 missing route
        """
        response = self.client.get(route, follow_redirects=False)

        allowed = {200, 301, 302, 401, 403}
        self.assertIn(
            response.status_code,
            allowed,
            msg=f"Route {route} returned unexpected status {response.status_code}",
        )

    def test_home_page(self):
        self.assert_route_safe("/")

    def test_dashboard_page(self):
        self.assert_route_safe("/dashboard")

    def test_crm_page(self):
        self.assert_route_safe("/crm")

    def test_hris_page(self):
        self.assert_route_safe("/hris")

    def test_ats_page(self):
        self.assert_route_safe("/ats")

    def test_orientation_page(self):
        self.assert_route_safe("/orientation")

    def test_sgsst_page(self):
        self.assert_route_safe("/sgsst")

    def test_inventory_page(self):
        self.assert_route_safe("/inventory")

    def test_finance_page(self):
        self.assert_route_safe("/finance")

    def test_marketing_page(self):
        self.assert_route_safe("/marketing")

    def test_calendar_page(self):
        self.assert_route_safe("/calendar")

    def test_reports_analytics_page(self):
        self.assert_route_safe("/reports-analytics")

    def test_xiomy_page(self):
        self.assert_route_safe("/xiomy-page")


if __name__ == "__main__":
    unittest.main()
