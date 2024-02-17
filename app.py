import random
from flask import jsonify
import secrets
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, session
from flask_sqlalchemy import SQLAlchemy
import openai
import google.generativeai as genai
import random

genai.configure(api_key="AIzaSyAdt0wkdAX-uM1x5rYaG8y8AwrNvb17th8")
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = "m4xpl0it"


def make_token():
    """
    Creates a cryptographically-secure, URL-safe string
    """
    return secrets.token_urlsafe(16) 
 
class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))


@app.route("/")
def index():
    return render_template("index.html")


userSession = {}

@app.route("/user")
def index_auth():
    my_id = make_token()
    userSession[my_id] = -1
    return render_template("index_auth.html",sessionId=my_id)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index1.html')
def stress_relief():
    return render_template('index1.html')

@app.route('/community.html')
def community():
    return render_template('community.html')

@app.route('/critical.html')
def critical():
    return render_template('critical.html')

@app.route('/criticalthinking2.html')
def criticalthinking2():
    return render_template('criticalthinking2.html')

@app.route('/types.html')
def types():
    return render_template('types.html')

@app.route('/yoga.html')
def yoga():
    return render_template('yoga.html')

@app.route("/upload")
def bmi():
    return render_template("bmi.html")

@app.route('/pred_page')
def pred_page():
    pred = session.get('pred_label', None)
    f_name = session.get('filename', None)
    return render_template('pred.html', pred=pred, f_name=f_name)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]

        login = user.query.filter_by(username=uname, password=passw).first()
        if login is not None:
            return redirect(url_for("index_auth"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']

        register = user(username=uname, email=mail, password=passw)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


# Gemini API integration
def get_gemini_response(question):
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    response = chat.send_message(question, stream=True)
    
    parts_text = []
    for chunk in response:
        for part in chunk.parts:
            parts_text.append(part.text)

    return parts_text

# Route for handling user messages
userSession = {}

# Initialize global dictionary to store user information
all_result = {}

@app.route('/ask', methods=['GET', 'POST'])
def chat_msg():
    user_message = request.args.get("message", "").lower()
    sessionId = request.args.get("sessionId", "")

    response = []

    if user_message == "undefined":
        rand_num = random.randint(0, 4)
        response.append("Hi, How can I assist you today? Feel free to share what's on your mind.")
        userSession[sessionId] = 0
        all_result['name'] = ""

    else:
        currentState = userSession.get(sessionId, -1)

        if currentState == -1:
            response.append("Hi " + user_message + ", How can I assist you today? Feel free to share what's on your mind.")
            userSession[sessionId] = 0
            all_result['name'] = user_message

        else:
            # Call Gemini API to get response for user's message
            response = get_gemini_response(user_message)
            userSession[sessionId] += 1

    return jsonify({'status': 'OK', 'answer': response})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False, port=3000)
