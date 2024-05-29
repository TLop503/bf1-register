import re
import hashlib
import json
import secrets

from flask import Flask, request, jsonify

app = Flask(__name__)

db_pth = "../users" # path to users on remote


def hash(user, passw):
    salt = secrets.token_bytes(16)
    prep = lambda user, passw, sal: ((user + passw ).encode() + sal)
    encoded_prep = prep(user, passw, salt)
    hashed = (hashlib.sha256(encoded_prep)).hexdigest()
    return salt, hashed



def user_exists(user):
    with open(db_pth, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = {}

        if user in data:
            return True
        else:
            return False


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if 'user' not in data:
        return jsonify({'Error': 'User field is missing'}), 400
    if 'pass' not in data:
        return jsonify({'Error': 'Password field is missing'}), 400
    if user_exists(data['user']):
        return jsonify({'Error': 'User already exists'}), 409
    
    else:
        salt, tok = hash(data['user'], data['pass'])
        new_user = {
            'salt': salt.hex(),
            'token': tok
        }
        with open(db_pth, 'r+') as file:
            try:
                db_data = json.load(file)
            except json.JSONDecodeError:
                db_data = {}
            
            db_data[data['user']] = new_user
            file.seek(0)
            json.dump(db_data, file)
            file.truncate()
            
        return jsonify({'Message': 'User registered successfully'}), 201


if __name__ == '__main__':
    app.run(debug=True, port=5001)
    #add port=##### to change the port the api uses