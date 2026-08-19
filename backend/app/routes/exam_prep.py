from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.exam_prep_service import ExamPrepService

exam_prep_bp = Blueprint('exam_prep', __name__)
exam_prep_service = ExamPrepService()


@exam_prep_bp.route('/strategy', methods=['POST'])
@jwt_required()
def generate_strategy():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    subject = data.get('subject', 'General Subject')
    unit = data.get('unit', '')
    exam_type = data.get('exam_type', 'Semester Exam')
    days_remaining = int(data.get('days_remaining', 7))
    category_id = data.get('category_id')

    try:
        strategy = exam_prep_service.generate_strategy(
            user_id=user_id,
            subject=subject,
            unit=unit,
            exam_type=exam_type,
            days_remaining=days_remaining,
            category_id=category_id
        )
        return jsonify({'success': True, 'data': {'strategy': strategy}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@exam_prep_bp.route('/study-plan', methods=['POST'])
@jwt_required()
def generate_study_plan():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    subject = data.get('subject', 'General Subject')
    days_remaining = int(data.get('days_remaining', 15))
    category_id = data.get('category_id')

    try:
        plan = exam_prep_service.generate_study_plan(
            user_id=user_id,
            subject=subject,
            days_remaining=days_remaining,
            category_id=category_id
        )
        return jsonify({'success': True, 'data': plan})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@exam_prep_bp.route('/important-topics', methods=['POST'])
@jwt_required()
def detect_important_topics():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    subject = data.get('subject', 'General Subject')
    category_id = data.get('category_id')

    try:
        topics = exam_prep_service.detect_important_topics(
            user_id=user_id,
            subject=subject,
            category_id=category_id
        )
        return jsonify({'success': True, 'data': topics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@exam_prep_bp.route('/paper-analysis', methods=['POST'])
@jwt_required()
def analyze_previous_papers():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    subject = data.get('subject', 'General Subject')
    category_id = data.get('category_id')

    try:
        analysis = exam_prep_service.analyze_previous_papers(
            user_id=user_id,
            subject=subject,
            category_id=category_id
        )
        return jsonify({'success': True, 'data': {'analysis': analysis}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@exam_prep_bp.route('/expected-questions', methods=['POST'])
@jwt_required()
def generate_expected_questions():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    subject = data.get('subject', 'General Subject')
    category_id = data.get('category_id')

    try:
        expected = exam_prep_service.generate_expected_questions(
            user_id=user_id,
            subject=subject,
            category_id=category_id
        )
        return jsonify({'success': True, 'data': {'expected_questions': expected}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
