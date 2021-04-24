from flask import Flask, render_template, request, redirect, make_response, \
     jsonify, send_from_directory
from flask_restful import reqparse, abort, Api, Resource

from data import db_session #, jobs_api, user_api
from data.users import User
from data.books import Book
from data.authors import Author

from forms.reg_log_forms import RegisterForm, LoginForm
from forms.book_forms import AddBookForm, SearchBookForm
import os

from flask_login import LoginManager, login_user, current_user, logout_user, \
    login_required

app: Flask = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] =''
api = Api(app)

'''
api.add_resource(user_resource.UserListResource, '/api/v2/user')
api.add_resource(user_resource.UserResource, '/api/v2/user/<int:user_id>')

api.add_resource(jobs_resource.JobsListResource, '/api/v2/jobs')
api.add_resource(jobs_resource.JobsResource, '/api/v2/jobs/<int:jobs_id>')
'''
login_manager = LoginManager()
login_manager.init_app(app)

def main():
    db_session.global_init("db/library.db")
    db_sess = db_session.create_session()
    '''
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    '''
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



@app.route("/")
def index():
    db_sess = db_session.create_session()
    books = db_sess.query(Book).all()
    return render_template("index.html", books=books, current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        print(form.email.data)
        user = User(
            email=form.email.data,
            username=form.username.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form, current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = AddBookForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        book = Book()
        book.title = form.title.data
        book.user_uploaded = current_user.id
        f = request.files['file']
        book_text = f.read()
        new_file = open(f"static/books/{form.author.data} - {form.title.data}.txt", mode="wb")
        new_file.write(book_text)
        new_file.close()
        book.file = f"static/books/{form.author.data} - {form.title.data}.txt"
        a_name = form.author.data
        book.author_name = a_name
        book.user_uploaded_name = current_user.username
        a_exists = 0
        for a in db_sess.query(Author).filter(Author.name == a_name).all():        
            a_exists = 1
            book.author_id = a.id
        if not a_exists:
            author = Author()
            author.name = a_name
            author.books = ""
            db_sess.add(author)
            for a in db_sess.query(Author).filter(Author.name == a_name).all():
                book.author_id = a.id  
        db_sess.add(book)
        for bk in db_sess.query(Book).filter(Book.title == form.title.data).all():
            book_id = bk.id
        for a in db_sess.query(Author).filter(Author.name == a_name).all():
            a.books = ", ".join([i for i in str(a.books).split(", ") + [str(book_id)] if i])     
        
        db_sess.commit()
        return redirect('/')
    return render_template('add_book.html', form=form)


@app.route('/download_book/<path:file>', methods=['GET', 'POST'])
def download_book(file):
    return send_from_directory(app.config['UPLOAD_FOLDER'], file, as_attachment=True)


@app.route('/read_book/<book_id>', methods=['GET'])
@login_required
def read_book(book_id):
    db_sess = db_session.create_session()
    for book in db_sess.query(Book).filter(Book.id == book_id).all():  
        text = open(book.file, mode="r").readlines()
        return render_template('read_book.html', text=text, book=book)
    
    
@app.route('/my_books', methods=['GET'])
@login_required
def my_books():
    db_sess = db_session.create_session()
    results = []
    for book in db_sess.query(Book).filter(Book.user_uploaded == current_user.id).all():  
        results.append(book)
    return render_template('found_books.html', books=results) 
    
    
@app.route('/search_book', methods=['GET', 'POST'])
def search_book():
    form = SearchBookForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        text = form.text.data
        results = []
        for book in db_sess.query(Book).filter((Book.title.like(f"%{text}%")) | 
                                               (Book.author_name.like(f"%{text}%"))).all():        
            results.append(book)
        return render_template('found_books.html', books=results) 
    return render_template('search_book.html', form=form)    


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(401)
def unauthorized(error):
    return redirect("/login")


if __name__ == '__main__':
    main()