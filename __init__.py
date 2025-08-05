'''imports'''
from flask import Flask, render_template, request, jsonify, redirect, flash, url_for
import os
import shelve
import magic
import re

app = Flask(__name__)
app.secret_key = 'qwfgsgs23124'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'profiles') #path to save pfps to
app.config['MAX_CONTENT_LENGTH'] = 2*1024*1024 #2MB file limit

from accounts.admin import Admin

ADMIN_SHELVE_NAME = 'admin_accounts.db' # shelve file

ALLOWED_ADMIN_EMAILS = [
    "mockmock582@gmail.com"
]

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Functions
def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email)

def is_strong_password(password):
    if (len(password) < 8): # check for atleast 8 length
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password): # check for atleast one special char
        return False
    return True

@app.route('/')
def home():
    '''Home/Dashboard page (page user logs into)'''

    return render_template('home.html')

@app.route('/reset-password-mail')
def check_mail():
    '''After user submits email to get password change'''

    return render_template('check-mail.html')

@app.route('/login')
def login():
    '''login page'''

    return render_template('login.html')

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
            if username in db:
                flash('User already exists. Please Login instead.', 'warning')
                return redirect(url_for('register'))

            # create new admin user
            new_admin = Admin(username=username, email=email, password=password, job='Admin')

            db[username] = new_admin

        flash('Admin account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/user-pwid')
def user_pwid():
    '''pwid table csv page'''

    return render_template('user-pwid.html')

@app.route('/user-caretaker')
def user_caretaker():
    '''caretaker table csv page'''

    return render_template('user-caretaker.html')

@app.route('/edit-userprofile')
def edit_userprofile():
    '''edit user profile'''

    return render_template('edit-userprofile.html')

@app.route('/upload', methods=['POST'])
def upload_pfp():
    '''handle user profile picture upload'''

    if 'file' not in request.files:
        return jsonify({'error':'No file found'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file_bytes = file.read(2048)  # 2KB is usually enough
    file.seek(0)  # Reset pointer for saving

    mime_type = magic.from_buffer(file_bytes, mime=True)

    if mime_type not in ['image/png', 'image/jpeg']:
        return jsonify({'error': 'Only JPEG and PNG images are allowed'}), 400
    
    # user_id = get_current_user_id()  # You must define this
    # filename = f"user_{user_id}.{kind.extension}"
    # save_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))

    # file.save(save_path)

    # return jsonify({'success': True, 'filename': filename}), 200
# Add more routes as needed

if __name__ == '__main__':
    app.run(debug=True)
