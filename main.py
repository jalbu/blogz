from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import pdb

'''
Blogs Project for LC101
Created By James Albu
'''

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:temppass@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "#someSecretString"
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User',backref='owner_posts', foreign_keys=[owner_id])

    def __init__(self, title, content, owner_id):
        self.title = title
        self.content = content
        self.owner_id = owner_id
        

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(64))
    email = db.Column(db.String(30))
    
    def __init__(self, username, password,email):
        self.username = username
        self.password = password
        self.email = email

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog','index','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog')
def blog():
    init_blog_posts = Blog.query.all()
    blog_posts = [
        {'post':post, 'user': User.query.filter_by(id=post.owner_id).first().username}
        for post in init_blog_posts
    ]
    return render_template('blog.html',blog_posts=blog_posts)

@app.route('/detail')
def detail_view():
    # For single blog page
    post_id = request.args.get('id')
    # For all user blogs
    user = request.args.get('user')
    # For rendering single blog posts
    if post_id:
        post = Blog.query.filter_by(id=post_id).first()
        username = User.query.filter_by(id=post.owner_id).first().username
        return render_template('detail.html',post=post,username=username)
    # For rendering all blog posts of a user
    elif user:
        user_post_list = Blog.query.filter_by(owner_id=user).all()
        # pdb.set_trace()
        user = User.query.filter_by(id=user).first()
        return render_template('detail.html',user_post_list=user_post_list,user=user)
    

def validate_user_input(test_string):
    if len(test_string) == 0:
        return "Field must not be empty"
    if len(test_string) > 30:
        return "Text must not be longer than 30 characters"
    else:
        return ""

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_error = ""
        pass_error = ""
        
        user_error = validate_user_input(username)
        pass_error = validate_user_input(password)
        # Validate user input
        active_user = User.query.filter_by(username=username).first()
        if active_user:
            if password == active_user.password:
                session['username'] = active_user.username
                return redirect('/blog')
            else:
                pass_error = 'Username and Password do not match'
        else:
            user_error = 'Username does not exist'
        if user_error != "" or pass_error != "":
            # Incorrect output
            return render_template('login.html', username=username,password=password,user_error=user_error,pass_error=pass_error)

    return render_template('login.html')

@app.route("/signup", methods=['post','get'])
def signup():
    # If string is a valid string, then return true, else false
    def validate_string(field,val_string):
        error = ''
        if val_string == '':
            error = field + 'cannot be empty'
        elif ' ' in val_string:
            error = field + 'must not contain spaces.'
        elif len(val_string) < 3 or len(val_string) > 20:
            error = field + 'must be between 3 and 20 characters'
        return error
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_pass = request.form['verify_pass']
        email = request.form['email']
        user_error = ''
        pass_error = ''
        verify_pass_error = ''
        email_error = ''
        # See if fields are empty, have spaces, or not the right length
        user_error = validate_string('Username ', username)
        pass_error = validate_string('Password ', password)
        verify_pass_error = validate_string('Validate Password ', verify_pass)
        if len(email) > 0:
            email_error = validate_string('Email ',email)
            if (email.count('@') != 1 or email.count(".") != 1):
                email_error = "Email must contain one '@' and one '.'"
        
        if password != verify_pass:
            verify_pass_error = "Passwords do not match"
            password = ""
            verify_pass = ""

        # Clear passwords if password or verify pass has an error
        if pass_error != '' or verify_pass_error != '':
            password = ""
            verify_pass = ""
        if user_error == '' and pass_error == '' and verify_pass_error == '' and email_error == '':
            # Fill this in
            new_user = User(username,password, email)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog')
        else:
            return render_template('signup.html', 
            username=username,
            password=password,
            verify_pass=verify_pass,
            email=email,
            user_error=user_error,
            pass_error=pass_error,
            verify_pass_error=verify_pass_error,
            email_error=email_error)
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/newpost',methods=['GET','POST'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        title_error = ''
        content_error = ''
    # Validate login
        if len(title) == 0 or len(title) > 120:
            title_error = 'Length of title must not be blank or greater than 120 characters'
            title = ''
        if len(content) == 0 or len(content) > 500:
            content_error = 'Length of content must not be blank or greater than 500 characters'
            content = ''
        if title_error == '' and content_error == '':
            newpost = Blog(
                title, content, User.query.filter_by(username=session['username']).first().id
                )
            db.session.add(newpost)
            db.session.flush()
            new_id = newpost.id
            db.session.commit()
            return redirect(f'/detail?id={new_id}')
        else:     
            return render_template('newpost.html',title=title,content=content, title_error=title_error,content_error=content_error)
    return render_template('newpost.html')

@app.route('/')
def index():
    user_list = User.query.all()
    return render_template('index.html',user_list=user_list)

if __name__ == '__main__':
    app.run()