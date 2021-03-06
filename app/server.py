from flask import Flask, send_file, send_from_directory
from resources.magic_castle_api import MagicCastleAPI
from resources.progress_api import ProgressAPI
from resources.available_resources_api import AvailableResourcesApi
from resources.user_api import UserAPI
from flask_cors import CORS
from models.cloud.openstack_manager import OpenStackManager
from database.schema_manager import SchemaManager
from database.database_manager import DatabaseManager

# Exit with an error if the clouds.yaml is not found or the OpenStack API can't be reached
OpenStackManager.test_connection()

# Update the database schema to the latest version
with DatabaseManager.connect() as database_connection:
    SchemaManager(database_connection).update_schema()

app = Flask(__name__)

# Allows all origins on all routes (not safe for production)
CORS(app)

magic_castle_view = MagicCastleAPI.as_view("magic_castle")
app.add_url_rule(
    "/api/magic-castles",
    view_func=magic_castle_view,
    defaults={"hostname": None},
    methods=["HEAD", "GET", "POST"],
)
app.add_url_rule(
    "/api/magic-castles/<string:hostname>",
    view_func=magic_castle_view,
    methods=["GET", "DELETE", "PUT"],
)
app.add_url_rule(
    "/api/magic-castles/<string:hostname>/apply",
    view_func=magic_castle_view,
    defaults={"apply": True},
    methods=["POST"],
)

progress_view = ProgressAPI.as_view("progress")
app.add_url_rule(
    "/api/magic-castles/<string:hostname>/status",
    view_func=progress_view,
    methods=["GET"],
)

available_resources_view = AvailableResourcesApi.as_view("available_resources")
app.add_url_rule(
    "/api/available-resources",
    view_func=available_resources_view,
    defaults={"hostname": None},
    methods=["GET"],
)
app.add_url_rule(
    "/api/available-resources/<string:hostname>",
    view_func=available_resources_view,
    methods=["GET"],
)

user_view = UserAPI.as_view("user")
app.add_url_rule("/api/users/me", view_func=user_view, methods=["GET"])


@app.route("/css/<path:path>")
def send_css_file(path):
    return send_from_directory("../dist/css", path)


@app.route("/js/<path:path>")
def send_js_file(path):
    return send_from_directory("../dist/js", path)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    # Single page application
    response = send_file("../dist/index.html")

    # Avoid caching SPA to avoid showing the page when the user is logged out
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
