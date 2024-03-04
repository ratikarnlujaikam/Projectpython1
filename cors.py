from flask_cors import CORS

def setup_cors(app):
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})