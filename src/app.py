from flask import Flask, escape, request, render_template, flash, redirect, url_for
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import os
from main import *

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
UPLOAD_FOLDER = '/home/nima/Downloads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
SAVE_FOLDER = '/home/nima/Main_Project/data/testcases/001'
app.config['SAVE_FOLDER'] = SAVE_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User( UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


# import our OCR function
from ocr_core import ocr_core

# define a folder to store and later serve the images
UPLOAD_FOLDER = '/static/uploads/'

# allow files of a specific type
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg' , 'pdf'])



# function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS






@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user, remember=form.remember.data)
                return redirect(url_for('homepage'))

        return '<h1>Invalid username or password</h1>'
        

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()

        #return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)
    

# route and function to handle the upload page
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_page():
    if request.method == 'POST':
        # check if there is a file in the request
        if 'file' not in request.files:
            return render_template('upload.html', msg='No file selected')
        file = request.files['file']
        # if no file is selected
        if file.filename == '':
            return render_template('upload.html', msg='No file selected')

        if file and allowed_file(file.filename):

            # call the OCR function on it
            extracted_text = ocr_core(file)

            # extract the text and display it
            return render_template('upload.html',
                                   msg='Successfully processed',
                                   extracted_text=extracted_text,
                                   )
    elif request.method == 'GET':
        return render_template('upload.html')



@app.route('/logout')
@login_required
def logout():

    logout_user()
    return redirect(url_for('index'))
    
    


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route('/writer', methods=['GET', 'POST'])
def homepage():
    if request.method.lower() == 'get':
        return render_template('home.html')
    elif request.method.lower() == 'post':
        if 'file' not in request.files:
            return 'no part'
        files = request.files.getlist('file')

        # submit an empty part without filename
        for file in files:
            if file.filename == '':
                return 'No selected file'
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                images_from_path = convert_from_path(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                for i, page in enumerate(images_from_path):
                    page.save(f'''{os.path.join(app.config['SAVE_FOLDER'], f"{filename.rsplit('.', 1)[0].lower()}{str(i)}")}{'.jpg'}''')
        
        return 'The writer of the handwritten document is ' + str(myapp())
        
        
        
        
if __name__ == "__main__":
    app.run(debug=True,port=5001)
