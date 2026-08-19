from app.routes.auth import auth_bp
from app.routes.documents import documents_bp
from app.routes.chat import chat_bp
from app.routes.categories import categories_bp
from app.routes.dashboard import dashboard_bp

__all__ = ['auth_bp', 'documents_bp', 'chat_bp', 'categories_bp', 'dashboard_bp']
