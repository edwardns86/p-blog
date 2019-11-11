from flask import Flask, render_template

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'

@app.route('/', methods= ['GET'])
def root():
    return render_template("home.html")

@app.route('/about', methods= ['GET'])
def about():
    return render_template("about.html")

@app.route('/blog', methods= ['GET'])
def blog():
    return render_template("blog.html")

@app.route('/login', methods= ['GET'])
def login():
    return render_template("login.html")

@app.route('/contact', methods= ['GET'])
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)