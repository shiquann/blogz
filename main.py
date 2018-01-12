from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fdgshkjldfshgksd'

class Blog_post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    post = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    def __init__(self, title, post, owner):
        self.title = title
        self.post = post
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog_post', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.route('/error', methods=['POST', 'GET'])
def error():
    error = 'Both fields need to be filled out'
    return render_template('newpost.html', error=error, title="Add a Blog Entry")

@app.route('/blog', methods=['POST', 'GET'])
def blog(): 
    if request.method == 'GET':
        blogpost = Blog_post.query.all()
        blog_id = request.args.get('id')
        blog_list = Blog_post.query.filter_by(id=blog_id).first()
        return render_template('blog.html', title='Add a Blog Entry', blogpost=blogpost, blog=blog_list )
    blog_title = request.form['blog_title']
    blog_body = request.form['blog_body']
    if len(blog_title) == 0 or len(blog_body) == 0:
        return redirect('/error')  
    
    owner = User.query.filter_by(username=session['username']).first()
       
    new_post = Blog_post(blog_title, blog_body, owner)
    db.session.add(new_post)
    db.session.commit()
    blogpost = Blog_post.query.all()
    blogposts = Blog_post.query.filter_by(owner=owner)
    blog_id = request.args.get('id')
    blog_list = Blog_post.query.filter_by(id=blog_id).first()

    return render_template('blog.html', blog_title=blog_title, blogpost=blogpost, title='Add a Blog Entry', blogposts=blogposts, blog=blog_list)

@app.route('/blogs', methods=['GET', 'POST'])
def blogs():
    ids = int(request.args.get('id', ''))
    blog_posts = Blog_post.query.get(ids)
    new_title = blog_posts.title
    body = blog_posts.post
    blog_id = request.args.get('id')
    blog_list = Blog_post.query.filter_by(id=blog_id).first()
    

    return render_template('entry.html', title=new_title, body=body, blog=blog_list)
    
@app.route('/post', methods=['POST', 'GET'])
def post():
    blog_body = request.form['blog_body']
    blog_title = request.form['blog_title']
    owner = User.query.filter_by(username=session['username']).first()
    username = User.query.first()
    new_post = Blog_post(blog_title, blog_body, owner)

    db.session.add(new_post)
    db.session.commit()
    blog_id = request.args.get('id')
    blog_list = Blog_post.query.filter_by(id=blog_id).first()
    
    

    
    
    return render_template('entry.html', body=blog_body, title=blog_title, blog=blog_list, username=username )

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'user_posts', 'blogs', 'blog','single_user_posts']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_error = "Incorrect password"
        username_error = "username does not exist"
        user = User.query.filter_by(username=username).first()
        if user and user.username == username:
            if user and user.password == password:
                session['username'] = username
                return redirect('/')
            else:
                return render_template('login.html', password_error=password_error)
        else:
            return render_template('login.html', username_error=username_error)

    
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        no_spaces = 'no spaces'
        username_short = 'username to short'
        username_long = 'username to long'
        password_short = 'password to short'
        password_long = 'password to long'
        passwords_not_equal = 'passwords not equal'
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        if " " in username:
            return render_template('register.html', username_error=no_spaces)
        if len(username) < 3:
            return render_template('register.html', username_error=username_short)
        if len(username) > 21:
            return render_template('register.html', username_error=username_long)
        if len(password) < 3:
            return render_template('register.html', password_error=password_short)
        if ' ' in password:
            return render_template('register.html', password_error=no_spaces)
        if len(password) > 21:
            return render_template('register.html', password_error=password_long)
        if password == verify:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/')
            else:
                username_in_use = 'username taken'
                return render_template('register.html', username_error=username_in_use)
        else:
            return render_template('register.html', password_error=passwords_not_equal)

    return render_template('register.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')



@app.route('/blogpost', methods=['GET', 'POST'])
def blog_posts():
    if request.method == 'POST':
        return render_template('/blogs')  
    blog_id = request.args.get('id')
    blog_list = Blog_post.query.filter_by(id=blog_id).first()
    return render_template('newpost.html', title='Add a Blog Entry', blog=blog_list  )

@app.route('/userposts', methods=['GET'])
def user_posts():
    user_id = request.args.get('id', '')
    posts = db.session.query(Blog_post).filter_by(owner_id=user_id).all()
    blog_id = request.args.get('id')
    blog_list = Blog_post.query.filter_by(id=blog_id).first()
    return render_template('allblogs.html', posts=posts, blog=blog_list)

@app.route('/singleuserpost', methods=['GET'])
def single_user_posts():
    blog_id = request.args.get('id')
    blog_list = Blog_post.query.filter_by(id=blog_id).first()
    return render_template('single.html', blog=blog_list)


@app.route('/', methods=['POST', 'GET'])
def index():
    username = User.query.all()
    return render_template('index.html', username=username)
if __name__ == '__main__':
    app.run()