from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.category import Category, DEFAULT_CATEGORIES
from app.extensions import db
from app.utils.error_handlers import success_response, error_response

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('', methods=['GET'])
@jwt_required()
def get_categories():
    """Return all available categories."""
    categories = Category.query.order_by(Category.name).all()
    return success_response(data={'categories': [c.to_dict() for c in categories]})


@categories_bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new category."""
    data = request.get_json()
    if not data:
        return error_response('Request body is required.', 400)

    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if not name:
        return error_response('Category name is required.', 400)
    if len(name) > 100:
        return error_response('Category name must be 100 characters or less.', 400)

    existing = Category.query.filter_by(name=name).first()
    if existing:
        return error_response('A category with this name already exists.', 409)

    category = Category(name=name, description=description or None)
    db.session.add(category)
    db.session.commit()

    return success_response(
        data={'category': category.to_dict()},
        message='Category created successfully.',
        status_code=201,
    )


@categories_bp.route('/<int:category_id>', methods=['PATCH'])
@jwt_required()
def update_category(category_id):
    """Update a category name or description."""
    category = Category.query.get(category_id)
    if not category:
        return error_response('Category not found.', 404)

    data = request.get_json() or {}
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return error_response('Category name cannot be empty.', 400)
        existing = Category.query.filter(Category.name == name, Category.id != category_id).first()
        if existing:
            return error_response('A category with this name already exists.', 409)
        category.name = name
    if 'description' in data:
        category.description = data['description'].strip() or None

    db.session.commit()
    return success_response(data={'category': category.to_dict()}, message='Category updated.')


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Delete a category (documents will have category set to null)."""
    category = Category.query.get(category_id)
    if not category:
        return error_response('Category not found.', 404)

    db.session.delete(category)
    db.session.commit()
    return success_response(message='Category deleted successfully.')
