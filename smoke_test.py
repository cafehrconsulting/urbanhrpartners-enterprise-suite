import sys
import traceback
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_app():
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
            "Could not find Flask app. Expected `create_app()` or `app` in app.py"
        )

    return flask_app


def main():
    try:
        app = load_app()
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False

        if "SQLALCHEMY_DATABASE_URI" in app.config:
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

        client = app.test_client()

        routes = [
            "/",
            "/dashboard",
            "/crm",
            "/hris",
            "/ats",
            "/orientation",
            "/sgsst",
            "/inventory",
            "/finance",
            "/marketing",
            "/calendar",
            "/reports-analytics",
            "/xiomy-page",
        ]

        print("=" * 80)
        print("UrbanHRPartners Enterprise Suite - Smoke Test")
        print("=" * 80)

        failures = []

        for route in routes:
            try:
                response = client.get(route, follow_redirects=False)
                status = response.status_code
                ok = status in {200, 301, 302, 401, 403}

                print(f"{route:<22} -> {status}")

                if not ok:
                    failures.append((route, status))
            except Exception as exc:
                failures.append((route, str(exc)))
                print(f"{route:<22} -> ERROR: {exc}")
                print("-" * 80)
                traceback.print_exc()
                print("-" * 80)
                break

        print("\n" + "=" * 80)

        if failures:
            print("FAILED ROUTES:")
            for route, problem in failures:
                print(f" - {route}: {problem}")
            print("=" * 80)
            raise SystemExit(1)

        print("ALL ROUTES PASSED BASIC SMOKE TEST")
        print("=" * 80)

    except Exception:
        print("\nFULL STARTUP TRACEBACK")
        print("=" * 80)
        traceback.print_exc()
        print("=" * 80)
        raise


if __name__ == "__main__":
    main()
