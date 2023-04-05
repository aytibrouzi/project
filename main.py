from flask import Flask, render_template, request, redirect, flash
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import csv
import re
import os
from dbcon import Users, Post, Like, db
from functions import textlen

UPLOAD_FOLDER = 'C:\\Users\\user\\Desktop\\try\\static\\uploads\\'

app = Flask(__name__, static_url_path = "/static", static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
app.secret_key = os.urandom(24)

@login_manager.user_loader
def load_user(user_id):
    return Users.select().where(Users.id==int(user_id)).first()

@app.before_request
def before_request():
    db.connect()
    
@app.after_request
def after_request(response):
    db.close()
    return response    

@app.route('/')
def head():
    all_posts = Post.select()
    return render_template('head.html', posts=all_posts)

# @app.route('/veiw/')

@app.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        # if request.files:
        title = request.form['title']
        description = request.form['description']
        photo = request.files['file']
        
        filename = secure_filename(photo.filename)
        
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        print('before')
        Post.create(
            title=title,
            author=current_user,
            description=description,
            filename=filename
        )
        print('created succesfull')
        return redirect ('/')
    return render_template('create.html')

@app.route('/<int:id>/')
def retrive_post(id):
    post = Post.select().where(Post.id==id).first()
    if post:
        return render_template('post.html', post=post)
    return f'Post with id = {id} does not exist'

@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/<int:id>/update/', methods = ('GET', "POST"))
def update(id):
    post = Post.select().where(Post.id==id).first()
    if post.author == current_user:
        if request.method == 'POST':
            if post:
                title = request.form['title']
                description = request.form['description']
                file = request.form['file']
                obj = Post.update({
                    Post.title: title,
                    Post.file: file,
                    Post.description:description
                }).where(Post.id==id)
                obj.execute()
                return redirect(f'/{id}/')
            return f'Post with id = {id} does not exist'
        return render_template('update.html', post=post)


@app.route('/<int:id>/delete/', methods=('GET', 'POST'))
def delete(id):
    post = Post.select().where(Post.id==id).first()
    if post.author == current_user:
        if request.method == 'POST':
            if post:
                post.delete_instance()
                return redirect(f'/')
            return f'Post with id = {id} does not exist'
        return render_template('delete.html', post=post)

@app.route('/register/', methods = ['GET', 'POST'])
@login_required
def lenth():
    if request.method=='POST':
        n = request.form['text']

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    if request.method=='POST':
        email = request.form['email'] 
        name = request.form['name']  
        password = request.form['password']
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
        user = Users.select().where(Users.email==email).first()
        if user:
            flash('Email address already exists')
            return redirect('/register/')
        else:
            t1 = len(email)
            t2 = len(name)
            t4 = len(password)
            if t4 < 8:
                p4 = 'your password should contain more than 8 sym'
            elif re.match(pattern, password) is None:
                p4 = 'your password should contain digits and latters in Upper and Lower register'
            elif t1 > 0 and t2 > 0 and t4 >= 8:
                Users.create(
                    email=email,
                    name=name,
                    password = generate_password_hash(password, method = 'sha256')
                )
                return redirect('/login/')
            return render_template('register.html', f4=p4)
    return render_template('register.html')


@app.route('/login/', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Users.select().where(Users.email==email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect('/login/')
        else: 
            login_user(user)
            return redirect('/profile/')
    
    return render_template('login.html')

@app.route('/profile/', methods = ['GET','POST'])
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user)

@app.route('/profile/<int:id>/')
@login_required
def anyprof(id):
    user = Users.select().where(Users.id==id).first()
    posts = Post.select().where(Post.author_id==id)
    return render_template('profile.html', user = user, posts=posts)

@app.route('/current_profile/')
@login_required
def current_profile():
    posts = Post.select().where(Post.author_id==current_user.id)
    return render_template('profile.html', user=current_user, posts=posts)

@app.route('/logout/', methods = ['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect('/register/')

if __name__ == '__main__':
    app.run(debug=True)
