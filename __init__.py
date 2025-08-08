# Standard library imports
import os
import re
import shelve
from datetime import timedelta, datetime
import uuid
import csv

# Third-party library imports
from flask import Flask, render_template, request, jsonify, redirect, flash, url_for, session
from flask_mail import Mail, Message
import magic
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Local application imports
from accounts.admin import Admin

load_dotenv()

app = Flask(__name__)
app.secret_key = 'qwfgsgs23124'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'profiles') #path to save pfps to
app.config['MAX_CONTENT_LENGTH'] = 2*1024*1024 #2MB file limit
app.config.update(
    MAIL_SERVER=str(os.getenv('MAIL_SERVER')),
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=str(os.getenv('MAIL_USERNAME')),
    MAIL_PASSWORD=str(os.getenv('MAIL_PASSWORD')), # SMTP key
    MAIL_DEFAULT_SENDER=str(os.getenv('MAIL_DEFAULT_SENDER'))
)

# set up mail
mail = Mail(app)

# csv file for page view logging
LOG_FILE = 'page_views.csv'


# set permanent session lifetime to 70 days
app.permanent_session_lifetime = timedelta(days=70)

ADMIN_SHELVE_NAME = 'admin_accounts.db' # shelve file

ALLOWED_ADMIN_EMAILS = [
    "mockmock582@gmail.com",
    "epicaresystem@gmail.com"
]

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

serializer = URLSafeTimedSerializer(app.secret_key)

# Functions
def log_page_view(user=None):
    with open('page_views.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        user_type = 'Unknown'
        if user is not None:
            user_type = user.get_user_type()

        writer.writerow([datetime.now().isoformat(), user_type])


def send_mail(subject, recipients, body, html=None):
    '''
    Sends an email using Flask-Mail.
    
    :param subject: Email subject
    :param recipients: List of recipient emails
    :param body: Plain text body
    :param html: Optional HTML body
    :param sender: Optional override sender
    '''
    msg = Message(
        subject=subject,
        recipients=recipients,
        sender=str(os.getenv('MAIL_DEFAULT_SENDER'))
    )
    msg.body = body
    if html:
        msg.html=html
    mail.send(msg)
    print('success')


def is_valid_email(email):
    '''check for email validity using regex'''

    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email)


def is_strong_password(password):
    '''check for password validity'''

    if len(password) < 8: # check for atleast 8 length
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password): # check for atleast one special char
        return False
    return True


def get_current_user():
    user_email = session.get('email')
    if not user_email:
        return None

    with shelve.open('admin_accounts.db') as db:
        user = db.get(user_email)

    return user

# ─────────── Routes ───────────

# ─────────── Auth Routes (Unauthenticated) ───────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''login page'''

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember =  request.form.get('remember') # 'on' if checkbox is checked

        with shelve.open(ADMIN_SHELVE_NAME) as db:
            if email in db:
                admin = db[email]
                if admin.get_password() == password:
                    session['email'] = email
                    session.permanent = bool(remember)
                    return redirect(url_for('home'))
                else:
                    flash('Incorrect password.', 'danger')
            else:
                flash('Email not found.', 'danger')

    log_page_view() # log the page view
    return render_template('login.html')

@app.route('/logout')
def logout():
    '''logs out the current user'''

    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''register page'''

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if not is_valid_email(email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('register'))

        if not is_strong_password(password):
            flash('Password must be at least 8 characters long ' \
            'and a special character.')
            return redirect(url_for('register'))


        if email not in ALLOWED_ADMIN_EMAILS:
            flash("Email not authorized to register as admin", "danger")
            return redirect(url_for("register"))

        username = email.split('@')[0]

        with shelve.open(ADMIN_SHELVE_NAME) as db:

            # check if user exists
            if email in db:
                flash('User already exists. Please Login instead.', 'warning')
                return redirect(url_for('register'))

            # create new admin user
            new_admin = Admin(username=username, email=email,
                              password=password, job='Administrator')

            db[email] = new_admin

        flash('Admin account created successfully!', 'success')
        return redirect(url_for('login'))

    log_page_view() # log the page view
    return render_template('register.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    '''page to submit email to send password reset link'''

    if request.method == 'POST':
        email = request.form.get('email')

        with shelve.open(ADMIN_SHELVE_NAME) as db:
            if email in db:
                # Generates a token that will expire after time
                token = serializer.dumps(email, salt='reset-password')

                # Create reset link
                reset_url = url_for('reset_password', token=token, _external=True)

                subject = 'Reset Your Epicare Password'
                body=f'Hi, you requested a password reset. Click the link below to reset your password:\n{reset_url}'

                send_mail(subject, [email], body, html=render_template('partials/reset-password-email.html', reset_url=reset_url))

        flash('Password reset link has been sent to the email', 'info')
        return redirect(url_for('check_mail')) # redirect to check-mail page
    
    log_page_view() # log the page view
    return render_template('forgot-password.html')


@app.route('/reset-password-mail')
def check_mail():
    '''After user submits email to get password change'''

    log_page_view() # log the page view
    return render_template('check-mail.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    '''page to reset password after user clicks link in email'''

    try:
        # deserialize email from token, expire after 1 hour
        email = serializer.loads(token, salt='reset-password', max_age=3600)

    except SignatureExpired:
        flash('The password reset link has expired.', 'danger')
        return redirect(url_for('login'))
    except BadSignature:
        flash("Invalid reset link.", "danger")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('reset-password.html', token=token)
        
        if not is_strong_password(password):
            flash('Password must be at least 8 characters long ' \
            'and a special character.')
            return render_template('reset-password.html', token=token)
        
        with shelve.open(ADMIN_SHELVE_NAME, writeback=True) as db:
            if email in db:
                db[email].set_password(password)
                flash('Password successfully updated.', 'success')
                return redirect(url_for('login'))

            else:
                flash('User no longer exists', 'danger')

    return render_template('reset-password.html')

# ─────────── Content Routes (Authenticated) ───────────

@app.route('/')
def home():
    '''Home/Dashboard page (page user logs into)'''


    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    log_page_view(user) # log the page view
    return render_template('home.html', user=user)


@app.route('/user-pwid')
def user_pwid():
    '''pwid table csv page'''
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    log_page_view(user) # log the page view
    return render_template('user-pwid.html', user=user)


@app.route('/user-caretaker')
def user_caretaker():
    '''caretaker table csv page'''
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    log_page_view(user) # log the page view
    return render_template('user-caretaker.html', user=user)


@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    '''edit user profile page'''
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if request.method=='POST':
        updated = False

        # Username update
        new_username = request.form.get('username', '').strip()
        if new_username and new_username != user.get_username():
            user.set_username(new_username)
            updated = True

        # Profile picture update
        file = request.files.get('profile_picture')
        if file and file.filename.strip(): # checks if file exists and if filename is not empty
            file_bytes = file.read(2048) # read the file
            file.seek(0) # reset pointer after read

            mime_type = magic.from_buffer(file_bytes, mime=True)
            allowed_types = ['image/jpeg', 'image/png'] # allow only jpeg and png files

            if mime_type in allowed_types:
                # sanitize filename to prevent unsafe files
                filename = secure_filename(file.filename)

                # unique filename to avoid conflict
                unique_filename = f'{uuid.uuid4().hex}_{filename}'

                # build the path where file will be saved
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

                # save uploaded file to filesystem
                file.save(file_path)

                user.profile_picture = os.path.join('uploads', 'profiles', unique_filename).replace("\\", '/')
                updated = True
            else:
                # if file type is invalid
                flash('Only .jpeg and .png files are allowed', 'danger')
                return redirect(url_for('edit_profile'))

        # save changes to shelve
        if updated:
            with shelve.open(ADMIN_SHELVE_NAME, writeback=True) as db:
                db[user.get_email()] = user
            flash('Profile updated successfully!', 'success')

        else:
            # no changes detected
            flash('No changes were made', 'info')

        #redirect to same page
        return redirect(url_for('edit_profile'))

    log_page_view(user) # log the page view
    # For GET requests, render template
    return render_template('edit-userprofile.html', user=user)




if __name__ == '__main__':
    app.run(debug=True)
