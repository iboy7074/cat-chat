"""
WhatsApp Clone - Python Server
Flask backend with Flask-SocketIO for real-time messaging
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import json
import os
import random
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'whatsapp-clone-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

DATA_FILE = Path(__file__).parent / 'data.json'

DEFAULT_CONTACTS = [
    {"id": 1, "name": "Alex Johnson", "phone": "+12345678901", "online": False},
    {"id": 2, "name": "Sarah Miller", "phone": "+12345678902", "online": False},
    {"id": 3, "name": "Mike Davis", "phone": "+12345678903", "online": False},
    {"id": 4, "name": "Emily Brown", "phone": "+12345678904", "online": False},
    {"id": 5, "name": "Chris Wilson", "phone": "+12345678905", "online": False},
    {"id": 6, "name": "Jessica Taylor", "phone": "+12345678906", "online": False},
    {"id": 7, "name": "David Anderson", "phone": "+12345678907", "online": False},
    {"id": 8, "name": "Amanda Thomas", "phone": "+12345678908", "online": False}
]

AUTO_REPLIES = [
    "That's great!",
    "I see what you mean",
    "Haha, that's funny",
    "Tell me more!",
    "Really?",
    "That's interesting",
    "I agree with you",
    "Nice!",
    "Sounds good",
    "Let me think about it"
]

online_users = {}


def load_data():
    """Load data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}, "messages": {}}


def save_data(data):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


data = load_data()


@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')


@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    req_data = request.get_json()
    username = req_data.get('username', '').strip()
    phone = req_data.get('phone', '').strip()
    password = req_data.get('password', '')

    if not username or not phone or not password:
        return jsonify({"error": "Please fill in all fields"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if phone in data['users']:
        return jsonify({"error": "Phone number already registered"}), 400

    data['users'][phone] = {
        "username": username,
        "password": password,
        "createdAt": datetime.now().isoformat()
    }

    data['messages'][phone] = {}
    for contact in DEFAULT_CONTACTS:
        data['messages'][phone][contact['phone']] = []

    save_data(data)

    return jsonify({
        "success": True,
        "user": {"username": username, "phone": phone}
    })


@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    req_data = request.get_json()
    phone = req_data.get('phone', '').strip()
    password = req_data.get('password', '')

    if phone not in data['users'] or data['users'][phone]['password'] != password:
        return jsonify({"error": "Invalid phone number or password"}), 401

    return jsonify({
        "success": True,
        "user": {"username": data['users'][phone]['username'], "phone": phone}
    })


@app.route('/api/contacts/<phone>', methods=['GET'])
def get_contacts(phone):
    """Get user's contacts and messages"""
    if phone not in data['messages']:
        data['messages'][phone] = {}
        for contact in DEFAULT_CONTACTS:
            data['messages'][phone][contact['phone']] = []

    user_contacts = []
    for contact in DEFAULT_CONTACTS:
        messages = data['messages'].get(phone, {}).get(contact['phone'], [])
        user_contacts.append({
            **contact,
            "messages": messages
        })

    user_contacts.sort(key=lambda x: messages_sort_key(x['messages']), reverse=True)

    return jsonify(user_contacts)


@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all registered users"""
    users = [
        {"username": u['username'], "phone": phone}
        for phone, u in data['users'].items()
    ]
    return jsonify(users)


def messages_sort_key(messages):
    """Sort key for messages"""
    if messages:
        return messages[-1].get('time', 0)
    return 0


# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')


@socketio.on('register')
def handle_register(phone):
    """Register user as online"""
    online_users[phone] = request.sid
    socketio.emit('userOnline', phone, broadcast=True)
    print(f'User registered: {phone}')


@socketio.on('sendMessage')
def handle_send_message(message):
    """Handle sending a message"""
    from_phone = message.get('from')
    to_phone = message.get('to')
    text = message.get('text')
    timestamp = message.get('timestamp', int(datetime.now().timestamp() * 1000))

    if from_phone not in data['messages']:
        data['messages'][from_phone] = {}
    if to_phone not in data['messages']:
        data['messages'][to_phone] = {}
    if to_phone not in data['messages'][from_phone]:
        data['messages'][from_phone][to_phone] = []
    if from_phone not in data['messages'][to_phone]:
        data['messages'][to_phone][from_phone] = []

    msg_id = str(int(datetime.now().timestamp() * 1000))

    msg_data = {
        "id": msg_id,
        "text": text,
        "time": timestamp,
        "sent": True,
        "delivered": False
    }

    data['messages'][from_phone][to_phone].append(msg_data)

    received_msg = {**msg_data, "sent": False}
    data['messages'][to_phone][from_phone].append(received_msg)

    save_data(data)

    socketio.emit('messageDelivered', {
        "messageId": msg_id,
        "from": from_phone,
        "to": to_phone
    }, room=request.sid)

    recipient_sid = online_users.get(to_phone)
    if recipient_sid:
        socketio.emit('newMessage', received_msg, room=recipient_sid)
        socketio.emit('typing', {"phone": from_phone, "typing": False}, room=recipient_sid)

    def auto_deliver():
        msg_data['delivered'] = True
        save_data(data)
        socketio.emit('messageDelivered', {
            "messageId": msg_id,
            "from": from_phone,
            "to": to_phone
        }, room=request.sid)

        if recipient_sid:
            socketio.emit('messageUpdated', {
                "messageId": msg_id,
                "from": to_phone
            }, room=recipient_sid)

    def auto_reply():
        reply = {
            "id": str(int(datetime.now().timestamp() * 1000)),
            "text": random.choice(AUTO_REPLIES),
            "time": int(datetime.now().timestamp() * 1000),
            "sent": False,
            "delivered": False
        }

        if to_phone not in data['messages']:
            data['messages'][to_phone] = {}
        if from_phone not in data['messages'][to_phone]:
            data['messages'][to_phone][from_phone] = []

        data['messages'][to_phone][from_phone].append(reply)
        save_data(data)

        sender_sid = online_users.get(from_phone)
        if sender_sid:
            socketio.emit('typing', {"phone": to_phone, "typing": False}, room=sender_sid)
            socketio.emit('newMessage', reply, room=sender_sid)

        if recipient_sid:
            socketio.emit('newMessage', reply, room=recipient_sid)

    from threading import Timer
    Timer(1.0, auto_deliver).start()
    Timer(2.0 + random.random() * 2.0, auto_reply).start()


@socketio.on('typing')
def handle_typing(data_):
    """Handle typing indicator"""
    to_phone = data_.get('to')
    typing = data_.get('typing', False)

    recipient_sid = online_users.get(to_phone)
    if recipient_sid:
        socketio.emit('typing', {"phone": list(online_users.keys())[list(online_users.values()).index(request.sid)] if request.sid in online_users.values() else None, "typing": typing}, room=recipient_sid)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    phone_to_remove = None
    for phone, sid in online_users.items():
        if sid == request.sid:
            phone_to_remove = phone
            break

    if phone_to_remove:
        del online_users[phone_to_remove]
        socketio.emit('userOffline', phone_to_remove, broadcast=True)
        print(f'User disconnected: {phone_to_remove}')

    print(f'Client disconnected: {request.sid}')


if __name__ == '__main__':
    print("=" * 50)
    print("  WhatsApp Clone - Python Server")
    print("  Running at: http://localhost:3000")
    print("=" * 50)
    socketio.run(app, host='0.0.0.0', port=3000, debug=True)
