import os
import logging
from flask import Flask

from app.config import get_config
from app.extensions import db, jwt, cors, bcrypt
from app.utils.error_handlers import register_error_handlers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)


def create_app():
    """Flask application factory."""
    app = Flask(__name__)

    # Load configuration
    config = get_config()
    app.config.from_object(config)

    # Ensure upload and chroma folders exist (resolve relative paths to absolute)
    _backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for folder_key in ('UPLOAD_FOLDER', 'CHROMA_PERSIST_DIRECTORY'):
        folder = app.config.get(folder_key, '')
        if folder and not os.path.isabs(folder):
            app.config[folder_key] = os.path.normpath(os.path.join(_backend_root, folder))
        os.makedirs(app.config[folder_key], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r'/api/*': {'origins': '*'}})

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.documents import documents_bp
    from app.routes.chat import chat_bp
    from app.routes.categories import categories_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.exam_prep import exam_prep_bp
    from app.routes.quiz import quiz_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(exam_prep_bp, url_prefix='/api/exam-prep')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')


    # Register global error handlers
    register_error_handlers(app)

    # Create tables, run migrations, and seed default data
    try:
        with app.app_context():
            db.create_all()
            _migrate_db()
            _seed_categories()
    except Exception as e:
        logging.getLogger(__name__).warning(f"Database initialization warning: {e}")

    return app



def _migrate_db():
    """Ensure missing columns like avatar_url are added to MySQL tables."""
    from sqlalchemy import text
    try:
        db.session.execute(text("ALTER TABLE users ADD COLUMN avatar_url LONGTEXT NULL;"))
        db.session.commit()
        logging.getLogger(__name__).info("Migrated: Added avatar_url column to users table.")
    except Exception:
        db.session.rollback()



def _seed_categories():
    """Seed default categories if they don't exist yet."""
    from app.models.category import Category, DEFAULT_CATEGORIES

    if Category.query.count() == 0:
        for cat_data in DEFAULT_CATEGORIES:
            category = Category(
                name=cat_data['name'],
                description=cat_data['description'],
            )
            db.session.add(category)
        db.session.commit()
        logging.getLogger(__name__).info('Default categories seeded.')
