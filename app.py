from flask import Flask, render_template, request, redirect, url_for , flash
from flask_sqlalchemy import SQLAlchemy  
from flask_moment import Moment
from flask_login import UserMixin,LoginManager, login_user, current_user, logout_user, login_required
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key='super super secret key'

moment = Moment(app)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



# Define models user

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    email = db.Column(db.String(255), nullable = False , unique = True)
    password = db.Column(db.String(300), nullable = False) 
    username = db.Column(db.String(100), nullable = True)
    userrole = db.Column(db.String(100), default = "User")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable = False)
    body = db.Column(db.String, nullable = False)
    author = db.Column(db.String(40), nullable = False)
    created_at = db.Column(db.DateTime, server_default=db.func.now()) 
    edited_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate= db.func.now() )

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

@app.route('/', methods= ['GET'])
def root():
    return render_template("home.html")

@app.route('/about', methods= ['GET'])
def about():
    return render_template("about.html")

@app.route('/profile', methods= ['GET', 'POST'])
@login_required 
def profile_edit():
    
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    
    if request.method == "POST": 
        
        email = request.form["email"],
        password = generate_password_hash(request.form["password"]),
        username = request.form["username"],
        userrole =  request.form["userrole"]  

        current_user.email = email
        current_user.password = password
        current_user.username = username
        current_user.userrole = userrole
        print("beforecommit",current_user.email)
        db.session.commit()
        print("aftercommit",current_user.email)
        return redirect(url_for('blog')) 
    return render_template("profile.html") 

@app.route('/blog', methods= ['GET'])
def blog():
    posts = Blog.query.all()
    now =datetime.utcnow()

    return render_template("blog.html",now = now, posts = posts[::-1])

@app.route('/login', methods= ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    if request.method == "POST":
        user = Users.query.filter_by(email = request.form["email"]).first()

        if not user: 
            new_user=Users(
                email = request.form["email"],
                password = generate_password_hash(request.form["password"])
            )
            flash('You have signed up to our blog, add more details to your account', 'success')
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            
            
            return redirect(url_for('profile'))
        if user.check_password(request.form["password"]):   
            login_user(user)
            
            flash('Welcome back {0}'.format(current_user.email), 'success')
            return redirect(url_for('root'))   
        flash('Incorrect password, please try to login again', 'warning')    

    return render_template("login.html") 
    

@app.route('/contact', methods= ['GET'])
def contact():
    return render_template("contact.html")

@app.route('/create-new-blog-post', methods= ['GET', 'POST'])
def createblogpost():
    if request.method == "POST": 
        new_blog=Blog(
            title = request.form["title"],
            body = request.form["body"],
            author = request.form["author"]
        )    
        db.session.add(new_blog) 
        db.session.commit()
        return redirect(url_for('blog')) 
    return render_template("new-blog.html")

    # posts = Blog.query.all()  ## query all the posts from database
    # print('posts ',posts)
    # return render_template('blog.html', posts = posts)  ## render this html file, and also pass posts as props to the html file so that we can consume it inside jinja
@app.route('/blogs/<id>', methods=['GET','POST']) ## specify route with methods
def delete_entry(id):  ## grabing id from route to function
    if request.method == "POST" :  ## check if the request method is POST, we execute the following logic
        post = Blog.query.filter_by(id=id).first() ## select a post from database base on the ID we got from URL
        if not post:  ## if there is no such post, we stop everything 
            return "THERE IS NO SUCH POST"
        db.session.delete(post)  ## else: there's an entry with that ID, we delete it
        db.session.commit()
        return redirect(url_for('blog')) ## then redirect to our root route or function new_post
    return "NOT ALLOWED"  ## guarding against incorrect request method (being nice!)

@app.route('/logout')
@login_required  #require user to be logged in
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)