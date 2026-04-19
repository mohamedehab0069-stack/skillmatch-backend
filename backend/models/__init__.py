from flask import Flask
from flask_cors import CORS
def create_app():
    print("🔥 CREATE_APP STARTED (CONFIRMED)")

    app = Flask(__name__)
    CORS(app)

    return app

def create_app():
    print("🔥 CREATE_APP STARTED")

    app = Flask(__name__)
    CORS(app)

    # ── Blueprints ──
    from backend.routes.main import bp as main_bp
    from backend.routes.ai import bp as ai_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(ai_bp)

    # ── Health check ──
    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app