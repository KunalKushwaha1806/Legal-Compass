/**
 * Legal Compass — Chat Routes
 *
 * POST   /api/chat          — proxy question to FastAPI or local NLP engine (JWT required)
 * GET    /api/chat/history  — get user's past Q&A (JWT required)
 * DELETE /api/chat/:id      — delete a specific chat (JWT required)
 */
import express from 'express';
import axios from 'axios';
import { execFile } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import authenticate from '../middleware/auth.js';
import pool from '../db/index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);
const rootDir    = path.join(__dirname, '..', '..');

const router = express.Router();

/** Local Python NLP engine fallback */
function queryLocalEngine(question) {
    return new Promise((resolve, reject) => {
        const pyCode = `import sys, json, nlp_engine; sys.stdout.reconfigure(encoding='utf-8'); engine = nlp_engine.LegalNLPEngine(); print(json.dumps(engine.answer(${JSON.stringify(question)})))`;
        execFile('python', ['-c', pyCode], { cwd: rootDir, encoding: 'utf8' }, (err, stdout) => {
            if (err) return reject(err);
            try {
                const lines = stdout.trim().split('\n');
                const jsonLine = lines.find(l => l.trim().startsWith('{'));
                if (!jsonLine) return reject(new Error('No JSON from local NLP engine'));
                resolve(JSON.parse(jsonLine));
            } catch (pErr) {
                reject(pErr);
            }
        });
    });
}

// ── POST /api/chat ────────────────────────────────────────────
router.post('/', authenticate, async (req, res) => {
    const { question } = req.body;
    const userId = req.user.userId;

    if (!question?.trim()) {
        return res.status(400).json({ error: 'Question is required.' });
    }
    if (question.trim().length > 1000) {
        return res.status(400).json({ error: 'Question must be under 1000 characters.' });
    }

    const pythonApiUrl = process.env.PYTHON_API_URL?.trim().replace(/\/$/, '');
    const isPlaceholder = !pythonApiUrl || pythonApiUrl.includes('your-ngrok-url');

    let answer, category = 'general', sources = [], response_time = null;
    const startTime = Date.now();

    let success = false;

    // Try FastAPI via ngrok if configured
    if (!isPlaceholder) {
        try {
            console.log(`[Chat] Querying FastAPI: ${pythonApiUrl}...`);
            const pyRes = await axios.post(
                `${pythonApiUrl}/api/chat`,
                { question: question.trim() },
                { timeout: 90_000, headers: { 'Content-Type': 'application/json' } }
            );

            response_time = parseFloat(((Date.now() - startTime) / 1000).toFixed(3));
            answer        = pyRes.data.answer;
            category      = pyRes.data.category || 'general';
            sources       = pyRes.data.sources || [];
            response_time = pyRes.data.response_time ?? response_time;
            success       = true;
            console.log(`[Chat] FastAPI success | time=${response_time}s`);
        } catch (err) {
            console.warn(`[Chat] FastAPI failed (${err.message}). Falling back to local NLP engine...`);
        }
    }

    // Fallback to local Python NLP engine
    if (!success) {
        try {
            console.log(`[Chat] Querying local NLP engine for: "${question.trim()}"`);
            const result  = await queryLocalEngine(question.trim());
            response_time = parseFloat(((Date.now() - startTime) / 1000).toFixed(3));
            answer        = result.answer;
            category      = result.category || 'general';
            sources       = result.sources || [];
            success       = true;
            console.log(`[Chat] Local NLP engine success | time=${response_time}s`);
        } catch (localErr) {
            console.error('[Chat] Local NLP engine error:', localErr.message);
            return res.status(500).json({
                error: 'Failed to process legal question. Check Python environment and nlp_engine.py.',
            });
        }
    }

    // Persist Q&A to database (PostgreSQL or SQLite fallback)
    try {
        const result = await pool.query(
            `INSERT INTO chats (user_id, question, answer, sources, response_time)
             VALUES ($1, $2, $3, $4, $5)
             RETURNING id, created_at`,
            [userId, question.trim(), answer, JSON.stringify(sources), response_time]
        );

        const chat = result.rows[0];

        return res.status(200).json({
            id:            chat ? chat.id : Date.now(),
            question:      question.trim(),
            answer,
            category,
            sources,
            response_time,
            created_at:    chat ? chat.created_at : new Date().toISOString(),
        });
    } catch (dbErr) {
        console.error('[Chat] DB save error:', dbErr.message);
        return res.status(200).json({
            id:            Date.now(),
            question:      question.trim(),
            answer,
            category,
            sources,
            response_time,
            created_at:    new Date().toISOString(),
        });
    }
});

// ── GET /api/chat/history ─────────────────────────────────────
router.get('/history', authenticate, async (req, res) => {
    const userId = req.user.userId;
    const page   = Math.max(1, parseInt(req.query.page)  || 1);
    const limit  = Math.min(50, parseInt(req.query.limit) || 20);
    const offset = (page - 1) * limit;

    try {
        const [rows, countRow] = await Promise.all([
            pool.query(
                `SELECT id, question, answer, sources, response_time, created_at
                 FROM chats
                 WHERE user_id = $1
                 ORDER BY created_at DESC
                 LIMIT $2 OFFSET $3`,
                [userId, limit, offset]
            ),
            pool.query('SELECT COUNT(*) FROM chats WHERE user_id = $1', [userId]),
        ]);

        const total = parseInt(countRow?.rows?.[0]?.count || 0, 10);

        return res.json({
            chats: rows.rows || [],
            pagination: {
                page,
                limit,
                total,
                pages: Math.ceil(total / limit) || 1,
                has_next: page < Math.ceil(total / limit),
                has_prev: page > 1,
            },
        });
    } catch (err) {
        console.error('[Chat] History error:', err.message);
        return res.status(500).json({ error: 'Server error fetching chat history.' });
    }
});

// ── DELETE /api/chat/:id ──────────────────────────────────────
router.delete('/:id', authenticate, async (req, res) => {
    const chatId = parseInt(req.params.id, 10);
    const userId = req.user.userId;

    if (isNaN(chatId)) {
        return res.status(400).json({ error: 'Invalid chat ID.' });
    }

    try {
        const result = await pool.query(
            'DELETE FROM chats WHERE id = $1 AND user_id = $2 RETURNING id',
            [chatId, userId]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Chat not found or permission denied.' });
        }

        return res.json({ message: 'Chat deleted successfully.', id: chatId });
    } catch (err) {
        console.error('[Chat] Delete error:', err.message);
        return res.status(500).json({ error: 'Server error deleting chat.' });
    }
});

export default router;
