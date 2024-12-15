from app import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures database tables are created within the app context
    app.run(debug=True)
