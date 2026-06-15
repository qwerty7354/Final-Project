from ext import app, db
from models import User, Book
from werkzeug.security import generate_password_hash


def init_db():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                password=generate_password_hash("admin123"),
                role="Admin"
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin created — username: admin | password: admin123")

        if Book.query.count() == 0:
            default_books = [
                Book(
                    title="The Great Gatsby",
                    author="F. Scott Fitzgerald",
                    year=1925,
                    genre="Fiction",
                    image="book1.png",
                    description="A story of wealth, obsession and the American Dream set in the roaring 1920s."
                ),
                Book(
                    title="1984",
                    author="George Orwell",
                    year=1949,
                    genre="Science Fiction",
                    image="book2.png",
                    description="A dystopian novel about a totalitarian society ruled by Big Brother."
                ),
                Book(
                    title="To Kill a Mockingbird",
                    author="Harper Lee",
                    year=1960,
                    genre="Fiction",
                    image="book3.png",
                    description="A powerful story of racial injustice and moral growth in the American South."
                ),
            ]
            for book in default_books:
                db.session.add(book)
            db.session.commit()
            print("3 default books added.")

        print("Database initialized.")


if __name__ == "__main__":
    init_db()
