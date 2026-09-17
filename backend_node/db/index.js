/**
 * Legal Compass — Database Abstraction Layer
 * Supports PostgreSQL (Neon.tech / Render Postgres) with automatic local/cloud fallback.
 * If DATABASE_URL is unconfigured, falls back to SQLite or pure-JS JSON store.
 * Zero native crash guarantee across all Linux environments (including Render GLIBC 2.35).
 */
import pg from 'pg';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import jsonStore from './jsonStore.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);

let mode = 'pg'; // 'pg' | 'sqlite' | 'json'
let pgPool = null;
let sqliteDb = null;
let dbInitialized = false;

// Determine if DATABASE_URL is a placeholder
const isPlaceholder = (url) => {
    if (!url) return true;
    return url.includes('username:password') || url.includes('ep-xxxx-xxxx');
};

async function initDb() {
    if (dbInitialized) return;
    const dbUrl = process.env.DATABASE_URL;

    // 1. Try PostgreSQL if DATABASE_URL is configured
    if (!isPlaceholder(dbUrl)) {
        try {
            console.log('[DB] Attempting PostgreSQL connection…');
            pgPool = new pg.Pool({
                connectionString: dbUrl,
                ssl: { rejectUnauthorized: false },
                connectionTimeoutMillis: 5000,
            });
            const client = await pgPool.connect();
            client.release();
            mode = 'pg';
            dbInitialized = true;
            console.log('[DB] Connected to PostgreSQL ✓');
            return;
        } catch (err) {
            console.warn('[DB] PostgreSQL connection failed:', err.message);
            console.warn('[DB] Falling back to file-based store…');
        }
    } else {
        console.log('[DB] No production DATABASE_URL provided. Initializing file-based store…');
    }

    // 2. Try native SQLite dynamically (if binary is compatible with host GLIBC)
    try {
        const sqlite3Module = await import('sqlite3');
        const sqlite3 = sqlite3Module.default || sqlite3Module;
        const sqlitePath = path.join(__dirname, '..', 'legal_compass_node.db');
        sqliteDb = new sqlite3.Database(sqlitePath);
        mode = 'sqlite';
        console.log(`[DB] Connected to local SQLite: ${sqlitePath} ✓`);

        await runSqlite(`
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        `);
        await runSqlite(`
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources TEXT DEFAULT '[]',
                response_time REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        `);
        dbInitialized = true;
        return;
    } catch (sqliteErr) {
        console.warn(`[DB] Native SQLite unavailable on this host (${sqliteErr.message}).`);
        console.log('[DB] Seamlessly using pure JavaScript persistent JSON store (legal_compass_node.json) ✓');
        mode = 'json';
        dbInitialized = true;
    }
}

function runSqlite(sql, params = []) {
    return new Promise((resolve, reject) => {
        if (!sqliteDb) return reject(new Error('SQLite not initialized'));
        sqliteDb.run(sql, params, function (err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

function allSqlite(sql, params = []) {
    return new Promise((resolve, reject) => {
        if (!sqliteDb) return reject(new Error('SQLite not initialized'));
        sqliteDb.all(sql, params, (err, rows) => {
            if (err) return reject(err);
            resolve(rows);
        });
    });
}

// Universal query interface supporting PG, SQLite, and pure JS JSON store
const query = async (text, params = []) => {
    if (!dbInitialized) {
        await initDb();
    }

    if (mode === 'pg') {
        return await pgPool.query(text, params);
    }

    if (mode === 'json') {
        return await jsonStore.query(text, params);
    }

    // SQLite execution
    let sqliteText = text.replace(/\$\d+/g, '?');
    const hasReturning = /RETURNING\s+/i.test(sqliteText);
    const isInsert = /INSERT\s+INTO\s+(\w+)/i.exec(sqliteText);

    if (hasReturning) {
        sqliteText = sqliteText.replace(/RETURNING\s+.*$/i, '').trim();
    }

    if (/^\s*SELECT/i.test(sqliteText)) {
        const rows = await allSqlite(sqliteText, params);
        rows.forEach(r => {
            if (typeof r.sources === 'string') {
                try { r.sources = JSON.parse(r.sources); } catch {}
            }
        });
        return { rows, rowCount: rows.length };
    }

    if (/^\s*INSERT/i.test(sqliteText)) {
        const res = await runSqlite(sqliteText, params);
        const tableName = isInsert ? isInsert[1] : 'users';
        const rows = await allSqlite(`SELECT * FROM ${tableName} WHERE id = ?`, [res.lastID]);
        return { rows, rowCount: 1 };
    }

    if (/^\s*DELETE/i.test(sqliteText)) {
        const res = await runSqlite(sqliteText, params);
        return { rows: res.changes ? [{ id: params[0] }] : [], rowCount: res.changes };
    }

    const res = await runSqlite(sqliteText, params);
    return { rows: [], rowCount: res.changes };
};

// Initialize DB on import asynchronously
initDb().catch(err => console.error('[DB] Init error:', err));

export default { query };
