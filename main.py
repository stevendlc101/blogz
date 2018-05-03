from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Blogz123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y327kTcyv&zE5C'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
    def __repr__(self):
        return '<Blog %r>' % self.name

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
    # def __repr__(self):
    #     return '<User %r>' % self.name

@app.before_request
def require_login():
    allowed_routes = ['login', 'index', 'sign_up', 'main_blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect("/login")

@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", users=users)

@app.route("/blog")
def main_blog():
    if(request.args.get('id')):
        id = request.args.get('id')
        blogs = Blog.query.filter_by(id=id)
        return render_template('indiv_blog.html', blogs=blogs)
    if(request.args.get('user')):
        user = request.args.get("user")
        blogs = Blog.query.filter_by(owner_id=user).all()
        return render_template('indiv_blogger.html', blogs=blogs)
    else:    
        blogs = Blog.query.all()
        return render_template('blog.html',  title="All Blog Posts", blogs=blogs)

@app.route("/newpost")
def get_blog_entry():
    return render_template('newpost.html', title="New Blog Post")

@app.route("/newpost", methods=['POST'])
def blog_entry():
    
    owner = User.query.filter_by(username=session['username']).first()
    
    title_error = ""
    body_error = ""

    blog_title = request.form['title']
    blog_body = request.form['body']

    if len(blog_title) == 0:
        title_error = "Please enter a valid blog title."

    if len(blog_body) == 0:
        body_error = "Please enter a valid blog entry."
        
    if not title_error and not body_error:
        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()
        new_id = str(new_blog.id)
        return redirect("/blog?id="+new_id)
        
    else:
        return render_template('newpost.html', title_error=title_error, body_error=body_error, title="New Blog Post")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        username_error = ""
        password_error = ""
        user = User.query.filter_by(username=username).first()

        if not user:
            username_error = "This username does not exist."
            password_error = ""

        if user and user.password != password:
            username_error = ""
            password_error = "Incorrect password. Please try again."

        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect("/newpost")

        else:
            return render_template('login.html', username_error=username_error, password_error=password_error, 
            username=username, password=password)
    else:
        return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['psw']
        reenter = request.form['verify']

        username_error = ""
        password_error = ""
        reenter_error = ""
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            username_error = "An account with that user-name already exists. Please try another."
        
        if len(username) == 0 or len(username) <3 or len(username) >20:
            username_error = "Invalid username. Must be between 3 & 20 characters (no spaces)."
        
        if len(password) == 0 or len(password) <3 or len(password) >20:
            password_error = "Please enter a valid password (between 3 & 20 characters, no spaces)."
            password = ""
            reenter = ""

        if password != reenter:
            reenter_error = "Passwords do not match. Please re-enter."
            password = ""
            reenter = ""

        if not existing_user and not username_error and not password_error and not reenter_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect("/newpost")
        else:
            return render_template('signup.html', username_error=username_error, password_error=password_error, 
            reenter_error= reenter_error, username=username)
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    if session:
        del session['username']
        return redirect('/blog')
    else:
        return redirect("/blog")


if __name__ == '__main__':
    app.run()

