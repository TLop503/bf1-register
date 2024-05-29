import re
import hashlib
import json
import secrets

from flask import Flask, request, jsonify

app = Flask(__name__)

db_pth = "../users" # path to users on remote


def hash(user, passw):
    salt = secrets.token_bytes(16)
    prep = lambda user, passw, sal: (user + passw + salt .encode())
    return salt, hashlib.sha256(prep(user, passw, salt ).hexdigest())


def user_exists(user):
    with open(db_pth, 'r') as file:
        data = json.loads(file)

        if user in data:
            return 1
        else: return 0


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    print(data)
    if 'user' not in data:
        return jsonify({'Error': 'User field is missing'}), 400
    if 'pass' not in data:
        return jsonify({'Error: password not in data'}), 400
    if user_exists(data['user']):
        # return conflict status
        return jsonify({'Error: user already exists'}, 409)
    
    else:
        salt, tok = hash(data['user'], data['pass'])
        new_user = {
            'salt': salt.hex(),
            'token': tok
        }
        with open(db_pth, 'r+') as file:
            try:
                db_data = json.load(file)
            # if blank
            except json.JSONDecodeError:
                db_data = {}
            
            db_data[data['user']] = new_user
            file.seek(0)  # Move the cursor to the beginning of the file
            json.dump(db_data, file)  # Write the updated data back to the file
            file.truncate()  # Remove any remaining data
            
        return jsonify({'Message': 'User registered successfully'}), 201


if __name__ == '__main__':
    app.run(debug=True)
    #add port=##### to change the port the api uses