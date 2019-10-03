from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:temppass@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(500))
    # completed = db.Column(db.Boolean, default=False)

    def __init__(self, title, content):
        self.title = title
        self.content = content

@app.route('/blog')
def blog():
    blog_posts = Blog.query.all()
    return render_template('blog.html',blog_posts=blog_posts)

@app.route('/detail')
def detail_view():
    id = int(request.args.get('id'))
    post = Blog.query.filter_by(id=id).first()
    return render_template('detail.html',post=post)

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
            newpost = Blog(title, content)
            db.session.add(newpost)
            db.session.flush()
            new_id = newpost.id
            db.session.commit()
            return redirect(f'/detail?id={new_id}')
        else:     
            return render_template('newpost.html',title=title,content=content, title_error=title_error,content_error=content_error)
    return render_template('newpost.html')
if __name__ == '__main__':
    app.run()