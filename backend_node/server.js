/**
 * Legal Compass — Node.js / Express Backend
 * ─────────────────────────────────────────
 * Phase 4: JWT auth + PostgreSQL (Neon.tech) + FastAPI proxy
 *
 * Endpoints:
 *   POST   /api/auth/register
 *   POST   /api/auth/login
 *   GET    /api/auth/me
 *   POST   /api/chat
 *   GET    /api/chat/history
 *   DELETE /api/chat/:id
 *   GET    /health
 */
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

import pool from './db/index.js';
import authRoutes from './routes/auth.js';
import chatRoutes from './routes/chat.js';

// ── Bootstrap ─────────────────────────────────────────────────
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname  = dirname(__filename);

const PORT         = parseInt(process.env.PORT || '3001', 10);
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';
const NODE_ENV     = process.env.NODE_ENV || 'development';

// ── Validate required env vars ────────────────────────────────
const REQUIRED_ENV = ['DATABASE_URL', 'JWT_SECRET'];
const missing = REQUIRED_ENV.filter(k => !process.env[k]);
if (missing.length > 0) {
    console.error(`\n[Server] FATAL: Missing required environment variables: ${missing.join(', ')}`);
    console.error('[Server] Copy .env.example to .env and fill in the values.\n');
    process.exit(1);
}

// ── Express app ───────────────────────────────────────────────
const app = express();

// Middleware
app.use(cors({
    origin: (origin, callback) => {
        // Allow: React dev (5173), Postman (no origin), production URL
        const allowed = [
            FRONTEND_URL,
            'http://localhost:5173',
            'http://localhost:3000',
        ];
        if (!origin || allowed.includes(origin)) return callback(null, true);
        return callback(new Error(`CORS blocked: ${origin}`));
    },
    credentials: true,
    methods: ['GET', 'POST', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
}));

app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// ── Routes ────────────────────────────────────────────────────
app.use('/api/auth', authRoutes);
app.use('/api/chat', chatRoutes);

// Health check — also shows Python API URL status
app.get('/health', (req, res) => {
    res.json({
        status:         'ok',
        service:        'Legal Compass Node Backend',
        environment:    NODE_ENV,
        python_api_url: process.env.PYTHON_API_URL
            ? `${process.env.PYTHON_API_URL.substring(0, 40)}...`
            : 'NOT CONFIGURED — set PYTHON_API_URL in .env',
        timestamp:      new Date().toISOString(),
    });
});

// ── 404 handler ───────────────────────────────────────────────
app.use((req, res) => {
    res.status(404).json({ error: `Route not found: ${req.method} ${req.path}` });
});

// ── Global error handler ──────────────────────────────────────
app.use((err, req, res, next) => {
    console.error('[Server] Unhandled error:', err.message);
    res.status(500).json({ error: 'An unexpected server error occurred.' });
});

// ── Database Init + Start ─────────────────────────────────────
async function initDatabase() {
    const schemaPath = join(__dirname, 'models', 'schema.sql');
    const schema = readFileSync(schemaPath, 'utf8');
    await pool.query(schema);
    console.log('[DB] Schema verified / tables created');
}

// ── Database Init + Start ─────────────────────────────────────
async function startServer() {
    console.log('\n' + '='.repeat(55));
    console.log('  Legal Compass — Node.js Backend');
    console.log('  Phase 4: JWT Auth + PostgreSQL/SQLite + FastAPI Proxy');
    console.log('='.repeat(55));

    // Warn if Python API URL is not set
    if (!process.env.PYTHON_API_URL || process.env.PYTHON_API_URL.includes('your-ngrok-url')) {
        console.warn('[Config] WARNING: PYTHON_API_URL not set to live ngrok URL — /api/chat will return 503 until configured');
    } else {
        console.log(`[Config] Python API → ${process.env.PYTHON_API_URL}`);
    }

    // Start listening
    app.listen(PORT, () => {
        console.log(`\n[Server] Running at http://localhost:${PORT}`);
        console.log(`[Server] Health check: http://localhost:${PORT}/health`);
        console.log(`[Server] Environment: ${NODE_ENV}`);
        console.log('='.repeat(55) + '\n');
    });
}

startServer();
