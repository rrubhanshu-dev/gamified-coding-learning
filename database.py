"""
Database connection and setup
"""

import sqlite3
from datetime import datetime

DATABASE = 'gamified_coding.db'


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all database tables"""
    db = get_db()
    
    # Users table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            language_track TEXT DEFAULT 'python',
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Questions table
    db.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT,
            difficulty TEXT NOT NULL CHECK(difficulty IN ('easy', 'medium', 'hard')),
            topic TEXT NOT NULL,
            subject TEXT DEFAULT 'Python',
            language_track TEXT DEFAULT 'python',
            points INTEGER DEFAULT 10,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP
        )
    ''')
    
    # Add is_active and subject columns if they don't exist
    try:
        db.execute('ALTER TABLE questions ADD COLUMN is_active INTEGER DEFAULT 1')
    except sqlite3.OperationalError:
        pass
    
    try:
        db.execute('ALTER TABLE questions ADD COLUMN subject TEXT DEFAULT \'Python\'')
    except sqlite3.OperationalError:
        pass
    
    # User stats table
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            streak INTEGER DEFAULT 0,
            last_activity_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Attempts table
    db.execute('''
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            selected_answer TEXT NOT NULL,
            is_correct INTEGER DEFAULT 0,
            xp_earned INTEGER DEFAULT 0,
            attempted_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        )
    ''')
    
    # Badges table
    db.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            badge_type TEXT,
            requirement_value INTEGER
        )
    ''')
    
    # User badges table
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            badge_id INTEGER NOT NULL,
            earned_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE,
            UNIQUE(user_id, badge_id)
        )
    ''')
    
    # Learning materials table
    db.execute('''
        CREATE TABLE IF NOT EXISTS learning_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            topic TEXT NOT NULL,
            language_track TEXT DEFAULT 'python',
            level TEXT DEFAULT 'beginner' CHECK(level IN ('beginner', 'intermediate', 'advanced')),
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')
    
    # Subjects table
    db.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            language_track TEXT DEFAULT 'python',
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Topics table
    db.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
            UNIQUE(subject_id, name)
        )
    ''')
    
    # Notes table
    db.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            visibility TEXT DEFAULT 'published' CHECK(visibility IN ('draft', 'published')),
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Question completion tracking
    try:
        db.execute('ALTER TABLE attempts ADD COLUMN is_final_attempt INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS question_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            first_correct_at TIMESTAMP,
            total_attempts INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
            UNIQUE(user_id, question_id)
        )
    ''')
    
    # Tests table
    db.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            subject_id INTEGER,
            time_limit_minutes INTEGER DEFAULT 60,
            total_questions INTEGER DEFAULT 0,
            passing_score INTEGER DEFAULT 50,
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'published', 'archived')),
            assigned_to_all INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Test questions table
    db.execute('''
        CREATE TABLE IF NOT EXISTS test_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            order_index INTEGER DEFAULT 0,
            points INTEGER DEFAULT 1,
            FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
            UNIQUE(test_id, question_id)
        )
    ''')
    
    # Test assignments table
    db.execute('''
        CREATE TABLE IF NOT EXISTS test_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            assigned_at TIMESTAMP,
            assigned_by INTEGER,
            FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE SET NULL,
            UNIQUE(test_id, user_id)
        )
    ''')
    
    # Test attempts table
    db.execute('''
        CREATE TABLE IF NOT EXISTS test_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            started_at TIMESTAMP,
            submitted_at TIMESTAMP,
            score INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            status TEXT DEFAULT 'in_progress' CHECK(status IN ('in_progress', 'completed', 'abandoned')),
            FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(test_id, user_id, started_at)
        )
    ''')
    
    # Test attempt answers table
    db.execute('''
        CREATE TABLE IF NOT EXISTS test_attempt_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_attempt_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            selected_answer TEXT,
            is_correct INTEGER DEFAULT 0,
            points_earned INTEGER DEFAULT 0,
            answered_at TIMESTAMP,
            FOREIGN KEY (test_attempt_id) REFERENCES test_attempts(id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        )
    ''')
    
    # Update users table for super_admin
    try:
        db.execute("ALTER TABLE users ADD COLUMN is_super_admin INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    # Courses table
    db.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived')),
            created_at TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Course subjects table
    db.execute('''
        CREATE TABLE IF NOT EXISTS course_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            order_index INTEGER DEFAULT 0,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
            UNIQUE(course_id, subject_id)
        )
    ''')
    
    # Course enrollments table
    db.execute('''
        CREATE TABLE IF NOT EXISTS course_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            enrolled_at TIMESTAMP,
            enrolled_by INTEGER,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'dropped')),
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (enrolled_by) REFERENCES users(id) ON DELETE SET NULL,
            UNIQUE(course_id, user_id)
        )
    ''')
    
    # Content generation log table
    db.execute('''
        CREATE TABLE IF NOT EXISTS content_generation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL CHECK(content_type IN ('note', 'question', 'test')),
            content_id INTEGER,
            generation_method TEXT DEFAULT 'placeholder',
            generated_at TIMESTAMP,
            generated_by INTEGER,
            FOREIGN KEY (generated_by) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Initialize default badges
    default_badges = [
        ('First Steps', 'Complete your first question', 'first_attempt', 1),
        ('Quick Learner', 'Reach level 5', 'level', 5),
        ('Expert', 'Reach level 10', 'level', 10),
        ('Master', 'Reach level 20', 'level', 20),
        ('Dedicated', 'Maintain a 7-day streak', 'streak', 7),
        ('Unstoppable', 'Maintain a 30-day streak', 'streak', 30),
        ('Centurion', 'Earn 1000 XP', 'xp', 1000),
        ('Champion', 'Earn 5000 XP', 'xp', 5000),
    ]
    
    for badge_name, description, badge_type, requirement in default_badges:
        db.execute(
            'INSERT OR IGNORE INTO badges (name, description, badge_type, requirement_value) VALUES (?, ?, ?, ?)',
            (badge_name, description, badge_type, requirement)
        )
    
    db.commit()
    db.close()
    print("Database initialized successfully!")
