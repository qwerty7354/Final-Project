from ext import app, db
from flask import render_template, redirect, flash, request
from forms import RegisterForm, BookForm, LoginForm, RatingForm, CommentForm
from models import Book, Rating, User, Comment
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from os import path


@app.route("/")
def home():
    q = request.args.get("q", "").strip()
    if q:
        books = Book.query.filter(Book.title.ilike(f"%{q}%")).all()
    else:
        books = Book.query.all()
    return render_template("index.html", books=books, q=q)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_pw)
        new_user.create()
        flash("წარმატებით დარეგისტრირდი!")
        return redirect("/")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("წარმატებით შეხვედი საიტზე!")
            return redirect("/")
        flash("მომხმარებლის სახელი ან პაროლი არასწორია.")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            year=form.year.data,
            genre=form.genre.data,
            description=form.description.data,
        )
        img = form.image.data
        if img and img.filename:
            new_book.image = img.filename
            img.save(path.join(app.root_path, "static", "images", img.filename))
        new_book.create()
        flash("წარმატებით დაემატა წიგნი!")
        return redirect("/")
    return render_template("add_book.html", form=form, title="Add Book")


@app.route("/update_book/<int:book_id>", methods=["GET", "POST"])
@login_required
def update_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash("წიგნი ვერ მოიძებნა.")
        return redirect("/")
    form = BookForm(title=book.title, author=book.author,
                    year=book.year, genre=book.genre, description=book.description)
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.year = form.year.data
        book.genre = form.genre.data
        book.description = form.description.data
        img = form.image.data
        if img and img.filename:
            img.save(path.join(app.root_path, "static", "images", img.filename))
            book.image = img.filename
        book.save()
        flash("წიგნი განახლდა!")
        return redirect("/")
    return render_template("add_book.html", form=form, title="Update Book")


@app.route("/delete_book/<int:book_id>")
@login_required
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash("წიგნი ვერ მოიძებნა.")
        return redirect("/")
    book.delete()
    flash("წიგნი წაიშალა.")
    return redirect("/")


@app.route("/book/<int:book_id>", methods=["GET", "POST"])
def view_book_details(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash("წიგნი ვერ მოიძებნა.")
        return redirect("/")
    ratings = Rating.query.filter_by(book_id=book_id).all()
    comments = Comment.query.filter_by(book_id=book_id).order_by(Comment.created_at.desc()).all()
    avg = round(sum(r.score for r in ratings) / len(ratings), 1) if ratings else None
    rating_form = RatingForm()
    comment_form = CommentForm()
    user_rating = None
    user_has_rated = False
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(book_id=book_id, user_id=current_user.id).first()
        user_has_rated = user_rating is not None
    return render_template("book_details.html",
                           book=book, ratings=ratings, avg=avg,
                           rating_form=rating_form, comment_form=comment_form,
                           comments=comments,
                           user_has_rated=user_has_rated, user_rating=user_rating)


@app.route("/add_rating/<int:book_id>", methods=["POST"])
@login_required
def add_rating(book_id):
    form = RatingForm()
    if form.validate_on_submit():
        existing = Rating.query.filter_by(book_id=book_id, user_id=current_user.id).first()
        if existing:
            flash("ამ წიგნს უკვე დაუსვი შეფასება.")
        else:
            Rating(score=form.score.data, book_id=book_id, user_id=current_user.id).create()
            flash("შეფასება დაემატა!")
    return redirect(f"/book/{book_id}")


@app.route("/edit_rating/<int:rating_id>", methods=["GET", "POST"])
@login_required
def edit_rating(rating_id):
    rating = db.session.get(Rating, rating_id)
    if not rating or rating.user_id != current_user.id:
        flash("ეს შეფასება შენი არ არის.")
        return redirect("/")
    form = RatingForm(score=rating.score)
    if form.validate_on_submit():
        rating.score = form.score.data
        rating.save()
        flash("შეფასება განახლდა!")
        return redirect(f"/book/{rating.book_id}")
    return render_template("edit_rating.html", form=form, rating=rating)


@app.route("/delete_rating/<int:rating_id>")
@login_required
def delete_rating(rating_id):
    rating = db.session.get(Rating, rating_id)
    if not rating or rating.user_id != current_user.id:
        flash("ეს შეფასება შენი არ არის.")
        return redirect("/")
    book_id = rating.book_id
    rating.delete()
    flash("შეფასება წაიშალა.")
    return redirect(f"/book/{book_id}")


@app.route("/add_comment/<int:book_id>", methods=["POST"])
@login_required
def add_comment(book_id):
    form = CommentForm()
    if form.validate_on_submit():
        Comment(text=form.text.data, book_id=book_id, user_id=current_user.id).create()
        flash("კომენტარი დაემატა!")
    return redirect(f"/book/{book_id}")


@app.route("/delete_comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
    if not comment or comment.user_id != current_user.id:
        flash("ეს კომენტარი შენი არ არის.")
        return redirect("/")
    book_id = comment.book_id
    comment.delete()
    flash("კომენტარი წაიშალა.")
    return redirect(f"/book/{book_id}")


@app.route("/popular")
def popular():
    books = Book.query.all()
    book_stats = []
    for book in books:
        ratings = Rating.query.filter_by(book_id=book.id).all()
        avg = round(sum(r.score for r in ratings) / len(ratings), 1) if ratings else 0
        book_stats.append({"book": book, "avg": avg, "count": len(ratings)})
    book_stats.sort(key=lambda x: (x["avg"], x["count"]), reverse=True)
    return render_template("popular.html", book_stats=book_stats)


@app.route("/profile")
@login_required
def profile():
    ratings = Rating.query.filter_by(user_id=current_user.id).all()
    comments = Comment.query.filter_by(user_id=current_user.id).order_by(Comment.created_at.desc()).all()
    return render_template("profile.html", ratings=ratings, comments=comments)


@app.route("/about")
def about():
    return render_template("about.html")
