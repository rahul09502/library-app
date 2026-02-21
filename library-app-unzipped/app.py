from flask import Flask, render_template, request, jsonify, g, session, redirect, url_for, flash
import sqlite3
import os
import functools
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import CSRFProtect
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'instance', 'library.db')

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'), static_folder=os.path.join(BASE_DIR, 'static'))
app.secret_key = os.environ.get('LIB_APP_SECRET', 'dev-secret-change-me')
# Simple admin password (use env var in production)
# Default changed to rahul@123 for convenience; override with env var LIB_ADMIN_PASS
ADMIN_PASSWORD = os.environ.get('LIB_ADMIN_PASS', 'rahul@123')
# enable CSRF protection for all POST/PUT/DELETE requests
csrf = CSRFProtect()
csrf.init_app(app)

def admin_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return view(*args, **kwargs)
    return wrapped


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('student_id'):
            return redirect(url_for('student_login'))
        return view(*args, **kwargs)
    return wrapped

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip()
    dept = request.args.get('dept', '').strip()
    # expanded filters
    min_year = request.args.get('min_year', '').strip()
    max_year = request.args.get('max_year', '').strip()
    available = request.args.get('available', '').strip().lower()  # '1' or 'true'
    db = get_db()
    params = []
    sql = "SELECT id, title, author, year, isbn, copies, department FROM books WHERE 1=1"
    if q:
        sql += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ? )"
        like = f"%{q}%"
        params.extend([like, like, like])
    if dept:
        sql += " AND department = ?"
        params.append(dept)
    if min_year.isdigit():
        sql += " AND year >= ?"
        params.append(int(min_year))
    if max_year.isdigit():
        sql += " AND year <= ?"
        params.append(int(max_year))
    if available in ('1', 'true', 'yes'):
        sql += " AND copies > 0"
    sql += " ORDER BY title LIMIT 200"
    cur = db.execute(sql, params)
    rows = cur.fetchall()
    books = [dict(r) for r in rows]
    return jsonify(books)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if pwd == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash('Logged in as admin', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid password', 'error')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))


@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        if not name or not email or not password:
            flash('Name, email and password are required', 'error')
            return redirect(url_for('student_register'))
        db = get_db()
        try:
            pwd_hash = generate_password_hash(password)
            db.execute('INSERT INTO students (name,email,password_hash) VALUES (?,?,?)', (name, email, pwd_hash))
            db.commit()
            flash('Registration successful, please login', 'success')
            return redirect(url_for('student_login'))
        except sqlite3.IntegrityError:
            flash('Email already registered', 'error')
            return redirect(url_for('student_register'))
    return render_template('student_register.html')


@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        db = get_db()
        cur = db.execute('SELECT id, name, password_hash FROM students WHERE email = ?', (email,))
        user = cur.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['student_id'] = user['id']
            session['student_name'] = user['name']
            # populate active borrow count in session
            cur2 = db.execute('SELECT COUNT(*) as cnt FROM borrows WHERE student_id = ? AND returned_at IS NULL', (user['id'],))
            cnt = cur2.fetchone()['cnt']
            session['borrow_count'] = cnt
            flash('Logged in', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials', 'error')
    return render_template('student_login.html')


@app.route('/student/logout')
def student_logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    session.pop('borrow_count', None)
    return redirect(url_for('index'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    cur = db.execute('SELECT id, title, author, year, isbn, copies, department FROM books ORDER BY title')
    books = [dict(r) for r in cur.fetchall()]
    return render_template('admin_dashboard.html', books=books)


@app.route('/admin/borrows')
@admin_required
def admin_borrows():
    db = get_db()
    cur = db.execute('''
        SELECT br.id as borrow_id, br.borrowed_at, br.returned_at,
               br.student_id, s.name as student_name, s.email, bk.id as book_id, bk.title
        FROM borrows br
        JOIN students s ON br.student_id = s.id
        JOIN books bk ON br.book_id = bk.id
        ORDER BY br.borrowed_at DESC
    ''')
    rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        try:
            borrowed = datetime.fromisoformat(r['borrowed_at']) if r['borrowed_at'] else None
            if r.get('returned_at'):
                returned = datetime.fromisoformat(r['returned_at'])
                delta = returned - borrowed if borrowed else None
                if delta is not None:
                    days = delta.days
                    hours = delta.seconds // 3600
                    r['duration_readable'] = f"{days}d {hours}h"
                else:
                    r['duration_readable'] = 'n/a'
            else:
                if borrowed:
                    delta = datetime.utcnow() - borrowed
                    days = delta.days
                    hours = delta.seconds // 3600
                    r['duration_readable'] = f"{days}d {hours}h (ongoing)"
                else:
                    r['duration_readable'] = 'n/a'
        except Exception:
            r['duration_readable'] = 'n/a'
    return render_template('admin_borrows.html', borrows=rows)


@app.route('/admin/add', methods=['POST'])
@admin_required
def admin_add():
    title = request.form.get('title','').strip()
    author = request.form.get('author','').strip()
    year = request.form.get('year','').strip()
    isbn = request.form.get('isbn','').strip()
    copies = request.form.get('copies','1').strip()
    department = request.form.get('department','').strip()
    db = get_db()
    # server-side validation
    errors = []
    if not title:
        errors.append('Title is required')
    if copies and not copies.isdigit():
        errors.append('Copies must be a number')
    if year and not year.isdigit():
        errors.append('Year must be a number')
    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('admin_dashboard'))
    db.execute('INSERT INTO books (title,author,year,isbn,copies,department) VALUES (?,?,?,?,?,?)',
               (title, author, int(year) if year.isdigit() else None, isbn, int(copies) if copies.isdigit() else 1, department))
    db.commit()
    flash('Book added', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit(book_id):
    db = get_db()
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        author = request.form.get('author','').strip()
        year = request.form.get('year','').strip()
        isbn = request.form.get('isbn','').strip()
        copies = request.form.get('copies','1').strip()
        department = request.form.get('department','').strip()
        errors = []
        if not title:
            errors.append('Title is required')
        if copies and not copies.isdigit():
            errors.append('Copies must be a number')
        if year and not year.isdigit():
            errors.append('Year must be a number')
        if errors:
            for e in errors:
                flash(e, 'error')
            return redirect(url_for('admin_edit', book_id=book_id))
        db.execute('UPDATE books SET title=?,author=?,year=?,isbn=?,copies=?,department=? WHERE id=?',
                   (title, author, int(year) if year.isdigit() else None, isbn, int(copies) if copies.isdigit() else 1, department, book_id))
        db.commit()
        flash('Book updated', 'success')
        return redirect(url_for('admin_dashboard'))
    cur = db.execute('SELECT id, title, author, year, isbn, copies, department FROM books WHERE id = ?', (book_id,))
    book = cur.fetchone()
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_edit.html', book=dict(book))


@app.route('/admin/delete/<int:book_id>', methods=['POST'])
@admin_required
def admin_delete(book_id):
    db = get_db()
    db.execute('DELETE FROM books WHERE id = ?', (book_id,))
    db.commit()
    flash('Book deleted', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/student/borrow/<int:book_id>', methods=['POST'])
@login_required
def student_borrow(book_id):
    db = get_db()
    cur = db.execute('SELECT id, title, copies FROM books WHERE id = ?', (book_id,))
    book = cur.fetchone()
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('index'))
    # enforce per-student borrow limit
    cur2 = db.execute('SELECT COUNT(*) as cnt FROM borrows WHERE student_id = ? AND returned_at IS NULL', (session['student_id'],))
    active = cur2.fetchone()['cnt']
    if active >= 3:
        flash('Borrow limit reached (3 books). Return a book before borrowing another.', 'error')
        return redirect(url_for('student_dashboard'))
    if book['copies'] <= 0:
        flash('Book not available', 'error')
        return redirect(url_for('index'))
    # decrement copies and create borrow record
    db.execute('UPDATE books SET copies = copies - 1 WHERE id = ?', (book_id,))
    db.execute('INSERT INTO borrows (student_id, book_id, borrowed_at) VALUES (?,?,?)',
               (session['student_id'], book_id, datetime.utcnow().isoformat()))
    db.commit()
    # update session borrow_count
    cur3 = db.execute('SELECT COUNT(*) as cnt FROM borrows WHERE student_id = ? AND returned_at IS NULL', (session['student_id'],))
    session['borrow_count'] = cur3.fetchone()['cnt']
    flash(f"Borrowed: {book['title']}", 'success')
    return redirect(url_for('student_dashboard'))


@app.route('/student/return/<int:borrow_id>', methods=['POST'])
@login_required
def student_return(borrow_id):
    db = get_db()
    cur = db.execute('SELECT id, student_id, book_id, returned_at FROM borrows WHERE id = ?', (borrow_id,))
    rec = cur.fetchone()
    if not rec:
        flash('Record not found', 'error')
        return redirect(url_for('student_dashboard'))
    if rec['student_id'] != session['student_id']:
        flash('Not authorized', 'error')
        return redirect(url_for('student_dashboard'))
    if rec['returned_at']:
        flash('Already returned', 'error')
        return redirect(url_for('student_dashboard'))
    # mark returned and increment copies
    db.execute('UPDATE borrows SET returned_at = ? WHERE id = ?', (datetime.utcnow().isoformat(), borrow_id))
    db.execute('UPDATE books SET copies = copies + 1 WHERE id = ?', (rec['book_id'],))
    db.commit()
    # update session borrow_count
    cur2 = db.execute('SELECT COUNT(*) as cnt FROM borrows WHERE student_id = ? AND returned_at IS NULL', (session['student_id'],))
    session['borrow_count'] = cur2.fetchone()['cnt']
    flash('Book returned', 'success')
    return redirect(url_for('student_dashboard'))


@app.route('/student/dashboard')
@login_required
def student_dashboard():
    db = get_db()
    cur = db.execute('''
        SELECT br.id as borrow_id, bk.id as book_id, bk.title, bk.author, br.borrowed_at, br.returned_at
        FROM borrows br JOIN books bk ON br.book_id = bk.id
        WHERE br.student_id = ?
        ORDER BY br.borrowed_at DESC
    ''', (session['student_id'],))
    borrows = [dict(r) for r in cur.fetchall()]
    # refresh session borrow count
    cur2 = db.execute('SELECT COUNT(*) as cnt FROM borrows WHERE student_id = ? AND returned_at IS NULL', (session['student_id'],))
    session['borrow_count'] = cur2.fetchone()['cnt']
    return render_template('student_dashboard.html', borrows=borrows)

if __name__ == '__main__':
    app.run(debug=True)
