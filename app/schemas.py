from app import ma
from app.models import User, Book, BorrowRequest

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book

class BorrowRequestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BorrowRequest

user_schema = UserSchema()
book_schema = BookSchema()
borrow_request_schema = BorrowRequestSchema()