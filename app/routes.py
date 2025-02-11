from flask import Blueprint, jsonify

routes_bp = Blueprint('main', __name__)

@routes_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong"})
