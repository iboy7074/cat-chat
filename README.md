# WhatsApp Clone

A real-time messaging web application built with Node.js, Express, and Socket.io.

![WhatsApp Clone](https://img.shields.io/badge/WhatsApp-Clone-25d366?style=for-the-badge&logo=whatsapp&logoColor=white)

## Features

- **User Authentication** - Register and login with phone number and password
- **Real-time Messaging** - Instant message delivery using Socket.io
- **Online Status** - See when users are online (green dot indicator)
- **Message Indicators** - Sent (✓) and delivered (✓✓) status
- **Typing Indicator** - Shows when someone is typing
- **Search Chats** - Filter contacts by name
- **Responsive Design** - Works on desktop and mobile
- **Auto-reply** - Demo contacts respond automatically

## Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) (v14 or higher)

### Installation

1. Clone or download this project

2. Install dependencies:
```bash
npm install
```

3. Start the server:
```bash
npm start
```

4. Open your browser and go to:
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
├── index.html      # Frontend (HTML/CSS/JS)
├── server.js       # Backend server
├── package.json    # Dependencies
├── data.json       # User data (created automatically)
└── SPEC.md         # Project specification
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Node.js, Express |
| Real-time | Socket.io |
| Storage | JSON file |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Create new user account |
| POST | `/api/login` | Login with phone & password |
| GET | `/api/contacts/:phone` | Get user's contacts & messages |

## Socket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `sendMessage` | Client → Server | Send a message |
| `newMessage` | Server → Client | Receive a message |
| `typing` | Both | Typing indicator |
| `userOnline` | Server → Client | User came online |
| `userOffline` | Server → Client | User went offline |

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

## Troubleshooting

**Port 3000 already in use?**
```bash
# Find and kill the process
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F
```

**Can't connect to server?**
- Make sure the server is running (`npm start`)
- Check if port 3000 is not blocked by firewall

**Data not persisting?**
- Delete `data.json` and restart server to reset all data

## License

Free to use for educational purposes.

---

Made with ❤️ using Node.js + Socket.io
