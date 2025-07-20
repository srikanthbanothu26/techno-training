from flask import Blueprint, render_template, redirect, flash, request, session, jsonify, url_for, current_app
from app.forms.forms import Student_RegistrationForm, StudentLoginForm, forget_passwordform, update_passwordForm
from app.oper.oper import check_user_exists, add_user
from flask_bcrypt import Bcrypt
from app.models.models import User
from flask_login import login_user, login_required, current_user, logout_user
import os
from app.extensions.db import db
from werkzeug.utils import secure_filename
from flask_wtf.csrf import generate_csrf
from sqlalchemy.exc import IntegrityError

bcrypt = Bcrypt()
student_bp = Blueprint('student', __name__)

PROFILE_PICS_FOLDER = 'static/profile_pics'


@student_bp.route('/student_registration', methods=["GET", "POST"])
def registration():
    form = Student_RegistrationForm(request.form)
    csrf_token = generate_csrf()
    user_exists = False
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        course = form.course.data
        profile_image = form.profile_image.data
        filename = None

        if profile_image:
            filename = f"{current_user.id}.png"

            profile_image_path = os.path.join(PROFILE_PICS_FOLDER, filename)
            profile_image.save(profile_image_path)

            # Update the user's profile image path in the database
            current_user.profile_image = filename
            db.session.commit()

        try:
            if not check_user_exists(username, email, course) and password == confirm_password:
                hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
                add_user(username, email, hashed_password, course, profile_image=filename)
                flash("Registration successful. Please log in.")
                return redirect('/student_login')
            else:
                user_exists = True
        except IntegrityError:
            user_exists = True

    return render_template('student_reg.html', form=form, csrf_token=csrf_token, user_exists=user_exists)


@student_bp.route("/student_login", methods=["GET", "POST"])
def login():
    form = StudentLoginForm(request.form)
    csrf_token = generate_csrf()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        course = form.course.data
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password) and course == user.course:
            login_user(user)
            session['username'] = user.username  # Store username in session
            session['course'] = user.course  # Store user course in session
            return redirect("/main")
        else:
            flash("Invalid credentials. Please try again.", "error")
    return render_template("student_login.html", form=form, csrf_token=csrf_token)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


@student_bp.route('/upload_profile_image', methods=['POST'])
@login_required
def upload_profile_image():
    try:
        if 'profile_image' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'}), 400

        file = request.files['profile_image']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400

        if file:
            filename = secure_filename(f"{current_user.id}.png")
            file_path = os.path.join(current_app.root_path, 'static', 'profile_pics', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(file.read())
            current_user.profile_image = filename
            db.session.commit()

            return jsonify({'success': True, 'message': 'File uploaded successfully', 'redirect_url': ''}), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to upload profile image', 'redirect_url': ''}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@student_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = forget_passwordform(request.form)
    if form.validate_on_submit():
        email = form.email.data
        print(email)
        user = User.query.filter_by(email=email).first()
        if user:
            session['reset_email'] = email  # Set the email in the session
            return redirect('/forgot_password_verify_email')
        else:
            return redirect("/student_registration")
    return render_template('forgot_password_email.html', form=form)


# Route to handle the verification of email for forgot password
@student_bp.route('/forgot_password_verify_email', methods=['GET', 'POST'])
def forgot_password_verify_email():
    form = update_passwordForm(request.form)  # Instantiate the form object
    if form.validate_on_submit():
        new_password = form.password.data
        confirm_password = form.confirm_password.data
        if new_password == confirm_password:
            email = session.get('reset_email')
            user = User.query.filter_by(email=email).first()
            if user:
                # Update the password for the user
                user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
                db.session.commit()
                flash("Password updated successfully. Please log in.")
                session.pop('reset_email')
                return redirect('/student_login')
            else:
                flash("User not found. Please try again.", "error")
        else:
            flash("Passwords do not match. Please try again.", "error")
    return render_template('forgot_password_update.html', form=form)


@student_bp.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    # Check if the current user is authenticated
    if current_user.is_authenticated:
        try:
            # Delete the user from the database
            db.session.delete(current_user)
            db.session.commit()
            # Log the user out
            logout_user()
            flash("Your account has been successfully deleted.")
            return redirect('/')
        except Exception as e:
            flash(f"An error occurred while deleting your account: {str(e)}", "error")
# If the request method is not POST or the user is not authenticated, redirect to the homepage
