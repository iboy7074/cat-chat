import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const server = createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

const DATA_FILE = join(__dirname, 'data.json');

function loadData() {
    if (fs.existsSync(DATA_FILE)) {
        return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
    }
    return {
        users: {},
        messages: {}
    };
}

function saveData(data) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

const defaultContacts = [
    { id: 1, name: 'Alex Johnson', phone: '+12345678901', online: false },
    { id: 2, name: 'Sarah Miller', phone: '+12345678902', online: false },
    { id: 3, name: 'Mike Davis', phone: '+12345678903', online: false },
    { id: 4, name: 'Emily Brown', phone: '+12345678904', online: false },
    { id: 5, name: 'Chris Wilson', phone: '+12345678905', online: false },
    { id: 6, name: 'Jessica Taylor', phone: '+12345678906', online: false },
    { id: 7, name: 'David Anderson', phone: '+12345678907', online: false },
    { id: 8, name: 'Amanda Thomas', phone: '+12345678908', online: false }
];

const autoReplies = [
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
];

let data = loadData();
let onlineUsers = new Map();

app.post('/api/register', (req, res) => {
    const { username, phone, password } = req.body;
    
    if (!username || !phone || !password) {
        return res.status(400).json({ error: 'Please fill in all fields' });
    }
    
    if (data.users[phone]) {
        return res.status(400).json({ error: 'Phone number already registered' });
    }
    
    data.users[phone] = {
        username,
        password,
        createdAt: Date.now()
    };
    
    data.messages[phone] = {};
    defaultContacts.forEach(contact => {
        data.messages[phone][contact.phone] = [];
    });
    
    saveData(data);
    res.json({ success: true, user: { username, phone } });
});

app.post('/api/login', (req, res) => {
    const { phone, password } = req.body;
    
    if (!data.users[phone] || data.users[phone].password !== password) {
        return res.status(401).json({ error: 'Invalid phone number or password' });
    }
    
    res.json({
        success: true,
        user: { username: data.users[phone].username, phone }
    });
});

app.get('/api/contacts/:phone', (req, res) => {
    const { phone } = req.params;
    const userContacts = defaultContacts.map(contact => {
        const messages = data.messages[phone]?.[contact.phone] || [];
        const lastMessage = messages.length > 0 ? messages[messages.length - 1] : null;
        return {
            ...contact,
            messages
        };
    });
    
    userContacts.sort((a, b) => {
        const aLast = a.messages.length > 0 ? a.messages[a.messages.length - 1].time : 0;
        const bLast = b.messages.length > 0 ? b.messages[b.messages.length - 1].time : 0;
        return bLast - aLast;
    });
    
    res.json(userContacts);
});

app.get('/api/users', (req, res) => {
    const users = Object.values(data.users).map(u => ({
        username: u.username,
        phone: u.phone
    }));
    res.json(users);
});

io.on('connection', (socket) => {
    console.log('User connected:', socket.id);
    
    socket.on('register', (phone) => {
        onlineUsers.set(phone, socket.id);
        socket.phone = phone;
        io.emit('userOnline', phone);
        console.log('User registered:', phone);
    });
    
    socket.on('sendMessage', (message) => {
        const { from, to, text, timestamp } = message;
        
        if (!data.messages[from]) {
            data.messages[from] = {};
        }
        if (!data.messages[from][to]) {
            data.messages[from][to] = [];
        }
        if (!data.messages[to]) {
            data.messages[to] = {};
        }
        if (!data.messages[to][from]) {
            data.messages[to][from] = [];
        }
        
        const msgData = {
            id: Date.now().toString(),
            text,
            time: timestamp || Date.now(),
            sent: true,
            delivered: false
        };
        
        data.messages[from][to].push(msgData);
        data.messages[to][from].push({ ...msgData, sent: false });
        
        saveData(data);
        
        socket.emit('messageDelivered', { messageId: msgData.id, from, to });
        
        const recipientSocketId = onlineUsers.get(to);
        if (recipientSocketId) {
            io.to(recipientSocketId).emit('newMessage', {
                ...msgData,
                sent: false
            }, from);
        }
        
        setTimeout(() => {
            msgData.delivered = true;
            saveData(data);
            socket.emit('messageDelivered', { messageId: msgData.id, from, to });
            
            if (recipientSocketId) {
                io.to(recipientSocketId).emit('messageUpdated', { messageId: msgData.id, from });
            }
        }, 1000);
        
        setTimeout(() => {
            const recipientSocketId = onlineUsers.get(to);
            const isOnline = recipientSocketId && onlineUsers.has(to);
            
            const reply = {
                id: Date.now().toString(),
                text: autoReplies[Math.floor(Math.random() * autoReplies.length)],
                time: Date.now(),
                sent: false,
                delivered: false
            };
            
            if (!data.messages[to]) data.messages[to] = {};
            if (!data.messages[to][from]) data.messages[to][from] = [];
            data.messages[to][from].push(reply);
            saveData(data);
            
            const senderSocketId = onlineUsers.get(from);
            if (senderSocketId) {
                io.to(senderSocketId).emit('typing', { phone: to, typing: false });
                io.to(senderSocketId).emit('newMessage', reply, to);
            }
            
            if (recipientSocketId) {
                const contact = defaultContacts.find(c => c.phone === from);
                io.to(recipientSocketId).emit('newMessage', reply, from);
            }
        }, 2000 + Math.random() * 2000);
    });
    
    socket.on('typing', ({ to, typing }) => {
        const recipientSocketId = onlineUsers.get(to);
        if (recipientSocketId) {
            io.to(recipientSocketId).emit('typing', { phone: socket.phone, typing });
        }
    });
    
    socket.on('disconnect', () => {
        if (socket.phone) {
            onlineUsers.delete(socket.phone);
            io.emit('userOffline', socket.phone);
            console.log('User disconnected:', socket.phone);
        }
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
