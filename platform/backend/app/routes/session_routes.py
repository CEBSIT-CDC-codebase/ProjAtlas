from flask import Blueprint, jsonify, request
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from ..models import Session,User
from .. import db

session_routes = Blueprint('session', __name__)

def validate_userId(userId):
    """Validate that userId is provided and exists in the User table"""
    if not userId:
        return jsonify({"error": "userId is required"}), 400
    user = User.query.filter_by(id=userId).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return None

@session_routes.route('/get-sessions/<int:userId>')
def get_sessions(userId):
    validation_result = validate_userId(userId)
    if validation_result:
        return validation_result
    sessions = Session.query.join(User).filter(
        Session.userId == userId,
        Session.deleteAt.is_(None)  # Only query sessions that have not been deleted
    ).all()
    return jsonify(sessions=[session.to_dict() for session in sessions]), 200


@session_routes.route('/get-session/<int:sessionId>')
def get_session(sessionId):
    if session := Session.get_active_session(sessionId):  # Directly calls the model method
        return jsonify(session=session.to_dict())
    return jsonify(error="Session not found"), 404


@session_routes.route('/add-session', methods=['POST'])
def add_session():
    data = request.get_json() or {}

    try:
        validation_result = validate_userId(data['userId'])
        if validation_result:
            return validation_result
        Session.validate_create(data)  # Calls model validation
        new_session = Session(
            name=data['name'],
            userId=data['userId']
        )
        db.session.add(new_session)
        db.session.commit()
        return jsonify(session=new_session.to_dict()), 201
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except IntegrityError:
        return jsonify(error="User does not exist"), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500


@session_routes.route('/update-session/<int:sessionId>', methods=['PUT'])
def update_session(sessionId):
    """Update user (directly uses the model method)"""
    if not (session := Session.query.get(sessionId)):
        return jsonify(error="Session not found"), 404

    if not (data := request.get_json()):
        return jsonify(error="No data provided"), 400

    try:
        session.safe_update(data)  # Uses the model's built-in method
        db.session.commit()
        return jsonify(session=session.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 400


@session_routes.route('/delete-session/<int:sessionId>', methods=['DELETE'])
def delete_session(sessionId):
    """Soft delete user (marks deletion time)"""
    if not (session := Session.query.get(sessionId)):
        return jsonify(error="Session not found"), 404

    try:
        session.deleteAt = datetime.now()  # Soft delete marker
        db.session.commit()
        return jsonify(message="Session deleted successfully"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500
