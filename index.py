from flask import Blueprint
bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    return 'Hello from routes1!'