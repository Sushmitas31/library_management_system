
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models import User, BorrowRequest, Book
from app.schemas import user_schema, borrow_request_schema, book_schema

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin privileges required"}), 403

@bp.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin', False)  # Default to False if not provided

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Check if the email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400
    
    new_user = User(email=email, password=password, is_admin=is_admin)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201


@bp.route('/create_book', methods=['POST'])
@jwt_required()
def create_book():
    data = request.json
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    new_book = Book(title=title)
    db.session.add(new_book)
    db.session.commit()
    return book_schema.jsonify(new_book)


@bp.route('/borrow_requests', methods=['GET'])
@jwt_required()
def view_borrow_requests():
    requests = BorrowRequest.query.all()
    return jsonify([borrow_request_schema.dump(req) for req in requests])

@bp.route('/borrow_requests/<int:request_id>', methods=['PATCH'])
@jwt_required()
def approve_or_deny_request(request_id):
    data = request.json
    status = data.get('status')
    if status not in ['Approved', 'Denied']:
        return jsonify({'error': 'Invalid status'}), 400
    borrow_request = BorrowRequest.query.get(request_id)
    if not borrow_request:
        return jsonify({'error': 'Request not found'}), 404
    borrow_request.status = status
    db.session.commit()
    return borrow_request_schema.jsonify(borrow_request)
