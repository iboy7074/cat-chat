# WhatsApp Clone

A real-time messaging web application with a choice of backend: **Node.js** or **Python**.

![WhatsApp Clone](https://img.shields.io/badge/WhatsApp-Clone-25d366?style=for-the-badge&logo=whatsapp&logoColor=white)

## Features

- **User Authentication** - Register and login with phone number and password
- **Real-time Messaging** - Instant message delivery using WebSockets
- **Online Status** - See when users are online (green dot indicator)
- **Message Indicators** - Sent (✓) and delivered (✓✓) status
- **Typing Indicator** - Shows when someone is typing
- **Search Chats** - Filter contacts by name
- **Responsive Design** - Works on desktop and mobile
- **Auto-reply** - Demo contacts respond automatically

## Quick Start

### Option 1: Python (Recommended)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python server.py
```

3. Open your browser:
```
http://localhost:3000
```

### Option 2: Node.js

1. Install dependencies:
```bash
npm install
```

2. Start the server:
```bash
npm start
```

3. Open your browser:
```
http://localhost:3000
```

## How to Test

### Single User (Demo)
1. Register a new account
2. Click on any contact (Alex, Sarah, etc.)
3. Send a message
4. Get auto-reply from the contact

### Multiple Users (Real-time)
1. Open `http://localhost:3000` in **two different browsers** (e.g., Chrome and Firefox)
2. Or use **incognito mode** for the second user
3. Register two different accounts
4. Message each other in real-time!

## Project Structure

```
├── index.html         # Frontend (HTML/CSS/JS)
├── server.py          # Python backend (Flask + SocketIO)
├── server.js          # Node.js backend (Express + Socket.io)
├── package.json       # Node.js dependencies
├── requirements.txt   # Python dependencies
├── data.json          # User data (created automatically)
└── README.md          # Documentation
```

## Tech Stack

### Python Version
| Layer | Technology |
|-------|------------|
| Backend | Flask, Flask-SocketIO |
| Real-time | python-socketio, eventlet |
| Storage | JSON file |

### Node.js Version
| Layer | Technology |
|-------|------------|
| Backend | Node.js, Express |
| Real-time | Socket.io |
| Storage | JSON file |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve the main app |
| POST | `/api/register` | Create new user account |
| POST | `/api/login` | Login with phone & password |
| GET | `/api/contacts/:phone` | Get user's contacts & messages |
| GET | `/api/users` | Get all registered users |

## Socket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `sendMessage` | Client → Server | Send a message |
| `newMessage` | Server → Client | Receive a message |
| `typing` | Both | Typing indicator |
| `userOnline` | Server → Client | User came online |
| `userOffline` | Server → Client | User went offline |

## Troubleshooting

**Port 3000 already in use?**
```bash
# Windows - Find and kill process
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F

# Mac/Linux
lsof -i :3000
kill -9 <PID>
```

**Python: Module not found?**
```bash
pip install -r requirements.txt
```

**Node.js: Command not found?**
- Install Node.js from https://nodejs.org/

**Can't connect to server?**
- Make sure the server is running
- Check if port 3000 is not blocked by firewall
- Try http://127.0.0.1:3000 instead

**Data not persisting?**
- Delete `data.json` and restart server to reset all data

## Screenshots

### Login/Register
- Clean, minimal design
- WhatsApp green theme
- Error handling for invalid inputs

### Chat List
- Contact avatars with online indicators
- Last message preview
- Timestamp of last message
- Search functionality

### Chat View
- Message bubbles (green=sent, white=received)
- Delivery status indicators
- Typing indicator
- Call buttons (decorative)

## License

Free to use for educational purposes.

---

Made with ❤️ - Supports both Python & Node.js
