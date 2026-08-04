/**
 * Legal Compass — Database Abstraction Layer
 * Supports PostgreSQL (Neon.tech) with automatic SQLite local fallback.
 * If DATABASE_URL is unconfigured or PG connection fails, falls back to SQLite seamlessly.
 */
import pg from 'pg';
import sqlite3 from 'sqlite3';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);

let mode = 'pg'; // 'pg' or 'sqlite'
let pgPool = null;
let sqliteDb = null;

// Determine if DATABASE_URL is a placeholder
const isPlaceholder = (url) => {
    if (!url) return true;
    return url.includes('username:password') || url.includes('ep-xxxx-xxxx');
};

async function initDb() {
    const dbUrl = process.env.DATABASE_URL;

    if (!isPlaceholder(dbUrl)) {
        try {
            console.log('[DB] Attempting PostgreSQL connection (Neon.tech)…');
            pgPool = new pg.Pool({
                connectionString: dbUrl,
                ssl: { rejectUnauthorized: false },
                connectionTimeoutMillis: 4000,
            });
            // Test connection
            const client = await pgPool.connect();
            client.release();
            mode = 'pg';
            console.log('[DB] Connected to PostgreSQL (Neon.tech) ✓');
            return;
        } catch (err) {
            console.warn('[DB] PostgreSQL connection failed:', err.message);
            console.warn('[DB] Falling back to local SQLite database…');
        }
    } else {
        console.log('[DB] No production DATABASE_URL provided. Using local SQLite database…');
    }

    // SQLite fallback
    mode = 'sqlite';
    const sqlitePath = path.join(__dirname, '..', 'legal_compass_node.db');
    sqliteDb = new sqlite3.Database(sqlitePath);
    console.log(`[DB] Connected to local SQLite: ${sqlitePath} ✓`);

    // Create tables in SQLite if they don't exist
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
}

function runSqlite(sql, params = []) {
    return new Promise((resolve, reject) => {
        sqliteDb.run(sql, params, function (err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

function allSqlite(sql, params = []) {
    return new Promise((resolve, reject) => {
        sqliteDb.all(sql, params, (err, rows) => {
            if (err) return reject(err);
            resolve(rows);
        });
    });
}

// Universal query interface supporting both PG ($1, $2) and SQLite (?)
const query = async (text, params = []) => {
    if (!sqliteDb && mode === 'sqlite') {
        await initDb();
    }

    if (mode === 'pg') {
        return await pgPool.query(text, params);
    }

    // SQLite execution
    // Convert PG parameter markers ($1, $2) to SQLite markers (?)
    let sqliteText = text.replace(/\$\d+/g, '?');

    // Handle RETURNING clause for SQLite
    const hasReturning = /RETURNING\s+/i.test(sqliteText);
    const isInsert = /INSERT\s+INTO\s+(\w+)/i.exec(sqliteText);

    if (hasReturning) {
        sqliteText = sqliteText.replace(/RETURNING\s+.*$/i, '').trim();
    }

    if (/^\s*SELECT/i.test(sqliteText)) {
        const rows = await allSqlite(sqliteText, params);
        // Format JSONB parsing if sources exist
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

// Initialize DB on import
initDb().catch(err => console.error('[DB] Init error:', err));

export default { query };
