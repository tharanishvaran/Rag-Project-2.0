from app.extensions import bcrypt
from app.models.user import User
from app.extensions import db


class AuthService:
    """Handles user authentication — registration and login."""
    
    @staticmethod
    def register_user(name: str, email: str, password: str, role: str = 'student') -> dict:
        """
        Register a new user.
        Returns the new user dict or raises ValueError on validation failure.
        """
        # Check if email already exists
        existing = User.query.filter_by(email=email.lower().strip()).first()
        if existing:
            raise ValueError('A user with this email already exists.')
        
        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user = User(
            name=name.strip(),
            email=email.lower().strip(),
            password_hash=password_hash,
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        
        return user.to_dict()
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> User:
        """
        Authenticate a user by email and password.
        Returns User object if valid, raises ValueError otherwise.
        """
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if not user:
            raise ValueError('Invalid email or password.')
        
        if not bcrypt.check_password_hash(user.password_hash, password):
            raise ValueError('Invalid email or password.')
        
        return user
    
    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """Get a user by ID. Returns None if not found."""
        return User.query.get(user_id)
