from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import json
from sqlalchemy.exc import IntegrityError
from ..models import Message, Session
from .. import db, executor
# import time
from atlas_assistant.assistant import UserInput
from . import globals

message_routes = Blueprint('message', __name__)

JSON_LIST_FIELDS = {'neurons', 'regions', 'matrix'}


def validate_session_id(sessionId):
    """Validate that sessionId is provided and exists in the Session table"""
    if not sessionId:
        return jsonify({"error": "sessionId is required"}), 400
    session = Session.query.filter_by(id=sessionId).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return None


@message_routes.route('/get-messages/<int:sessionId>', methods=['GET'])
def get_messages(sessionId):
    """Get all sessions for the current user (excluding deleted messages)"""
    validation_result = validate_session_id(sessionId)
    if validation_result:
        return validation_result

    # Add filter condition where deleteAt is null
    messages = Message.query.filter(
        Message.sessionId == sessionId,
        Message.deleteAt.is_(None)  # Only query messages that have not been deleted
    ).all()
    return jsonify(messages=[message.to_dict() for message in messages]), 200


@message_routes.route('/get-message/<int:messageId>')
def get_message(messageId):
    if message := Message.get_active_message(messageId):
        return jsonify(message=message.to_dict())
    return jsonify(error="Message not found"), 404


@message_routes.route('/add-message', methods=['POST'])
def add_message():
    data = request.get_json() or {}
    try:
        validation_result = validate_session_id(data['sessionId'])
        if validation_result:
            return validation_result
        Message.validate_create(data)  # Calls model validation
        new_message = Message(
            role=data['role'],
            sessionId=data['sessionId'],
            task=data['task'],
        )
        # Optional field updates
        for field in ['content', 'toolCalls',  'neurons', 'matrix', 'regions']:
            if field in data:
                if field in JSON_LIST_FIELDS:
                    setattr(new_message, field, json.dumps(data[field]))
                else:
                    setattr(new_message, field, data[field])

        db.session.add(new_message)
        db.session.commit()

        def background_task():
            start_time = datetime.now()
            result = globals.chat_session.send_message(
                UserInput(id=data.get('sessionId', ''), content=data.get('content', ''), task=data.get('task', ''), neurons=data.get('neurons', []), regions=data.get('regions', []), matrix=data.get('matrix', [])))
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            if not result.content and result.tool_calls:
                result.content = 'Execution Completed'
            elif not result.content and not result.tool_calls:
                result.content = 'We’re unable to provide a solution for this question, please try another one.'
            new_message = Message(
                role='assistant',
                sessionId=data['sessionId'],
                task=data['task'],
                toolCalls=json.dumps(result.tool_calls),
                content=result.content,
            )
            print(f"Execution time: {execution_time} seconds")
            db.session.add(new_message)
            db.session.commit()

        executor.submit(background_task)
        return jsonify(message=new_message.to_dict()), 201

    except ValueError as e:
        return jsonify(error=str(e)), 400
    except IntegrityError:
        return jsonify(error="User does not exist"), 400
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(error=str(e)), 500


@message_routes.route('/update-message/<int:messageId>', methods=['PUT'])
def update_message(messageId):
    """Update user (directly uses the model method)"""
    if not (message := Message.query.get(messageId)):
        return jsonify(error="Message not found"), 404

    if not (data := request.get_json()):
        return jsonify(error="No data provided"), 400

    try:
        message.safe_update(data)  # Uses the model's built-in method
        db.session.commit()
        return jsonify(message=message.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 400


@message_routes.route('/delete-message/<int:messageId>', methods=['DELETE'])
def delete_message(messageId):
    """Soft delete user (marks deletion time)"""
    if not (message := Message.query.get(messageId)):
        return jsonify(error="Message not found"), 404

    try:
        message.deleteAt = datetime.now()  # Soft delete marker
        db.session.commit()
        return jsonify(message="Message deleted successfully"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500
