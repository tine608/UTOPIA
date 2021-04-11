from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.validators import Length, EqualTo, DataRequired
from passlib.hash import sha256_crypt
app = Flask(__name__)
app.secret_key = 'Mini Flask'

#config SQL
app.config['MYSQL_Host'] = 'localhost'
app.config['MYSQL_USER'] = 'newuser'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'miniflask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MYSQL
mysql = MySQL(app)

@app.route('/')
@app.route('/home')
def index():
	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/story')
def story():
	return render_template('story.html')

@app.route('/babies')
def babies():
	return render_template('babies.html')

@app.route('/gallery')
def gallery():
	return render_template('gallery.html')


class RegisterForm(Form):
	name = StringField('Name',[validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('password', [validators.DataRequired(), validators.EqualTo('confirm', message = 'Passwords do not match')])
	confirm = PasswordField('Confirm Password')


class LoginForm(Form):
	username = StringField('Username', [validators.Length(min=4, max=25)])
	password = PasswordField('password', [validators.DataRequired()])
	

@app.route('/register', methods=['GET', 'POST'])		
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data 
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		#create cursor
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))

		#comit to DB
		mysql.connection.commit()

		#close connection
		cur.close()

		flash("You are now registered and can log in", 'success')
		return redirect(url_for('index'))
	return render_template('register.html', form = form)

@app.route('/login', methods=["GET", "POST"])
def login():
	form = LoginForm(request.form)
	if request.method == 'POST':
		username = form.username.data
		password_candidate = form.password.data

		cur = mysql.connection.cursor()

		result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
		if result > 0:
			password = password_candidate

			if sha256_crypt.verify(password_candidate, password):
				app.logger.info('PASSWORD MATCHED')
			else:
				app.logger,info('PASSWORD NOT MARCHED')
		else:
			app.logger.info('NO USER')
	return render_template('login.html', form = form)

if __name__ == '__main__':
	app.run(debug=True)
	