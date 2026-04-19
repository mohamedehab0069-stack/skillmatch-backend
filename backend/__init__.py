from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # config (اختياري)
    app.config["SECRET_KEY"] = "dev"

    # extensions
    CORS(app)

    # routes (blueprints)
    from backend.routes.main import bp as main_bp
    from backend.routes.ai import bp as ai_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(ai_bp)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app