from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fdgshkjldfshgksd'

class Blog_post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    post = db.Column(db.String(500))
 

    def __init__(self, title, post):
        self.title = title
        self.post = post

@app.route('/error', methods=['POST', 'GET'])
def error():
    error = 'Both fields need to be filled out'
    return render_template('newpost.html', error=error, title="Add a Blog Entry")

@app.route('/blog', methods=['POST', 'GET'])
def blog(): 
    if request.method == 'GET':
        blogpost = Blog_post.query.all()
        return render_template('blog.html', title='Add a Blog Entry', blogpost=blogpost)
    blog_title = request.form['blog_title']
    blog_body = request.form['blog_body']
    if len(blog_title) == 0 or len(blog_body) == 0:
        return redirect('/error')         
    new_post = Blog_post(blog_title, blog_body)
    db.session.add(new_post)
    db.session.commit()
    blogpost = Blog_post.query.all()
    return render_template('blog.html', blog_title=blog_title, blogpost=blogpost, title='Add a Blog Entry')

@app.route('/blogs', methods=['GET', 'POST'])
def blogs():
    ids = int(request.args.get('id', ''))
    blog_posts = Blog_post.query.get(ids)
    new_title = blog_posts.title
    body = blog_posts.post

    
    
    return render_template('entry.html', title=new_title, body=body)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect('/blog')  

    return render_template('newpost.html', title='Add a Blog Entry'  )




if __name__ == '__main__':
    app.run()