/**
 * Legal Compass — Auth Routes
 *
 * POST /api/auth/register  — create account
 * POST /api/auth/login     — get JWT token
 * GET  /api/auth/me        — get current user (protected)
 */
import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import pool from '../db/index.js';
import authenticate from '../middleware/auth.js';

const router = express.Router();

// ── Helpers ───────────────────────────────────────────────────

/** Sign a 7-day JWT for the given user */
function signToken(user) {
    return jwt.sign(
        { userId: user.id, email: user.email, name: user.name },
        process.env.JWT_SECRET,
        { expiresIn: '7d' }
    );
}

/** Simple email format check */
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ── POST /api/auth/register ───────────────────────────────────
router.post('/register', async (req, res) => {
    const { name, email, password } = req.body;

    // Validation
    if (!name?.trim() || !email?.trim() || !password) {
        return res.status(400).json({ error: 'Name, email, and password are required.' });
    }
    if (!isValidEmail(email)) {
        return res.status(400).json({ error: 'Please provide a valid email address.' });
    }
    if (password.length < 6) {
        return res.status(400).json({ error: 'Password must be at least 6 characters.' });
    }
    if (name.trim().length < 2) {
        return res.status(400).json({ error: 'Name must be at least 2 characters.' });
    }

    try {
        // Check for existing account
        const existing = await pool.query(
            'SELECT id FROM users WHERE email = $1',
            [email.toLowerCase().trim()]
        );
        if (existing.rows.length > 0) {
            return res.status(409).json({ error: 'An account with this email already exists.' });
        }

        // Hash password (salt rounds = 12)
        const passwordHash = await bcrypt.hash(password, 12);

        // Insert user
        const result = await pool.query(
            `INSERT INTO users (name, email, password)
             VALUES ($1, $2, $3)
             RETURNING id, name, email, created_at`,
            [name.trim(), email.toLowerCase().trim(), passwordHash]
        );

        const user = result.rows[0];
        const token = signToken(user);

        console.log(`[Auth] New user registered: ${user.email}`);

        return res.status(201).json({
            message: 'Account created successfully.',
            token,
            user: { id: user.id, name: user.name, email: user.email },
        });
    } catch (err) {
        console.error('[Auth] Register error:', err.message);
        return res.status(500).json({ error: 'Server error during registration. Please try again.' });
    }
});

// ── POST /api/auth/login ──────────────────────────────────────
router.post('/login', async (req, res) => {
    const { email, password } = req.body;

    if (!email?.trim() || !password) {
        return res.status(400).json({ error: 'Email and password are required.' });
    }

    try {
        const result = await pool.query(
            'SELECT id, name, email, password FROM users WHERE email = $1',
            [email.toLowerCase().trim()]
        );

        if (result.rows.length === 0) {
            // Deliberate vague message to prevent email enumeration
            return res.status(401).json({ error: 'Invalid email or password.' });
        }

        const user = result.rows[0];

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(401).json({ error: 'Invalid email or password.' });
        }

        const token = signToken(user);

        console.log(`[Auth] User logged in: ${user.email}`);

        return res.json({
            message: 'Login successful.',
            token,
            user: { id: user.id, name: user.name, email: user.email },
        });
    } catch (err) {
        console.error('[Auth] Login error:', err.message);
        return res.status(500).json({ error: 'Server error during login. Please try again.' });
    }
});

// ── GET /api/auth/me ─────────────────────────────────────────
router.get('/me', authenticate, async (req, res) => {
    try {
        const result = await pool.query(
            'SELECT id, name, email, created_at FROM users WHERE id = $1',
            [req.user.userId]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'User not found.' });
        }

        return res.json({ user: result.rows[0] });
    } catch (err) {
        console.error('[Auth] Me error:', err.message);
        return res.status(500).json({ error: 'Server error.' });
    }
});

export default router;
