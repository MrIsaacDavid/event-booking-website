#used for authentication of users like login and sign-up
from flask import Blueprint,request, jsonify,abort,g
from .models import User, Booking,Event
from werkzeug.security import generate_password_hash,check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user,login_required,current_user
import jwt
from datetime import datetime,timedelta
from functools import wraps
from . import KEY
from flask_bcrypt import Bcrypt






auth =Blueprint('auth',__name__)
bcrypt = Bcrypt()
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = jwt.decode(token.split()[1], KEY, algorithms=['HS256'])
            user_id = data.get('user_id')
            user_id = data.get('user_id')
            user = User.query.get(user_id)

            if user and user.is_admin:
                g.current_user = user
                return f(*args, **kwargs)
            else:
                return jsonify({"error": "Not authorized to access this resource"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

    return decorated_function


# API endpoint to update the is_admin property of a user

@auth.route('/users/<int:user_id>/admin', methods=['PUT'])
@admin_required
def make_user_admin(user_id):
    user = User.query.get(user_id)

    if not user:
        abort(404)  # User not found

    data = request.get_json()
    if 'is_admin' in data:
        user.is_admin = data['is_admin']
        db.session.commit()
        return jsonify({"message":"User admin status updated successfully"}), 200
    else:
        return jsonify({"message":"Invalid request data"}), 400


@auth.route('/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    if data and "email" in data and "firstName" in data and "password" in data:
        email = data.get('email')
        first_name = data.get('firstName')
        password = data.get('password')  # Corrected variable name

        if len(password) < 8:
            return jsonify({"message": "Password should be at least 8 characters long."}), 400

        
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


@auth.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = request.json.get('email')
    password = request.json.get('password')

    admin_user = User.query.filter_by(email=email, is_admin=True).first()

    if admin_user and check_password_hash(admin_user.password, password)==True:
        # Generate a JWT token for the admin user
        token_payload = {
            'user_id': admin_user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(token_payload, KEY, algorithm='HS256')
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

      
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
    
@auth.route('/Create_event', methods=['POST'])
@admin_required
def create_event():
    data = request.get_json()
    name = data.get('name')
    date_str = data.get('date')
    venue=data.get('venue')
    max_users = data.get('max_users')

    try:
        # Convert the date string to a datetime object
        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()

        # Check if an event with the same name already exists
        existing_event = Event.query.filter_by(name=name).first()
        if existing_event:
            return jsonify(message='Event with the same name already exists'), 400

        new_event = Event(name=name, date=date_obj, venue=venue, max_users=max_users)

        db.session.add(new_event)
        db.session.commit()
        return jsonify(message='Event created successfully'), 201

    except ValueError:
        return jsonify(message='Invalid date format'), 400

    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500
# Get all events API
@auth.route('/event', methods=['GET'])
@login_required
def get_events():
    events = Event.query.all()
    event_list = []
    for event in events:
        event_data = {
            'id': event.id,
            'eventname': event.name,
            'eventdate': event.date.strftime('%Y-%m-%d %H:%M:%S'),  # Format the datetime if needed
            'venue':event.venue
        }
        event_list.append(event_data)
    return jsonify(events=event_list), 200
@auth.route('/book', methods=['POST'])
@login_required  # Use this decorator to ensure the user is authenticated before creating a booking
def create_book():
    data = request.get_json()
    user_id = data.get('user_id')
    event_ids = data.get('event_ids')  # Use 'event_ids' to represent multiple event IDs

    user = User.query.get(user_id)

    if user:
        for event_id in event_ids:
            event = Event.query.get(event_id)

            if event:
                existing_booking = Booking.query.filter_by(user_id=user_id, event_id=event_id).first()

                if existing_booking:
                    return jsonify({'message': 'User has already booked for event with ID {}'.format(event_id)}), 400

                remaining_slots = event.max_users - Booking.query.filter_by(event_id=event_id).count()

                if remaining_slots <= 0:
                    return jsonify({'message': 'No available slots for event with ID {}'.format(event_id)}), 400

                new_booking = Booking(user_id=user_id, event_id=event_id)
                db.session.add(new_booking)
                db.session.commit()

            else:
                return jsonify({'message': 'Invalid event ID: {}'.format(event_id)}), 400

        return jsonify({'message': 'Bookings created successfully'}), 201

    else:
        return jsonify({'message': 'Invalid user ID'}), 400
@auth.route('/users_with_bookings', methods=['GET'])
def get_users_with_bookings():
    users_with_bookings = []
    bookings = Booking.query.all()  # Query all bookings from the database
    for booking in bookings:
        user = User.query.get(booking.user_id)
        event=Event.query.get(booking.event_id)  # Assuming user_id is a foreign key in Booking model
        users_with_bookings.append({
            'user_id': user.id,
            'first_name': user.first_name,
            'email': user.email,
            'booking_id': booking.id,
            'event_name':event.name,
            'Venue':event.venue,
            'event_id':event.id
            
           
        })
    return jsonify(users_with_bookings)

@auth.route('/bookings/<int:event_id>', methods=['DELETE'])
#@login_required
#@admin_required
def delete_event(event_id):
    event = Booking.query.get(event_id)

    if event is None:
        return jsonify({"error": "Event not found"}), 404

    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({"message": "Event deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)  # Retrieve the user by their ID

    if user:
        # If the user is found, return their data as JSON response
        response = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'is_admin':user.is_admin
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
        users_list.append({'id': user.id, 'email': user.email, 'first_name':user.first_name,'is_admin':user.is_admin})
    return jsonify({'users': users_list})
@auth.route('/user/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    if g.current_user is None:
        return jsonify({"error": "User not found"}), 404

    if not g.current_user.is_admin:
        return jsonify({"error": "Not authorized to delete users"}), 401

    user_to_delete = User.query.get(user_id)
    if user_to_delete is None:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user_to_delete)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"})

''''
@auth.route('/user/recover/<int:user_id>', methods=['PUT'])
def recover_user(user_id):
    user = User.query.filter_by(id=user_id, is_deleted=True).first()

    if user:
        user.is_deleted = False
        db.session.commit()
        return jsonify({'message': 'User recovered successfully'}), 200
    else:
        return jsonify({'message': 'User not found or already recovered'}), 404

'''
