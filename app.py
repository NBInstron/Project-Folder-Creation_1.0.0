from flask import Flask, jsonify
from googleapiclient.errors import HttpError

from config import Config
from logging_config import configure_logging
from routes.webhook import webhook_bp
from services.drive_service import DriveAuthError


def create_app() -> Flask:
    config = Config.from_env()
    configure_logging(config.log_file)

    app = Flask(__name__)
    app.config.from_mapping(APP_CONFIG=config)
    app.register_blueprint(webhook_bp)
    app.logger.info("Registered blueprint: webhook_bp")
    app.logger.debug("Logging initialized. base log file: %s", config.log_file)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(DriveAuthError)
    def handle_drive_auth_error(error: DriveAuthError):
        app.logger.exception("Google Drive authentication failed")
        return jsonify({"status": "error", "message": str(error)}), 500

    @app.errorhandler(HttpError)
    def handle_google_api_error(error: HttpError):
        app.logger.exception("Google Drive API request failed")
        return jsonify({"status": "error", "message": "Google Drive API failure"}), 502

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unhandled application error")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    config = app.config["APP_CONFIG"]
    app.run(host=config.flask_host, port=config.flask_port, debug=config.flask_debug)
