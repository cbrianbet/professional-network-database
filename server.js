const express = require('express');
const path = require('path');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');
const cors = require('cors');
require('dotenv').config();

const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'please-change-this-secret';
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || '';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || '';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL ? { rejectUnauthorized: false } : false,
});

async function initDatabase() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'user',
      status TEXT NOT NULL DEFAULT 'active',
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
  `);

  await pool.query(`
    CREATE TABLE IF NOT EXISTS profiles (
      id SERIAL PRIMARY KEY,
      user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
      full_name TEXT NOT NULL,
      email TEXT NOT NULL,
      headline TEXT,
      location TEXT,
      skills TEXT[],
      summary TEXT,
      status TEXT NOT NULL DEFAULT 'pending',
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
  `);

  await pool.query(`
    CREATE TABLE IF NOT EXISTS members (
      id SERIAL PRIMARY KEY,
      user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
      name TEXT NOT NULL,
      phone TEXT NOT NULL,
      email TEXT NOT NULL,
      age INTEGER NOT NULL,
      national_id TEXT NOT NULL,
      sub_location TEXT,
      education TEXT,
      form_four_year INTEGER,
      kcse TEXT,
      institution TEXT,
      course TEXT,
      graduation INTEGER,
      status TEXT NOT NULL,
      employer TEXT,
      career TEXT,
      skills TEXT[],
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
  `);


  if (ADMIN_EMAIL && ADMIN_PASSWORD) {
    const result = await pool.query('SELECT id FROM users WHERE email = $1', [ADMIN_EMAIL.toLowerCase()]);
    if (result.rowCount === 0) {
      const hash = await bcrypt.hash(ADMIN_PASSWORD, 12);
      await pool.query(
        'INSERT INTO users (name, email, password_hash, role, status) VALUES ($1, $2, $3, $4, $5)',
        ['Administrator', ADMIN_EMAIL.toLowerCase(), hash, 'admin', 'active']
      );
      console.log('Created initial admin user:', ADMIN_EMAIL);
    }
  }
}

function generateToken(user) {
  return jwt.sign(
    {
      id: user.id,
      email: user.email,
      role: user.role,
      status: user.status,
    },
    JWT_SECRET,
    { expiresIn: '7d' }
  );
}

function authMiddleware(req, res, next) {
  const auth = req.headers.authorization || '';
  const token = auth.startsWith('Bearer ') ? auth.slice(7) : null;
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  try {
    req.user = jwt.verify(token, JWT_SECRET);
    return next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}

function adminOnly(req, res, next) {
  if (!req.user || req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Admin access required' });
  }
  next();
}

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'pages')));

app.get('/api/auth/me', authMiddleware, async (req, res) => {
  const result = await pool.query('SELECT id, name, email, role, status, created_at FROM users WHERE id = $1', [req.user.id]);
  if (!result.rowCount) return res.status(404).json({ error: 'User not found' });
  res.json({ user: result.rows[0] });
});

app.post('/api/auth/signup', async (req, res) => {
  try {
    const { name, email, password } = req.body || {};
    if (!name || !email || !password) {
      return res.status(400).json({ error: 'Name, email, and password are required' });
    }
    const cleanEmail = email.toLowerCase();
    const existing = await pool.query('SELECT id FROM users WHERE email = $1', [cleanEmail]);
    if (existing.rowCount) {
      return res.status(409).json({ error: 'Email is already registered' });
    }
    const password_hash = await bcrypt.hash(password, 12);
    const result = await pool.query(
      'INSERT INTO users (name, email, password_hash, role, status) VALUES ($1, $2, $3, $4, $5) RETURNING id, name, email, role, status',
      [name.trim(), cleanEmail, password_hash, 'user', 'active']
    );
    const user = result.rows[0];
    const token = generateToken(user);
    res.json({ token, user });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to create account' });
  }
});

app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body || {};
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }
    const cleanEmail = email.toLowerCase();
    const result = await pool.query('SELECT id, name, email, password_hash, role, status FROM users WHERE email = $1', [cleanEmail]);
    if (!result.rowCount) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    const user = result.rows[0];
    const valid = await bcrypt.compare(password, user.password_hash);
    if (!valid) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    const token = generateToken(user);
    res.json({ token, user: { id: user.id, name: user.name, email: user.email, role: user.role, status: user.status } });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Login failed' });
  }
});

app.get('/api/admin/users', authMiddleware, adminOnly, async (req, res) => {
  try {
    const result = await pool.query('SELECT id, name, email, role, status, created_at FROM users ORDER BY created_at DESC');
    res.json({ users: result.rows });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to load users' });
  }
});

app.post('/api/admin/users', authMiddleware, adminOnly, async (req, res) => {
  try {
    const { name, email, password, role, status } = req.body || {};
    if (!name || !email || !password) {
      return res.status(400).json({ error: 'Name, email, and password are required' });
    }
    const normalizedEmail = email.toLowerCase();
    const existing = await pool.query('SELECT id FROM users WHERE email = $1', [normalizedEmail]);
    if (existing.rowCount) {
      return res.status(409).json({ error: 'Email is already registered' });
    }
    const password_hash = await bcrypt.hash(password, 12);
    const result = await pool.query(
      'INSERT INTO users (name, email, password_hash, role, status) VALUES ($1, $2, $3, $4, $5) RETURNING id, name, email, role, status',
      [name.trim(), normalizedEmail, password_hash, role || 'user', status || 'active']
    );
    res.status(201).json({ user: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to create user' });
  }
});

app.patch('/api/admin/users/:id', authMiddleware, adminOnly, async (req, res) => {
  try {
    const { id } = req.params;
    const { name, email, role, status } = req.body || {};
    const updates = [];
    const values = [];
    let index = 1;
    if (name) {
      updates.push(`name = $${index++}`);
      values.push(name.trim());
    }
    if (email) {
      const normalizedEmail = email.toLowerCase();
      const existing = await pool.query('SELECT id FROM users WHERE email = $1 AND id <> $2', [normalizedEmail, id]);
      if (existing.rowCount) {
        return res.status(409).json({ error: 'Email is already registered' });
      }
      updates.push(`email = $${index++}`);
      values.push(normalizedEmail);
    }
    if (role) {
      updates.push(`role = $${index++}`);
      values.push(role);
    }
    if (status) {
      updates.push(`status = $${index++}`);
      values.push(status);
    }
    if (!updates.length) {
      return res.status(400).json({ error: 'No updates provided' });
    }
    values.push(id);
    const result = await pool.query(`UPDATE users SET ${updates.join(', ')} WHERE id = $${index} RETURNING id, name, email, role, status`, values);
    if (!result.rowCount) return res.status(404).json({ error: 'User not found' });
    res.json({ user: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to update user' });
  }
});

app.get('/api/profiles', authMiddleware, async (req, res) => {
  try {
    if (req.user.role === 'admin') {
      const result = await pool.query('SELECT * FROM profiles ORDER BY created_at DESC');
      return res.json({ profiles: result.rows });
    }
    const result = await pool.query('SELECT * FROM profiles WHERE user_id = $1 ORDER BY created_at DESC', [req.user.id]);
    res.json({ profiles: result.rows });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to load profiles' });
  }
});

app.post('/api/profiles', authMiddleware, async (req, res) => {
  try {
    const { full_name, email, headline, location, skills, summary } = req.body || {};
    if (!full_name || !email) {
      return res.status(400).json({ error: 'Full name and email are required' });
    }
    const result = await pool.query(
      `INSERT INTO profiles (user_id, full_name, email, headline, location, skills, summary, status)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
       RETURNING *`,
      [req.user.id, full_name, email, headline || '', location || '', Array.isArray(skills) ? skills : [], summary || '', 'pending']
    );
    res.json({ profile: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to create profile' });
  }
});

app.get('/api/members', authMiddleware, async (req, res) => {
  try {
    if (req.user.role === 'admin') {
      const result = await pool.query('SELECT * FROM members ORDER BY created_at DESC');
      return res.json({ members: result.rows });
    }

    const result = await pool.query('SELECT * FROM members WHERE user_id = $1 ORDER BY created_at DESC', [req.user.id]);
    res.json({ members: result.rows });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to load members' });
  }
});

app.post('/api/members', authMiddleware, async (req, res) => {
  try {
    const {
      name,
      phone,
      email,
      age,
      nationalId,
      subLocation,
      education,
      formFourYear,
      kcse,
      institution,
      course,
      graduation,
      status,
      employer,
      career,
      skills,
    } = req.body || {};

    if (!name || !phone || !email || !age || !nationalId || !career || !status) {
      return res.status(400).json({ error: 'Missing required member fields' });
    }

    // Only admins may create member records through this endpoint.
    // Regular users are no longer allowed to create member records (they can only view).
    if (req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Admin access required to create member records' });
    }

    // allow multiple member records per user (no pre-insert uniqueness check)

    const result = await pool.query(
      `INSERT INTO members (
         user_id, name, phone, email, age, national_id, sub_location,
         education, form_four_year, kcse, institution, course, graduation,
         status, employer, career, skills
       ) VALUES (
         $1, $2, $3, $4, $5, $6, $7,
         $8, $9, $10, $11, $12, $13,
         $14, $15, $16, $17
       ) RETURNING *`,
      [
        req.user.id,
        name,
        phone,
        email,
        age,
        nationalId,
        subLocation || '',
        education || '',
        formFourYear || null,
        kcse || '',
        institution || '',
        course || '',
        graduation || null,
        status,
        employer || '',
        career,
        Array.isArray(skills) ? skills : [],
      ]
    );

    res.json({ member: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to create member' });
  }
});

app.patch('/api/members/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const {
      name,
      phone,
      email,
      age,
      nationalId,
      subLocation,
      education,
      formFourYear,
      kcse,
      institution,
      course,
      graduation,
      status,
      employer,
      career,
      skills,
    } = req.body || {};

    if (!name || !phone || !email || !age || !nationalId || !career || !status) {
      return res.status(400).json({ error: 'Missing required member fields' });
    }

    const existing = await pool.query('SELECT user_id FROM members WHERE id = $1', [id]);
    if (!existing.rowCount) {
      return res.status(404).json({ error: 'Member record not found' });
    }

    // Only admin users may update member records via this endpoint.
    if (req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Admin access required to update member records' });
    }

    const result = await pool.query(
      `UPDATE members SET
         name = $1, phone = $2, email = $3, age = $4, national_id = $5,
         sub_location = $6, education = $7, form_four_year = $8, kcse = $9,
         institution = $10, course = $11, graduation = $12, status = $13,
         employer = $14, career = $15, skills = $16
       WHERE id = $17
       RETURNING *`,
      [
        name,
        phone,
        email,
        age,
        nationalId,
        subLocation || '',
        education || '',
        formFourYear || null,
        kcse || '',
        institution || '',
        course || '',
        graduation || null,
        status,
        employer || '',
        career,
        Array.isArray(skills) ? skills : [],
        id,
      ]
    );

    res.json({ member: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to update member' });
  }
});

// Admin: create member for any user (admin-only path)
app.post('/api/admin/members', authMiddleware, adminOnly, async (req, res) => {
  try {
    const {
      userId,
      name,
      phone,
      email,
      age,
      nationalId,
      subLocation,
      education,
      formFourYear,
      kcse,
      institution,
      course,
      graduation,
      status,
      employer,
      career,
      skills,
    } = req.body || {};

    if (!userId || !name || !phone || !email || !age || !nationalId || !career || !status) {
      return res.status(400).json({ error: 'Missing required member fields or userId' });
    }

    // Verify user exists
    const userCheck = await pool.query('SELECT id FROM users WHERE id = $1', [userId]);
    if (!userCheck.rowCount) return res.status(404).json({ error: 'User not found' });

    // allow multiple member records per user (no pre-insert uniqueness check)

    const result = await pool.query(
      `INSERT INTO members (
         user_id, name, phone, email, age, national_id, sub_location,
         education, form_four_year, kcse, institution, course, graduation,
         status, employer, career, skills
       ) VALUES (
         $1, $2, $3, $4, $5, $6, $7,
         $8, $9, $10, $11, $12, $13,
         $14, $15, $16, $17
       ) RETURNING *`,
      [
        userId,
        name,
        phone,
        email,
        age,
        nationalId,
        subLocation || '',
        education || '',
        formFourYear || null,
        kcse || '',
        institution || '',
        course || '',
        graduation || null,
        status,
        employer || '',
        career,
        Array.isArray(skills) ? skills : [],
      ]
    );

    res.status(201).json({ member: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to create member' });
  }
});

// Admin: delete member record
app.delete('/api/members/:id', authMiddleware, adminOnly, async (req, res) => {
  try {
    const result = await pool.query('DELETE FROM members WHERE id = $1 RETURNING id', [req.params.id]);
    if (!result.rowCount) return res.status(404).json({ error: 'Member not found' });
    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to delete member' });
  }
});

// Admin: get member by id
app.get('/api/members/:id', authMiddleware, adminOnly, async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM members WHERE id = $1', [req.params.id]);
    if (!result.rowCount) return res.status(404).json({ error: 'Member not found' });
    res.json({ member: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to load member' });
  }
});

// Admin: export members to CSV
app.get('/api/admin/export/members', authMiddleware, adminOnly, async (req, res) => {
  try {
    const result = await pool.query('SELECT id, user_id, name, email, phone, age, national_id, sub_location, education, kcse, institution, course, graduation, status, employer, career, skills, created_at FROM members ORDER BY created_at DESC');
    const rows = result.rows || [];
    const columns = ['id','user_id','name','email','phone','age','national_id','sub_location','education','kcse','institution','course','graduation','status','employer','career','skills','created_at'];
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename="members-export.csv"');
    const escape = v => typeof v === 'string' && (v.includes(',') || v.includes('\n') || v.includes('"')) ? `"${v.replace(/"/g,'""')}"` : (v===null||v===undefined?'':v);
    res.write(columns.join(',') + '\n');
    rows.forEach(r => {
      const line = columns.map(c => escape(Array.isArray(r[c]) ? r[c].join(';') : (r[c]===null? '': String(r[c])))).join(',');
      res.write(line + '\n');
    });
    res.end();
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to export members' });
  }
});

// Admin: export users to CSV
app.get('/api/admin/export/users', authMiddleware, adminOnly, async (req, res) => {
  try {
    const result = await pool.query('SELECT id, name, email, role, status, created_at FROM users ORDER BY created_at DESC');
    const rows = result.rows || [];
    const columns = ['id','name','email','role','status','created_at'];
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename="users-export.csv"');
    const escape = v => typeof v === 'string' && (v.includes(',') || v.includes('\n') || v.includes('"')) ? `"${v.replace(/"/g,'""')}"` : (v===null||v===undefined?'':v);
    res.write(columns.join(',') + '\n');
    rows.forEach(r => {
      const line = columns.map(c => escape(r[c])).join(',');
      res.write(line + '\n');
    });
    res.end();
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to export users' });
  }
});

app.delete('/api/profiles/:id', authMiddleware, adminOnly, async (req, res) => {
  try {
    const result = await pool.query('DELETE FROM profiles WHERE id = $1 RETURNING id', [req.params.id]);
    if (!result.rowCount) return res.status(404).json({ error: 'Profile not found' });
    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to delete profile' });
  }
});

app.patch('/api/profiles/:id', authMiddleware, adminOnly, async (req, res) => {
  try {
    const { status } = req.body || {};
    if (!status) return res.status(400).json({ error: 'Status is required' });
    const result = await pool.query('UPDATE profiles SET status = $1 WHERE id = $2 RETURNING *', [status, req.params.id]);
    if (!result.rowCount) return res.status(404).json({ error: 'Profile not found' });
    res.json({ profile: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Unable to update profile status' });
  }
});

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'pages', 'index.html'));
});

initDatabase()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Server listening on http://localhost:${PORT}`);
    });
  })
  .catch((err) => {
    console.error('Database initialization failed:', err);
    process.exit(1);
  });
