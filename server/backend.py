from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/debug', methods=['GET'])
def connect_response():
    return jsonify({"message": "Flask Server Works"})

if __name__ == '__main__':
    app.run(debug=True)
