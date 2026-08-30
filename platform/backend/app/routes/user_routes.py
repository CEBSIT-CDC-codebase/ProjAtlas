from flask import Blueprint, jsonify, request
from datetime import datetime
from ..models import User
from .. import db

user_routes = Blueprint('user', __name__)


@user_routes.route('/get-user/<string:email>')
def get_user(email):
    """Get active user (automatically filters out deleted users)"""
    if user := User.query.filter_by(email=email).first():  # Directly calls the model method
        return jsonify(user=user.to_dict())
    return jsonify(error="Active user not found"), 404


@user_routes.route('/add-user', methods=['POST'])
def add_user():
    """Add user (only validates that email is required)"""
    data = request.get_json() or {}

    if not data.get('email'):
        return jsonify(error="Email is required"), 400

    try:
        new_user = User(email=data['email'])
        # Optional field updates
        for field in ['name', 'title', 'department', 'role']:
            if field in data:
                setattr(new_user, field, data[field])

        db.session.add(new_user)
        db.session.commit()
        return jsonify(user=new_user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 400


@user_routes.route('/update-user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user (directly uses the model method)"""
    if not (user := User.query.get(user_id)):
        return jsonify(error="User not found"), 404

    if not (data := request.get_json()):
        return jsonify(error="No data provided"), 400

    try:
        user.safe_update(data)  # Uses the model's built-in method
        db.session.commit()
        return jsonify(user=user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 400


@user_routes.route('/delete-user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Soft delete user (marks deletion time)"""
    if not (user := User.query.get(user_id)):
        return jsonify(error="User not found"), 404

    try:
        user.deleteAt = datetime.now()  # Soft delete marker
        db.session.commit()
        return jsonify(message="User deleted successfully"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500
