/**
 * Legal Compass — Pure JavaScript Database Store
 * ──────────────────────────────────────────────
 * Zero native C++ dependencies, zero GLIBC requirements.
 * Works seamlessly on any Linux environment (Render, Railway, Ubuntu, Alpine, Docker).
 * Persists users and chat history in legal_compass_node.json.
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);
const DB_FILE    = path.join(__dirname, '..', 'legal_compass_node.json');

let dbData = { users: [], chats: [] };

function loadDb() {
  try {
    if (fs.existsSync(DB_FILE)) {
      const raw = fs.readFileSync(DB_FILE, 'utf8');
      dbData = JSON.parse(raw);
      if (!Array.isArray(dbData.users)) dbData.users = [];
      if (!Array.isArray(dbData.chats)) dbData.chats = [];
    } else {
      saveDb();
    }
  } catch (err) {
    console.warn('[JSON DB] Warning loading database file, initializing clean store:', err.message);
    dbData = { users: [], chats: [] };
  }
}

function saveDb() {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(dbData, null, 2), 'utf8');
  } catch (err) {
    console.error('[JSON DB] Error writing to file:', err.message);
  }
}

loadDb();

/**
 * Universal query interface matching PostgreSQL / SQLite signature
 */
export async function query(text, params = []) {
  const sql = text.trim();

  // 1. SELECT user by email
  if (/SELECT.*FROM\s+users\s+WHERE\s+email\s*=\s*/i.test(sql)) {
    const email = String(params[0] || '').toLowerCase().trim();
    const user = dbData.users.find(u => u.email.toLowerCase().trim() === email);
    if (!user) return { rows: [], rowCount: 0 };
    return {
      rows: [{
        id: user.id,
        name: user.name,
        email: user.email,
        password: user.password,
        created_at: user.created_at
      }],
      rowCount: 1
    };
  }

  // 2. SELECT user by id
  if (/SELECT.*FROM\s+users\s+WHERE\s+id\s*=\s*/i.test(sql)) {
    const userId = Number(params[0]);
    const user = dbData.users.find(u => u.id === userId);
    if (!user) return { rows: [], rowCount: 0 };
    return {
      rows: [{
        id: user.id,
        name: user.name,
        email: user.email,
        created_at: user.created_at
      }],
      rowCount: 1
    };
  }

  // 3. INSERT user
  if (/INSERT\s+INTO\s+users/i.test(sql)) {
    const [name, email, password] = params;
    const nextId = dbData.users.length > 0
      ? Math.max(...dbData.users.map(u => u.id || 0)) + 1
      : 1;

    const newUser = {
      id: nextId,
      name: String(name).trim(),
      email: String(email).toLowerCase().trim(),
      password: String(password),
      created_at: new Date().toISOString()
    };

    dbData.users.push(newUser);
    saveDb();

    return {
      rows: [{
        id: newUser.id,
        name: newUser.name,
        email: newUser.email,
        created_at: newUser.created_at
      }],
      rowCount: 1
    };
  }

  // 4. INSERT chat
  if (/INSERT\s+INTO\s+chats/i.test(sql)) {
    const [userId, question, answer, sourcesRaw, responseTime] = params;
    const nextId = dbData.chats.length > 0
      ? Math.max(...dbData.chats.map(c => c.id || 0)) + 1
      : 1;

    let sources = [];
    if (typeof sourcesRaw === 'string') {
      try { sources = JSON.parse(sourcesRaw); } catch { sources = []; }
    } else if (Array.isArray(sourcesRaw)) {
      sources = sourcesRaw;
    }

    const newChat = {
      id: nextId,
      user_id: Number(userId),
      question: String(question),
      answer: String(answer),
      sources,
      response_time: responseTime ?? null,
      created_at: new Date().toISOString()
    };

    dbData.chats.push(newChat);
    saveDb();

    return {
      rows: [{
        id: newChat.id,
        created_at: newChat.created_at
      }],
      rowCount: 1
    };
  }

  // 5. COUNT chats for user
  if (/SELECT\s+COUNT\(\*\)\s+FROM\s+chats\s+WHERE\s+user_id\s*=\s*/i.test(sql)) {
    const userId = Number(params[0]);
    const count = dbData.chats.filter(c => c.user_id === userId).length;
    return {
      rows: [{ count: String(count) }],
      rowCount: 1
    };
  }

  // 6. SELECT chat history for user
  if (/SELECT.*FROM\s+chats\s+WHERE\s+user_id\s*=\s*/i.test(sql)) {
    const userId = Number(params[0]);
    const limit  = Number(params[1] || 20);
    const offset = Number(params[2] || 0);

    const userChats = dbData.chats
      .filter(c => c.user_id === userId)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(offset, offset + limit);

    return {
      rows: userChats,
      rowCount: userChats.length
    };
  }

  // 7. DELETE chat by id and user_id
  if (/DELETE\s+FROM\s+chats\s+WHERE/i.test(sql)) {
    const chatId = Number(params[0]);
    const userId = Number(params[1]);

    const idx = dbData.chats.findIndex(c => c.id === chatId && c.user_id === userId);
    if (idx !== -1) {
      dbData.chats.splice(idx, 1);
      saveDb();
      return { rows: [{ id: chatId }], rowCount: 1 };
    }
    return { rows: [], rowCount: 0 };
  }

  return { rows: [], rowCount: 0 };
}

export default { query };
