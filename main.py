from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyNewPass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))

    def __init__(self, title, body):
        self.title = title
        self.body = body
    def __repr__(self):
        return '<Blog %r>' % self.name

@app.route("/", methods=['POST', 'GET'])
def index():
    return redirect("/blog")

@app.route("/blog")
def main_blog():
    if(request.args.get('id')):
        id = request.args.get('id')
        blogs = Blog.query.filter_by(id=id)
        return render_template('indiv_blog.html', blogs=blogs)
    else:    
        blogs = Blog.query.all()
        return render_template('blog.html',  title="My Blog Post", blogs=blogs)

@app.route("/newpost")
def get_blog_entry():
    return render_template('newpost.html', title="New Blog Post")

@app.route("/newpost", methods=['POST'])
def blog_entry():
    
    title_error = ""
    body_error = ""

    blog_title = request.form['title']
    blog_body = request.form['body']

    if len(blog_title) == 0:
        title_error = "Please enter a valid blog title."

    if len(blog_body) == 0:
        body_error = "Please enter a valid blog entry."
        
    if not title_error and not body_error:
        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()
        new_id = str(new_blog.id)
        return redirect("/blog?id="+new_id)
        
    else:
        return render_template('newpost.html', title_error=title_error, body_error=body_error, title="New Blog Post")


if __name__ == '__main__':
    app.run()

