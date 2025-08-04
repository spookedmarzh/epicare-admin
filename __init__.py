'''imports'''
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import magic

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'profiles') #path to save pfps to
app.config['MAX_CONTENT_LENGTH'] = 2*1024*1024 #2MB file limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

@app.route('/register')
def register():
    '''register page'''

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
