#used for authentication of users like login and sign-up
from flask import Blueprint,render_template,request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user

auth =Blueprint('auth',__name__)

@auth.route('/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    if data and "email" in data and "firstName" in data and "password" in data:
        email = data.get('email')
        first_name = data.get('firstName')
        password = data.get('password')  # Corrected variable name
        
        user = User.query.filter_by(email=email).first()

        if user is None:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return jsonify({'message': 'User created successfully!'}),201
        else:
            return jsonify({'message': 'Email already exists!'})

    else:
        return jsonify({"message": "Invalid data!"})

      
@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email and password:
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password)==True:  # Assuming you have a method to check the password in your User model
            
            login_user(user)
            return jsonify({'message': 'Successfully logged in', 'email': email}), 200
        else:
            return jsonify({'message': 'Unauthorized user'}), 401
    else:
        return jsonify({'message': 'Bad Request - Missing email or password'}), 400

@auth.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)  # Retrieve the user by their ID

    if user:
        # If the user is found, return their data as JSON response
        response = {
            'id': user.id,
            'email': user.email,
            'password': user.password
        }
        return jsonify(response), 200
    else:
        # If user is not found, return a 404 Not Found response
        return jsonify({'message': 'User not found'}), 404
    
@auth.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append({'id': user.id, 'email': user.email})
    return jsonify({'users': users_list})

