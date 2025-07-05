from flask import Flask, request, jsonify

from index import bp as index
from whatsapp import bp as whatsapp

app = Flask(__name__)
app.register_blueprint(index)
app.register_blueprint(whatsapp)

# if __name__ == '__main__':
#     app.run(port=5001)