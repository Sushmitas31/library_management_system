from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app import db
from app.models import Book, BorrowRequest, User
from app.schemas import book_schema, borrow_request_schema
import datetime
import csv
import os

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/login', methods=['POST'])
@jwt_required()
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email, password=password).first()
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    additional_claims = {"is_admin": user.is_admin}
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    return jsonify({'access_token': access_token}), 200



@bp.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    return jsonify([book_schema.dump(book) for book in books])

@bp.route('/borrow', methods=['POST'])
@jwt_required()
def borrow_book():
    data = request.json
    user_id = get_jwt_identity()
    book_id = data.get('book_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    if not (user_id and book_id and start_date and end_date):
        return jsonify({'error': 'All fields are required'}), 400
    overlapping_request = BorrowRequest.query.filter(
        BorrowRequest.book_id == book_id,
        BorrowRequest.status == 'Approved',
        BorrowRequest.start_date <= datetime.datetime.strptime(end_date, '%Y-%m-%d').date(),
        BorrowRequest.end_date >= datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    ).first()
    if overlapping_request:
        return jsonify({'error': 'Book is already borrowed for these dates'}), 400
    borrow_request = BorrowRequest(
        user_id=user_id,
        book_id=book_id,
        start_date=datetime.datetime.strptime(start_date, '%Y-%m-%d').date(),
        end_date=datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    )
    db.session.add(borrow_request)
    db.session.commit()
    return borrow_request_schema.jsonify(borrow_request)

@bp.route('/history', methods=['GET'])
@jwt_required()
def view_personal_history():
    user_id = get_jwt_identity()
    history = BorrowRequest.query.filter_by(user_id=user_id).all()
    return jsonify([borrow_request_schema.dump(req) for req in history])

@bp.route('/history/download', methods=['GET'])
@jwt_required()
def download_history():
    user_id = get_jwt_identity()
    history = BorrowRequest.query.filter_by(user_id=user_id).all()
    if not history:
        return jsonify({'error': 'No history found'}), 404
    file_path = os.path.join(os.getcwd(), f'user_{user_id}_history.csv')

    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Book ID', 'Start Date', 'End Date', 'Status'])
        for record in history:
            csvwriter.writerow([record.book_id, record.start_date, record.end_date, record.status])
    return send_file(file_path, as_attachment=True)
