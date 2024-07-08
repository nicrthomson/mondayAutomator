import os
import json
import requests
import asyncio
import aiohttp
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import anthropic

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monday_board_editor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this in a real app
CORS(app, supports_credentials=True)

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    monday_api_token = db.Column(db.String(200), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password=hashed_password, monday_api_token=data.get('monday_api_token'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'username': user.username, 'monday_api_token': user.monday_api_token})
        return jsonify(access_token=access_token), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/auth/check', methods=['GET'])
@jwt_required()
def check():
    return jsonify({"message": "Authenticated"}), 200

def call_ai_api(prompt):
    client = anthropic.Anthropic(api_key="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")
    
    system_message = """
    You are an AI assistant that creates detailed Monday.com board structures based on user prompts.
    Your response MUST be a valid JSON object with the following structure:
    {
        "board": {
            "name": "Board name",
            "kind": "public/private/share",
            "description": "Board description"
        },
        "groups": [
            {
                "name": "Group name"
            }
        ],
        "columns": [
            {
                "title": "Column title",
                "type": "column_type",
                "description": "Column description"
            }
        ],
        "items": [
            {
                "name": "Item name",
                "group_id": "group_id",
                "column_values": {
                    "column_id": "value"
                },
                "subitems": [
                    {
                        "name": "Subitem name",
                        "column_values": {
                            "column_id": "value"
                        }
                    }
                ]
            }
        ]
    }
    Do not include any explanatory text outside of this JSON structure.
    """
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4000,
        temperature=0.7,
        system=system_message,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response = message.content[0].text
    print(f"AI Response: {response}")
    return response

async def create_board_async(api_key, json_data, workspace_id):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:3001/create_board', json={
            'apiKey': api_key,
            'boardData': json_data,
            'workspaceId': workspace_id
        }) as response:
            return await response.json()

def create_board(api_key, json_data, workspace_id):
    return asyncio.run(create_board_async(api_key, json_data, workspace_id))

@app.route('/process_prompt', methods=['POST'])
@jwt_required()
def process_prompt():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        prompt = data.get('prompt')
        workspace_id = data.get('workspace_id')

        if not prompt:
            return jsonify({"error": "Missing prompt or workspace ID"}), 400

        ai_response = call_ai_api(prompt)
        print(f"Raw AI response: {ai_response}")

        try:
            json_data = json.loads(ai_response)
        except json.JSONDecodeError as json_error:
            print(f"JSON Decode Error: {str(json_error)}")
            return jsonify({"error": f"Invalid AI response format: {str(json_error)}"}), 500

        response = create_board(current_user['monday_api_token'], json_data, workspace_id)
        return jsonify(response), 200
    except KeyError as e:
        return jsonify({"error": f"Missing key in response: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_items', methods=['GET'])
def get_items():
    api_key = request.headers.get('Authorization')
    board_id = request.headers.get('Board-ID')
    
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    query = f"""
    query {{
        boards (ids: {board_id}) {{
            items {{
                id
                name
                column_values {{
                    id
                    text
                }}
            }}
        }}
    }}
    """
    response = requests.post(url, json={'query': query}, headers=headers)
    return jsonify(response.json()), response.status_code

@app.route('/create_item', methods=['POST'])
def create_item():
    api_key = request.headers.get('Authorization')
    board_id = request.headers.get('Board-ID')
    data = request.get_json()
    
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    query = f"""
    mutation {{
        create_item (board_id: {board_id}, group_id: "topics", item_name: "{data['item_name']}", column_values: "{data['column_values']}") {{
            id
        }}
    }}
    """
    response = requests.post(url, json={'query': query}, headers=headers)
    return jsonify(response.json()), response.status_code

@app.route('/update_item', methods=['POST'])
def update_item():
    api_key = request.headers.get('Authorization')
    data = request.get_json()
    
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    query = f"""
    mutation {{
        change_column_value (item_id: {data['item_id']}, column_id: "{data['column_id']}", board_id: {data['board_id']}, value: "{data['value']}") {{
            id
        }}
    }}
    """
    response = requests.post(url, json={'query': query}, headers=headers)
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
