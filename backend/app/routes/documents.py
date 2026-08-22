from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.document_service import DocumentService
from app.models.category import Category
from app.utils.file_utils import allowed_file
from app.utils.error_handlers import success_response, error_response

documents_bp = Blueprint('documents', __name__)
document_service = DocumentService()


@documents_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload one or more PDF documents."""
    user_id = int(get_jwt_identity())

    if 'files' not in request.files:
        return error_response('No files provided. Use field name "files".', 400)

    files = request.files.getlist('files')
    category_id = request.form.get('category_id', type=int)

    if not files or all(f.filename == '' for f in files):
        return error_response('No files selected.', 400)

    # Validate category if provided
    if category_id is not None:
        category = Category.query.get(category_id)
        if not category:
            return error_response('Invalid category.', 400)

    results = []
    for file in files:
        if file.filename == '':
            continue

        if not allowed_file(file.filename):
            results.append({
                'filename': file.filename,
                'success': False,
                'error': 'Unsupported file format. Allowed formats: PDF, Word (.docx), Text (.txt), Markdown (.md), PowerPoint (.pptx)',
            })
            continue


        try:
            document = document_service.save_and_process(file, user_id, category_id)
            results.append({
                'filename': document.original_filename,
                'success': True,
                'document': document.to_dict(),
            })
        except Exception as e:
            results.append({
                'filename': file.filename,
                'success': False,
                'error': str(e),
            })

    all_success = all(r['success'] for r in results)
    status_code = 201 if all_success else 207  # 207 Multi-Status for partial success

    return success_response(
        data={'results': results},
        message=f'Processed {len(results)} file(s).',
        status_code=status_code,
    )


@documents_bp.route('', methods=['GET'])
@jwt_required()
def list_documents():
    """Get all documents for the authenticated user."""
    user_id = int(get_jwt_identity())
    category_id = request.args.get('category_id', type=int)

    documents = document_service.get_user_documents(user_id, category_id)
    return success_response(data={'documents': documents, 'total': len(documents)})


@documents_bp.route('/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get a single document by ID."""
    user_id = int(get_jwt_identity())
    document = document_service.get_document(document_id, user_id)

    if not document:
        return error_response('Document not found.', 404)

    return success_response(data={'document': document.to_dict()})


@documents_bp.route('/<int:document_id>/status', methods=['GET'])
@jwt_required()
def get_document_status(document_id):
    """Retrieve detailed document processing lifecycle status & progress."""
    user_id = int(get_jwt_identity())
    document = document_service.get_document(document_id, user_id)

    if not document:
        return error_response('Document not found.', 404)

    return success_response(data={
        'document_id': document.id,
        'filename': document.original_filename,
        'status': document.upload_status.upper() if document.upload_status else 'UPLOADED',
        'progress': document.processing_progress or 0,
        'total_chunks': document.total_chunks or 0,
        'error_message': document.error_message
    })


@documents_bp.route('/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    """Delete a document and all associated data."""
    user_id = int(get_jwt_identity())
    deleted = document_service.delete_document(document_id, user_id)

    if not deleted:
        return error_response('Document not found.', 404)

    return success_response(message='Document deleted successfully.')


@documents_bp.route('/<int:document_id>/category', methods=['PATCH'])
@jwt_required()
def update_document_category(document_id):
    """Update the category of a document."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    category_id = data.get('category_id')
    if category_id is not None:
        category = Category.query.get(category_id)
        if not category:
            return error_response('Invalid category.', 400)

    try:
        document = document_service.update_category(document_id, user_id, category_id)
        return success_response(
            data={'document': document.to_dict()},
            message='Category updated successfully.',
        )
    except ValueError as e:
        return error_response(str(e), 404)
