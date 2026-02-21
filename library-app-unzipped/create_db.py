import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE = Path(__file__).parent
DB_PATH = BASE / 'instance' / 'library.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    year INTEGER,
    isbn TEXT,
    copies INTEGER DEFAULT 1,
    department TEXT
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS borrows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrowed_at TEXT NOT NULL,
    returned_at TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
)
''')

sample = [
    ('Introduction to Algorithms','Cormen, Leiserson, Rivest',2009,'0262033844',3,'CSE'),
    ('Clean Code','Robert C. Martin',2008,'0132350882',2,'CSE'),
    ('Linear Algebra and Its Applications','Gilbert Strang',2016,'0980232776',1,'Math'),
    ('Database System Concepts','Silberschatz, Korth, Sudarshan',2010,'0073523321',2,'CSE'),
    ('Artificial Intelligence: A Modern Approach','Stuart Russell, Peter Norvig',2010,'0136042597',2,'CSE'),
    ('Operating System Concepts','Silberschatz, Galvin, Gagne',2018,'1119456339',2,'CSE'),
    ('Discrete Mathematics and Its Applications','Kenneth H. Rosen',2011,'0073383090',1,'Math'),
    ('Computer Networks','Andrew S. Tanenbaum',2010,'0132126958',1,'CSE'),
    ('Principles of Compiler Design','Aho, Ullman',2007,'0201003003',1,'CSE'),
    ('Modern Database Management','Jeffrey A. Hoffer',2012,'0136086203',1,'CSE')
]

cur.executemany('INSERT INTO books (title,author,year,isbn,copies,department) VALUES (?,?,?,?,?,?)', sample)

# sample student
pwd = generate_password_hash('student123')
try:
    cur.execute('INSERT INTO students (name,email,password_hash) VALUES (?,?,?)', ('Sample Student', 'student@example.com', pwd))
except Exception:
    pass

conn.commit()
conn.close()

print('Created database at', DB_PATH)
