"""
Gamified Coding Learning Web Application
Main Flask Application Entry Point

Author: Your Name
Date: 2024
"""
from seed_data import seed_all
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import datetime
from functools import wraps
from database import init_db, get_db
from logic import (calculate_xp, check_level_up, update_streak, check_badge_unlock,
                  get_user_stats, get_leaderboard, get_accuracy_percentage,
                  check_question_completion, record_question_completion, should_award_xp,
                  generate_note_content, generate_question_content, log_content_generation)

# Initialize Flask app
app = Flask(__name__)
from database import init_db, get_db

def initialize_app():
    """Initialize database and auto-seed if empty (cloud-safe)"""
    init_db()
    db = get_db()

    try:
        # Check if database is empty by checking users table count
        cursor = db.execute("SELECT COUNT(*) as count FROM users")
        count = cursor.fetchone()["count"]
    except Exception as e:
        print(f"⚠️ Error checking database: {e}")
        count = 0

    if count == 0:
        print("=" * 60)
        print("⚠️ Database is empty. Starting auto-seeding...")
        print("=" * 60)
        try:
            seed_all()
            print("=" * 60)
            print("✅ Database seeded successfully!")
            print("=" * 60)
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            raise
    else:
        print(f"ℹ️ Database already contains {count} user(s). Skipping seed.")

initialize_app()

app.secret_key = 'your-secret-key-change-in-production-2024-gamified-coding'

# Configuration
app.config['DATABASE'] = 'gamified_coding.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database is already initialized by initialize_app() above


# ==================== UTILITY FUNCTIONS ====================

def normalize_answer(answer):
    """Normalize answer for comparison - handles case, whitespace, and None values"""
    if answer is None:
        return ''
    return ''.join(str(answer).split()).upper()


def compare_answers(student_answer, correct_answer):
    """Compare answers after normalization"""
    student_norm = normalize_answer(student_answer)
    correct_norm = normalize_answer(correct_answer)
    
    if not student_norm or not correct_norm:
        return False
    
    return student_norm == correct_norm


# ==================== DECORATORS ====================

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Require admin or super admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        db = get_db()
        user = db.execute(
            'SELECT role, is_super_admin FROM users WHERE id = ?', (session['user_id'],)
        ).fetchone()
        is_super_admin = user['is_super_admin'] if user and 'is_super_admin' in user.keys() else 0
        if not user or (user['role'] != 'admin' and not is_super_admin):
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def super_admin_required(f):
    """Require super admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        db = get_db()
        user = db.execute(
            'SELECT is_super_admin FROM users WHERE id = ?', (session['user_id'],)
        ).fetchone()
        is_super_admin = user['is_super_admin'] if user and 'is_super_admin' in user.keys() else 0
        if not user or not is_super_admin:
            flash('Access denied. Super admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        language_track = request.form.get('language_track', 'python')

        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        db = get_db()
        
        # Check if username or email already exists
        existing_user = db.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()

        if existing_user:
            flash('Username or email already exists.', 'danger')
            return render_template('register.html')

        # Create new user
        hashed_password = generate_password_hash(password)
        try:
            cursor = db.execute(
                '''INSERT INTO users (username, email, password, language_track, role, created_at)
                   VALUES (?, ?, ?, ?, 'student', ?)''',
                (username, email, hashed_password, language_track, datetime.datetime.now())
            )
            db.commit()
            user_id = cursor.lastrowid

            # Initialize user stats
            db.execute(
                '''INSERT INTO user_stats (user_id, xp, level, streak, last_activity_date)
                   VALUES (?, 0, 1, 0, ?)''',
                (user_id, datetime.date.today())
            )
            db.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')

        db = get_db()
        user = db.execute(
            'SELECT id, username, email, password, role FROM users WHERE username = ?',
            (username,)
        ).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            # Update last login
            db.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (datetime.datetime.now(), user['id'])
            )
            db.commit()

            flash(f'Welcome back, {user["username"]}!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# ==================== STUDENT ROUTES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard with stats and charts"""
    db = get_db()
    user_id = session['user_id']
    
    # Get user stats
    stats = get_user_stats(user_id)
    
    # Get recent attempts
    recent_attempts = db.execute(
        '''SELECT q.title, a.is_correct, a.attempted_at, q.difficulty, q.topic
           FROM attempts a
           JOIN questions q ON a.question_id = q.id
           WHERE a.user_id = ?
           ORDER BY a.attempted_at DESC
           LIMIT 10''',
        (user_id,)
    ).fetchall()

    # Get topic-wise performance
    topic_stats = db.execute(
        '''SELECT q.topic, 
                  COUNT(*) as total,
                  SUM(CASE WHEN a.is_correct = 1 THEN 1 ELSE 0 END) as correct
           FROM attempts a
           JOIN questions q ON a.question_id = q.id
           WHERE a.user_id = ?
           GROUP BY q.topic''',
        (user_id,)
    ).fetchall()

    # Get badges
    badges = db.execute(
        '''SELECT b.name, b.description, ub.earned_at
           FROM user_badges ub
           JOIN badges b ON ub.badge_id = b.id
           WHERE ub.user_id = ?
           ORDER BY ub.earned_at DESC''',
        (user_id,)
    ).fetchall()

    # Get XP history for charts (last 30 days)
    xp_history_raw = db.execute(
        '''SELECT DATE(attempted_at) as date, SUM(xp_earned) as daily_xp
           FROM attempts
           WHERE user_id = ? AND attempted_at >= datetime('now', '-30 days')
           GROUP BY DATE(attempted_at)
           ORDER BY date''',
        (user_id,)
    ).fetchall()
    
    # Convert Row objects to dictionaries for JSON serialization
    xp_history = [{'date': str(row['date']), 'daily_xp': int(row['daily_xp'])} for row in xp_history_raw]
    
    # Convert topic_stats to dictionaries as well
    topic_stats_list = [{'topic': row['topic'], 'total': row['total'], 'correct': row['correct']} for row in topic_stats]

    return render_template('dashboard.html', 
                         stats=stats,
                         recent_attempts=recent_attempts,
                         topic_stats=topic_stats_list,
                         badges=badges,
                         xp_history=xp_history)


@app.route('/practice')
@login_required
def practice():
    """Practice page with questions organized by topic and level"""
    db = get_db()
    user_id = session['user_id']
    
    # Get filter parameters
    topic = request.args.get('topic', '')
    difficulty = request.args.get('difficulty', '')
    
    # Get user's language track
    user = db.execute(
        'SELECT language_track FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    language_track = user['language_track'] if user else 'python'
    
    # Build query - only active questions
    query = '''SELECT id, title, difficulty, topic, points
               FROM questions 
               WHERE language_track = ? AND is_active = 1'''
    params = [language_track]
    
    if topic:
        query += ' AND topic = ?'
        params.append(topic)
    if difficulty:
        query += ' AND difficulty = ?'
        params.append(difficulty)
    
    query += ''' ORDER BY topic, 
                     CASE difficulty
                         WHEN "easy" THEN 1
                         WHEN "medium" THEN 2
                         WHEN "hard" THEN 3
                     END, id'''
    
    questions = db.execute(query, params).fetchall()
    
    # Get unique topics and difficulties for filter (only active questions)
    topics_list = db.execute(
        'SELECT DISTINCT topic FROM questions WHERE language_track = ? AND is_active = 1 ORDER BY topic',
        (language_track,)
    ).fetchall()
    
    # Organize questions by topic
    questions_by_topic = {}
    
    # Initialize all topics with empty levels
    for topic_row in topics_list:
        topic_name = topic_row['topic']
        if topic_name not in questions_by_topic:
            questions_by_topic[topic_name] = {
                'easy': [],
                'medium': [],
                'hard': []
            }
    
    # Organize actual questions by topic and difficulty
    for question in questions:
        topic_name = question['topic']
        if topic_name not in questions_by_topic:
            questions_by_topic[topic_name] = {
                'easy': [],
                'medium': [],
                'hard': []
            }
        questions_by_topic[topic_name][question['difficulty']].append(question)
    
    difficulties = ['easy', 'medium', 'hard']
    
    return render_template('practice.html',
                         questions=questions,
                         questions_by_topic=questions_by_topic,
                         topics=topics_list,
                         difficulties=difficulties,
                         selected_topic=topic,
                         selected_difficulty=difficulty)


@app.route('/question/<int:question_id>')
@login_required
def question_detail(question_id):
    """View and attempt a specific question"""
    db = get_db()
    user_id = session['user_id']
    
    # Get question (only active)
    question = db.execute(
        'SELECT * FROM questions WHERE id = ? AND is_active = 1', (question_id,)
    ).fetchone()
    
    if not question:
        flash('Question not found.', 'danger')
        return redirect(url_for('practice'))
    
    # Get user's previous attempts
    attempts = db.execute(
        '''SELECT is_correct, attempted_at, xp_earned
           FROM attempts
           WHERE user_id = ? AND question_id = ?
           ORDER BY attempted_at DESC
           LIMIT 5''',
        (user_id, question_id)
    ).fetchall()
    
    return render_template('question.html',
                         question=question,
                         attempts=attempts)


@app.route('/submit_answer', methods=['POST'])
@login_required
def submit_answer():
    """Submit answer and calculate XP"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400
            
        question_id = data.get('question_id')
        selected_answer = data.get('answer', '').strip()
        
        if not question_id or not selected_answer:
            return jsonify({'success': False, 'message': 'Invalid request: question_id and answer are required'}), 400
        
        db = get_db()
        user_id = session['user_id']
        
        # Get question
        question = db.execute(
            'SELECT * FROM questions WHERE id = ?', (question_id,)
        ).fetchone()
        
        if not question:
            return jsonify({'success': False, 'message': 'Question not found'}), 404
        
        # Check answer using normalized comparison
        is_correct = compare_answers(selected_answer, question['correct_answer'])
        
        # MODULE 2: Check if XP should be awarded (prevent farming)
        try:
            should_award, award_reason = should_award_xp(user_id, question_id, is_correct)
        except Exception as xp_check_error:
            # If XP check fails, default to awarding XP
            print(f"Error in should_award_xp: {str(xp_check_error)}")
            should_award = True
            award_reason = "error_fallback"
        
        # Calculate XP (but may be reduced if already completed)
        if should_award:
            xp_earned = calculate_xp(is_correct, question['difficulty'], question['points'])
        else:
            # Already completed - only give minimal participation XP for wrong answers
            if is_correct:
                xp_earned = 0  # No XP for repeated correct answers
            else:
                xp_earned = calculate_xp(False, question['difficulty'], question['points'])  # Participation only
        
        # Get the selected option text for feedback
        selected_option_map = {
            'A': question['option_a'],
            'B': question['option_b'],
            'C': question['option_c'],
            'D': question['option_d']
        }
        selected_option_text = selected_option_map.get(selected_answer.upper(), 'Unknown')
        
        # Get correct option text
        correct_option_map = {
            'A': question['option_a'],
            'B': question['option_b'],
            'C': question['option_c'],
            'D': question['option_d']
        }
        correct_option_text = correct_option_map.get(question['correct_answer'].upper(), 'Unknown')
        
        # Record question completion (non-blocking - errors are handled inside)
        try:
            record_question_completion(user_id, question_id, is_correct)
        except Exception as completion_error:
            # Log but don't fail the request
            print(f"Error in record_question_completion: {str(completion_error)}")
        
        # Save attempt
        is_final_attempt = 1 if (is_correct and should_award) else 0
        db.execute(
            '''INSERT INTO attempts (user_id, question_id, selected_answer, is_correct, xp_earned, attempted_at, is_final_attempt)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (user_id, question_id, selected_answer, is_correct, xp_earned, datetime.datetime.now(), is_final_attempt)
        )
        
        # Update user stats
        user_stats = db.execute(
            'SELECT xp, level FROM user_stats WHERE user_id = ?', (user_id,)
        ).fetchone()
        
        # Initialize user stats if they don't exist
        if not user_stats:
            from datetime import date
            db.execute(
                '''INSERT INTO user_stats (user_id, xp, level, streak, last_activity_date)
                   VALUES (?, 0, 1, 0, ?)''',
                (user_id, date.today())
            )
            current_xp = 0
            current_level = 1
        else:
            current_xp = user_stats['xp'] or 0
            current_level = user_stats['level'] or 1
        
        new_xp = current_xp + xp_earned
        new_level = check_level_up(new_xp)
        
        db.execute(
            'UPDATE user_stats SET xp = ?, level = ? WHERE user_id = ?',
            (new_xp, new_level, user_id)
        )
        
        # Commit before calling other functions that might use database
        db.commit()
        
        # Update streak (uses its own connection)
        update_streak(user_id)
        
        # Check badge unlock (uses its own connection)
        try:
            badge_unlocked = check_badge_unlock(user_id, new_xp, new_level)
        except Exception as badge_error:
            # Don't fail the whole request if badge check fails
            print(f"Badge unlock error: {str(badge_error)}")
            badge_unlocked = []
        
        return jsonify({
            'success': True,
            'is_correct': is_correct,
            'xp_earned': xp_earned,
            'new_xp': new_xp,
            'new_level': new_level,
            'correct_answer': question['correct_answer'],
            'correct_answer_text': correct_option_text,
            'selected_answer': selected_answer,
            'selected_answer_text': selected_option_text,
            'explanation': question['explanation'] or 'No explanation provided.',
            'badge_unlocked': badge_unlocked,
            'xp_awarded': should_award,
            'award_reason': award_reason
        })
    except Exception as e:
        # Ensure we always return JSON, even on errors
        import traceback
        # Log the error for debugging
        error_msg = str(e)
        if app.debug:
            print(f"Error in submit_answer: {error_msg}")
            print(traceback.format_exc())
        
        # Try to rollback any database changes if db was created
        try:
            if 'db' in locals():
                db.rollback()
        except Exception:
            pass
        
        return jsonify({
            'success': False,
            'message': f'An error occurred while processing your answer: {error_msg}',
            'error_details': traceback.format_exc() if app.debug else 'Enable debug mode for details'
        }), 500


@app.route('/leaderboard')
@login_required
def leaderboard():
    """Leaderboard page"""
    leaderboard_data = get_leaderboard()
    return render_template('leaderboard.html', leaderboard=leaderboard_data)


# ==================== LEARNING AREA ROUTES ====================

@app.route('/learn')
@login_required
def learn():
    """Main learning hub - shows courses, subjects, and materials"""
    db = get_db()
    user_id = session['user_id']
    
    enrolled_courses = db.execute(
        '''SELECT c.id, c.name FROM courses c
           JOIN course_enrollments ce ON c.id = ce.course_id
           WHERE ce.user_id = ? AND ce.status = 'active' ''',
        (user_id,)
    ).fetchall()
    
    if enrolled_courses:
        course_ids = [c['id'] for c in enrolled_courses]
        placeholders = ','.join(['?'] * len(course_ids))
        subjects = db.execute(
            f'''SELECT DISTINCT s.* FROM subjects s
                JOIN course_subjects cs ON s.id = cs.subject_id
                WHERE cs.course_id IN ({placeholders})
                ORDER BY s.order_index, s.name''',
            course_ids
        ).fetchall()
    else:
        subjects = db.execute('SELECT * FROM subjects ORDER BY order_index, name').fetchall()
    
    user = db.execute('SELECT language_track FROM users WHERE id = ?', (user_id,)).fetchone()
    language_track = user['language_track'] if user else 'python'
    
    topics_data = db.execute(
        '''SELECT topic, level, COUNT(*) as material_count
           FROM learning_materials
           WHERE language_track = ?
           GROUP BY topic, level
           ORDER BY topic, 
                    CASE level
                        WHEN 'beginner' THEN 1
                        WHEN 'intermediate' THEN 2
                        WHEN 'advanced' THEN 3
                    END''',
        (language_track,)
    ).fetchall()
    
    topics_dict = {}
    for row in topics_data:
        topic = row['topic']
        if topic not in topics_dict:
            topics_dict[topic] = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
        topics_dict[topic][row['level']] = row['material_count']
    
    all_materials = db.execute(
        '''SELECT * FROM learning_materials
           WHERE language_track = ?
           ORDER BY topic, 
                    CASE level
                        WHEN 'beginner' THEN 1
                        WHEN 'intermediate' THEN 2
                        WHEN 'advanced' THEN 3
                    END, order_index''',
        (language_track,)
    ).fetchall()
    
    return render_template('learn/index.html',
                         subjects=subjects,
                         enrolled_courses=enrolled_courses,
                         topics_dict=topics_dict,
                         all_materials=all_materials,
                         language_track=language_track)


@app.route('/learn/topic/<topic>')
@login_required
def learn_topic(topic):
    """Learning materials for a specific topic"""
    db = get_db()
    user_id = session['user_id']
    level = request.args.get('level', '')
    
    user = db.execute(
        'SELECT language_track FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    language_track = user['language_track'] if user else 'python'
    
    query = '''SELECT * FROM learning_materials
               WHERE topic = ? AND language_track = ?'''
    params = [topic, language_track]
    
    if level:
        query += ' AND level = ?'
        params.append(level)
    
    query += ''' ORDER BY 
                    CASE level
                        WHEN 'beginner' THEN 1
                        WHEN 'intermediate' THEN 2
                        WHEN 'advanced' THEN 3
                    END, order_index'''
    
    materials = db.execute(query, params).fetchall()
    
    questions_query = 'SELECT * FROM questions WHERE topic = ? AND language_track = ?'
    questions_params = [topic, language_track]
    
    if level:
        difficulty_map = {'beginner': 'easy', 'intermediate': 'medium', 'advanced': 'hard'}
        questions_query += ' AND difficulty = ?'
        questions_params.append(difficulty_map.get(level, ''))
    
    questions_query += ' ORDER BY difficulty, id'
    questions = db.execute(questions_query, questions_params).fetchall()
    
    return render_template('learn/topic.html',
                         topic=topic,
                         materials=materials,
                         questions=questions,
                         selected_level=level)


@app.route('/learn/material/<int:material_id>')
@login_required
def learn_material(material_id):
    """View a specific learning material"""
    db = get_db()
    
    material = db.execute(
        'SELECT * FROM learning_materials WHERE id = ?', (material_id,)
    ).fetchone()
    
    if not material:
        flash('Learning material not found.', 'danger')
        return redirect(url_for('learn'))
    
    # Get related materials in same topic
    related = db.execute(
        '''SELECT * FROM learning_materials
           WHERE topic = ? AND id != ? AND language_track = ?
           ORDER BY order_index
           LIMIT 5''',
        (material['topic'], material_id, material['language_track'])
    ).fetchall()
    
    return render_template('learn/material.html',
                         material=material,
                         related=related)


# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    db = get_db()
    
    # Get statistics
    total_users = db.execute('SELECT COUNT(*) as count FROM users WHERE role = "student"').fetchone()['count']
    total_questions = db.execute('SELECT COUNT(*) as count FROM questions').fetchone()['count']
    total_attempts = db.execute('SELECT COUNT(*) as count FROM attempts').fetchone()['count']
    
    # Get recent activity
    recent_attempts = db.execute(
        '''SELECT u.username, q.title, a.is_correct, a.attempted_at
           FROM attempts a
           JOIN users u ON a.user_id = u.id
           JOIN questions q ON a.question_id = q.id
           ORDER BY a.attempted_at DESC
           LIMIT 10'''
    ).fetchall()
    
    # Get user analytics
    user_analytics = db.execute(
        '''SELECT us.user_id, u.username, us.xp, us.level, us.streak,
                  COUNT(DISTINCT a.question_id) as questions_attempted,
                  SUM(CASE WHEN a.is_correct = 1 THEN 1 ELSE 0 END) as correct_attempts,
                  COUNT(*) as total_attempts
           FROM user_stats us
           JOIN users u ON us.user_id = u.id
           LEFT JOIN attempts a ON us.user_id = a.user_id
           WHERE u.role = 'student'
           GROUP BY us.user_id, u.username, us.xp, us.level, us.streak
           ORDER BY us.xp DESC
           LIMIT 20'''
    ).fetchall()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_questions=total_questions,
                         total_attempts=total_attempts,
                         recent_attempts=recent_attempts,
                         user_analytics=user_analytics)


@app.route('/admin/questions')
@admin_required
def admin_questions():
    """Manage questions"""
    db = get_db()
    
    # Get filter parameters
    topic = request.args.get('topic', '')
    difficulty = request.args.get('difficulty', '')
    
    subject = request.args.get('subject', '')
    show_inactive = request.args.get('show_inactive', '0') == '1'
    
    query = 'SELECT * FROM questions WHERE 1=1'
    params = []
    
    if topic:
        query += ' AND topic = ?'
        params.append(topic)
    if difficulty:
        query += ' AND difficulty = ?'
        params.append(difficulty)
    if subject:
        query += ' AND subject = ?'
        params.append(subject)
    if not show_inactive:
        query += ' AND is_active = 1'
    
    query += ' ORDER BY subject, topic, difficulty, id DESC'
    
    questions = db.execute(query, params).fetchall()
    
    topics = db.execute('SELECT DISTINCT topic FROM questions ORDER BY topic').fetchall()
    subjects = db.execute('SELECT DISTINCT subject FROM questions WHERE subject IS NOT NULL ORDER BY subject').fetchall()
    difficulties = ['easy', 'medium', 'hard']
    
    # Group questions by subject → topic → difficulty for better organization
    questions_by_subject = {}
    for q in questions:
        subj = q.get('subject', 'Python') or 'Python'
        top = q['topic']
        diff = q['difficulty']
        
        if subj not in questions_by_subject:
            questions_by_subject[subj] = {}
        if top not in questions_by_subject[subj]:
            questions_by_subject[subj][top] = {'easy': [], 'medium': [], 'hard': []}
        
        questions_by_subject[subj][top][diff].append(q)
    
    return render_template('admin/questions.html',
                         questions=questions,
                         questions_by_subject=questions_by_subject,
                         topics=topics,
                         subjects=subjects,
                         difficulties=difficulties,
                         selected_topic=topic,
                         selected_difficulty=difficulty,
                         selected_subject=subject,
                         show_inactive=show_inactive)


@app.route('/admin/question/add', methods=['GET', 'POST'])
@admin_required
def admin_add_question():
    """Add new question"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        question_text = request.form.get('question_text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip()
        explanation = request.form.get('explanation', '').strip()
        difficulty = request.form.get('difficulty', 'easy')
        topic = request.form.get('topic', '').strip()
        language_track = request.form.get('language_track', 'python')
        points = int(request.form.get('points', 10))
        
        if not all([title, question_text, option_a, option_b, option_c, option_d, correct_answer, topic]):
            flash('All fields are required.', 'danger')
            return render_template('admin/add_question.html')
        
        db = get_db()
        try:
            subject = request.form.get('subject', 'Python').strip()
            is_active = request.form.get('is_active', '1') == '1'
            
            db.execute(
                '''INSERT INTO questions (title, question_text, option_a, option_b, option_c, option_d,
                   correct_answer, explanation, difficulty, topic, subject, language_track, points, is_active, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (title, question_text, option_a, option_b, option_c, option_d, correct_answer,
                 explanation, difficulty, topic, subject, language_track, points, 1 if is_active else 0, datetime.datetime.now())
            )
            db.commit()
            flash('Question added successfully!', 'success')
            return redirect(url_for('admin_questions'))
        except Exception as e:
            db.rollback()
            flash(f'Failed to add question: {str(e)}', 'danger')
            return render_template('admin/add_question.html')
    
    return render_template('admin/add_question.html')


@app.route('/admin/question/<int:question_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_question(question_id):
    """Edit existing question"""
    db = get_db()
    question = db.execute('SELECT * FROM questions WHERE id = ?', (question_id,)).fetchone()
    
    if not question:
        flash('Question not found.', 'danger')
        return redirect(url_for('admin_questions'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        question_text = request.form.get('question_text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip()
        explanation = request.form.get('explanation', '').strip()
        difficulty = request.form.get('difficulty', 'easy')
        topic = request.form.get('topic', '').strip()
        language_track = request.form.get('language_track', 'python')
        points = int(request.form.get('points', 10))
        
        if not all([title, question_text, option_a, option_b, option_c, option_d, correct_answer, topic]):
            flash('All fields are required.', 'danger')
            return render_template('admin/edit_question.html', question=question)
        
        try:
            db.execute(
                '''UPDATE questions SET title=?, question_text=?, option_a=?, option_b=?, option_c=?,
                   option_d=?, correct_answer=?, explanation=?, difficulty=?, topic=?, 
                   language_track=?, points=? WHERE id=?''',
                (title, question_text, option_a, option_b, option_c, option_d, correct_answer,
                 explanation, difficulty, topic, language_track, points, question_id)
            )
            db.commit()
            flash('Question updated successfully!', 'success')
            return redirect(url_for('admin_questions'))
        except Exception as e:
            db.rollback()
            flash(f'Failed to update question: {str(e)}', 'danger')
            return render_template('admin/edit_question.html', question=question)
    
    return render_template('admin/edit_question.html', question=question)


@app.route('/admin/question/<int:question_id>/delete', methods=['POST'])
@admin_required
def admin_delete_question(question_id):
    """Delete question"""
    db = get_db()
    try:
        db.execute('DELETE FROM questions WHERE id = ?', (question_id,))
        db.commit()
        flash('Question deleted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Failed to delete question: {str(e)}', 'danger')
    
    return redirect(url_for('admin_questions'))


@app.route('/admin/question/<int:question_id>/toggle', methods=['POST'])
@admin_required
def admin_toggle_question(question_id):
    """Enable/disable a question"""
    db = get_db()
    try:
        question = db.execute('SELECT is_active FROM questions WHERE id = ?', (question_id,)).fetchone()
        if not question:
            flash('Question not found.', 'danger')
            return redirect(url_for('admin_questions'))
        
        new_status = 0 if question['is_active'] else 1
        db.execute('UPDATE questions SET is_active = ? WHERE id = ?', (new_status, question_id))
        db.commit()
        
        status_text = 'enabled' if new_status else 'disabled'
        flash(f'Question {status_text} successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Failed to toggle question: {str(e)}', 'danger')
    return redirect(url_for('admin_questions'))


@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    """Analytics and reporting"""
    db = get_db()
    
    # Overall statistics
    stats = {
        'total_users': db.execute('SELECT COUNT(*) as count FROM users WHERE role="student"').fetchone()['count'],
        'total_questions': db.execute('SELECT COUNT(*) as count FROM questions').fetchone()['count'],
        'total_attempts': db.execute('SELECT COUNT(*) as count FROM attempts').fetchone()['count'],
        'avg_accuracy': db.execute(
            'SELECT AVG(CASE WHEN is_correct=1 THEN 100 ELSE 0 END) as avg FROM attempts'
        ).fetchone()['avg'] or 0
    }
    
    # Topic performance
    topic_performance = db.execute(
        '''SELECT q.topic, COUNT(*) as total_attempts,
                  SUM(CASE WHEN a.is_correct=1 THEN 1 ELSE 0 END) as correct_attempts,
                  AVG(a.xp_earned) as avg_xp
           FROM attempts a
           JOIN questions q ON a.question_id = q.id
           GROUP BY q.topic
           ORDER BY total_attempts DESC'''
    ).fetchall()
    
    # Difficulty performance
    difficulty_performance = db.execute(
        '''SELECT q.difficulty, COUNT(*) as total_attempts,
                  SUM(CASE WHEN a.is_correct=1 THEN 1 ELSE 0 END) as correct_attempts
           FROM attempts a
           JOIN questions q ON a.question_id = q.id
           GROUP BY q.difficulty
           ORDER BY q.difficulty'''
    ).fetchall()
    
    return render_template('admin/analytics.html',
                         stats=stats,
                         topic_performance=topic_performance,
                         difficulty_performance=difficulty_performance)


# ==================== MODULE 1: LEARNING AREA (SUBJECTS → TOPICS → NOTES) ====================

@app.route('/learn/subject/<int:subject_id>')
@login_required
def view_subject(subject_id):
    """View topics in a subject"""
    db = get_db()
    topics = db.execute(
        'SELECT * FROM topics WHERE subject_id = ? ORDER BY order_index, name',
        (subject_id,)
    ).fetchall()
    subject = db.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,)).fetchone()
    
    if not subject:
        flash('Subject not found.', 'danger')
        return redirect(url_for('learn'))
    
    return render_template('learn/subject.html', subject=subject, topics=topics)


@app.route('/learn/topic/<int:topic_id>')
@login_required
def view_topic_notes(topic_id):
    """View notes in a topic"""
    db = get_db()
    notes = db.execute(
        '''SELECT * FROM notes WHERE topic_id = ? AND visibility = 'published'
           ORDER BY order_index, created_at''',
        (topic_id,)
    ).fetchall()
    topic = db.execute(
        'SELECT t.*, s.name as subject_name FROM topics t JOIN subjects s ON t.subject_id = s.id WHERE t.id = ?',
        (topic_id,)
    ).fetchone()
    
    if not topic:
        flash('Topic not found.', 'danger')
        return redirect(url_for('learn'))
    
    return render_template('learn/topic_notes.html', topic=topic, notes=notes)


@app.route('/learn/note/<int:note_id>')
@login_required
def view_note(note_id):
    """View a specific note"""
    db = get_db()
    note = db.execute(
        '''SELECT n.*, t.name as topic_name, t.subject_id, s.name as subject_name
           FROM notes n
           JOIN topics t ON n.topic_id = t.id
           JOIN subjects s ON t.subject_id = s.id
           WHERE n.id = ? AND n.visibility = 'published' ''',
        (note_id,)
    ).fetchone()
    
    if not note:
        flash('Note not found or not published.', 'danger')
        return redirect(url_for('learn'))
    
    return render_template('learn/note.html', note=note)


# ==================== ADMIN: LEARNING AREA MANAGEMENT ====================

@app.route('/admin/subjects')
@admin_required
def admin_subjects():
    """Admin: Manage subjects"""
    db = get_db()
    subjects = db.execute('SELECT * FROM subjects ORDER BY order_index, name').fetchall()
    return render_template('admin/subjects.html', subjects=subjects)


@app.route('/admin/subject/add', methods=['GET', 'POST'])
@admin_required
def admin_add_subject():
    """Admin: Add new subject"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        language_track = request.form.get('language_track', 'python')
        
        if not name:
            flash('Subject name is required.', 'danger')
            return render_template('admin/add_subject.html')
        
        db = get_db()
        try:
            db.execute(
                '''INSERT INTO subjects (name, description, language_track, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?)''',
                (name, description, language_track, datetime.datetime.now(), session['user_id'])
            )
            db.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('admin_subjects'))
        except Exception as e:
            db.rollback()
            flash(f'Failed to add subject: {str(e)}', 'danger')
    
    return render_template('admin/add_subject.html')


@app.route('/admin/topics')
@admin_required
def admin_topics():
    """Admin: Manage topics"""
    db = get_db()
    subject_id = request.args.get('subject_id', '')
    
    query = '''SELECT t.*, s.name as subject_name FROM topics t
               JOIN subjects s ON t.subject_id = s.id'''
    params = []
    
    if subject_id:
        query += ' WHERE t.subject_id = ?'
        params.append(subject_id)
    
    query += ' ORDER BY s.name, t.order_index, t.name'
    topics = db.execute(query, params).fetchall()
    subjects = db.execute('SELECT * FROM subjects ORDER BY name').fetchall()
    
    return render_template('admin/topics.html', topics=topics, subjects=subjects, selected_subject=subject_id)


@app.route('/admin/topic/add', methods=['GET', 'POST'])
@admin_required
def admin_add_topic():
    """Admin: Add new topic"""
    db = get_db()
    subjects = db.execute('SELECT * FROM subjects ORDER BY name').fetchall()
    
    if request.method == 'POST':
        subject_id = request.form.get('subject_id', '').strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not subject_id or not name:
            flash('Subject and topic name are required.', 'danger')
            return render_template('admin/add_topic.html', subjects=subjects)
        
        try:
            db.execute(
                '''INSERT INTO topics (subject_id, name, description, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?)''',
                (subject_id, name, description, datetime.datetime.now(), session['user_id'])
            )
            db.commit()
            flash('Topic added successfully!', 'success')
            return redirect(url_for('admin_topics'))
        except Exception as e:
            db.rollback()
            flash(f'Failed to add topic: {str(e)}', 'danger')
    
    return render_template('admin/add_topic.html', subjects=subjects)


@app.route('/admin/notes')
@admin_required
def admin_notes():
    """Admin: Manage notes"""
    db = get_db()
    topic_id = request.args.get('topic_id', '')
    
    query = '''SELECT n.*, t.name as topic_name, s.name as subject_name
               FROM notes n
               JOIN topics t ON n.topic_id = t.id
               JOIN subjects s ON t.subject_id = s.id'''
    params = []
    
    if topic_id:
        query += ' WHERE n.topic_id = ?'
        params.append(topic_id)
    
    query += ' ORDER BY s.name, t.name, n.order_index, n.title'
    notes = db.execute(query, params).fetchall()
    topics = db.execute(
        '''SELECT t.*, s.name as subject_name FROM topics t
           JOIN subjects s ON t.subject_id = s.id
           ORDER BY s.name, t.name'''
    ).fetchall()
    
    return render_template('admin/notes.html', notes=notes, topics=topics, selected_topic=topic_id)


@app.route('/admin/note/add', methods=['GET', 'POST'])
@admin_required
def admin_add_note():
    """Admin: Add new note"""
    db = get_db()
    topics = db.execute(
        '''SELECT t.*, s.name as subject_name FROM topics t
           JOIN subjects s ON t.subject_id = s.id
           ORDER BY s.name, t.name'''
    ).fetchall()
    
    if request.method == 'POST':
        topic_id = request.form.get('topic_id', '').strip()
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        visibility = request.form.get('visibility', 'published')
        
        if not topic_id or not title or not content:
            flash('Topic, title, and content are required.', 'danger')
            return render_template('admin/add_note.html', topics=topics)
        
        try:
            db.execute(
                '''INSERT INTO notes (topic_id, title, content, visibility, created_at, updated_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (topic_id, title, content, visibility, datetime.datetime.now(), datetime.datetime.now(), session['user_id'])
            )
            db.commit()
            flash('Note added successfully!', 'success')
            return redirect(url_for('admin_notes'))
        except Exception as e:
            db.rollback()
            flash(f'Failed to add note: {str(e)}', 'danger')
    
    return render_template('admin/add_note.html', topics=topics)


@app.route('/admin/note/<int:note_id>/generate', methods=['POST'])
@admin_required
def admin_generate_note(note_id):
    """Admin: Generate note content using AI (placeholder)"""
    db = get_db()
    note = db.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    
    if not note:
        return jsonify({'success': False, 'message': 'Note not found'}), 404
    
    topic = db.execute('SELECT name FROM topics WHERE id = ?', (note['topic_id'],)).fetchone()
    topic_name = topic['name'] if topic else 'Unknown'
    
    # Generate content (placeholder)
    generated_content = generate_note_content(topic_name)
    
    # Update note
    try:
        db.execute(
            'UPDATE notes SET content = ?, updated_at = ? WHERE id = ?',
            (generated_content, datetime.datetime.now(), note_id)
        )
        db.commit()
        
        # Log generation
        log_content_generation('note', note_id, 'placeholder', session['user_id'])
        
        return jsonify({'success': True, 'content': generated_content})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== MODULE 3: TEST/EXAM SYSTEM ====================

@app.route('/tests')
@login_required
def student_tests():
    """Student: View available tests"""
    db = get_db()
    user_id = session['user_id']
    
    # Get tests assigned to this user or all students
    # Show all published tests that are either:
    # 1. Assigned to all students (assigned_to_all = 1), OR
    # 2. Specifically assigned to this user (in test_assignments)
    tests = db.execute(
        '''SELECT DISTINCT t.*, 
                  (SELECT COUNT(*) FROM test_attempts ta WHERE ta.test_id = t.id AND ta.user_id = ?) as attempt_count
           FROM tests t
           LEFT JOIN test_assignments ta ON t.id = ta.test_id AND ta.user_id = ?
           WHERE t.status = 'published'
             AND (t.assigned_to_all = 1 OR ta.user_id IS NOT NULL)
           ORDER BY t.created_at DESC''',
        (user_id, user_id)
    ).fetchall()
    
    return render_template('tests/list.html', tests=tests)


@app.route('/test/<int:test_id>')
@login_required
def view_test(test_id):
    """Student: View test details"""
    db = get_db()
    user_id = session['user_id']
    
    test = db.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    if not test:
        flash('Test not found.', 'danger')
        return redirect(url_for('student_tests'))
    
    # Check if already attempted
    attempt = db.execute(
        'SELECT * FROM test_attempts WHERE test_id = ? AND user_id = ? ORDER BY started_at DESC LIMIT 1',
        (test_id, user_id)
    ).fetchone()
    
    # Get questions count
    question_count = db.execute(
        'SELECT COUNT(*) as count FROM test_questions WHERE test_id = ?',
        (test_id,)
    ).fetchone()['count']
    
    return render_template('tests/view.html', test=test, attempt=attempt, question_count=question_count)


@app.route('/test/<int:test_id>/start', methods=['POST'])
@login_required
def start_test(test_id):
    """Student: Start a test (allows retakes)"""
    db = get_db()
    user_id = session['user_id']
    
    # Check if there's an in-progress attempt
    in_progress = db.execute(
        'SELECT * FROM test_attempts WHERE test_id = ? AND user_id = ? AND status = "in_progress"',
        (test_id, user_id)
    ).fetchone()
    
    if in_progress:
        # Continue existing attempt
        return redirect(url_for('take_test', test_id=test_id))
    
    # Create new test attempt (allows retakes)
    try:
        db.execute(
            '''INSERT INTO test_attempts (test_id, user_id, started_at, status)
               VALUES (?, ?, ?, 'in_progress')''',
            (test_id, user_id, datetime.datetime.now())
        )
        db.commit()
        return redirect(url_for('take_test', test_id=test_id))
    except Exception as e:
        db.rollback()
        flash(f'Failed to start test: {str(e)}', 'danger')
        return redirect(url_for('view_test', test_id=test_id))


@app.route('/test/<int:test_id>/take')
@login_required
def take_test(test_id):
    """Student: Take the test"""
    db = get_db()
    user_id = session['user_id']
    
    # Get active attempt
    attempt = db.execute(
        'SELECT * FROM test_attempts WHERE test_id = ? AND user_id = ? AND status = "in_progress" ORDER BY started_at DESC LIMIT 1',
        (test_id, user_id)
    ).fetchone()
    
    if not attempt:
        flash('No active test attempt found.', 'warning')
        return redirect(url_for('view_test', test_id=test_id))
    
    # Get test questions
    questions = db.execute(
        '''SELECT q.*, tq.points, tq.order_index
           FROM test_questions tq
           JOIN questions q ON tq.question_id = q.id
           WHERE tq.test_id = ?
           ORDER BY tq.order_index''',
        (test_id,)
    ).fetchall()
    
    # Get already answered questions
    answered = db.execute(
        'SELECT question_id, selected_answer FROM test_attempt_answers WHERE test_attempt_id = ?',
        (attempt['id'],)
    ).fetchall()
    answered_dict = {a['question_id']: a['selected_answer'] for a in answered}
    
    test = db.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    
    return render_template('tests/take.html', test=test, questions=questions, attempt=attempt, answered=answered_dict)


@app.route('/test/<int:test_id>/submit_answer', methods=['POST'])
@login_required
def submit_test_answer(test_id):
    """Student: Submit answer for a test question"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400
        
        question_id = data.get('question_id')
        selected_answer = data.get('answer', '').strip()
        
        if not question_id:
            return jsonify({'success': False, 'message': 'Question ID is required'}), 400
        
        if not selected_answer:
            return jsonify({'success': False, 'message': 'Answer is required'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Invalid request: {str(e)}'}), 400
    
    db = get_db()
    user_id = session['user_id']
    
    # Get active attempt
    attempt = db.execute(
        'SELECT * FROM test_attempts WHERE test_id = ? AND user_id = ? AND status = "in_progress" ORDER BY started_at DESC LIMIT 1',
        (test_id, user_id)
    ).fetchone()
    
    if not attempt:
        return jsonify({'success': False, 'message': 'No active test attempt'}), 400
    
    # Get question
    question = db.execute('SELECT * FROM questions WHERE id = ?', (question_id,)).fetchone()
    if not question:
        return jsonify({'success': False, 'message': 'Question not found'}), 404
    
    # Check answer using normalized comparison
    is_correct = compare_answers(selected_answer, question['correct_answer'])
    
    # Additional debug logging
    if app.debug:
        print(f"DEBUG: submit_test_answer - Question ID: {question_id}")
        print(f"DEBUG: Student Answer (raw): {repr(selected_answer)}")
        print(f"DEBUG: Correct Answer (raw): {repr(question['correct_answer'])}")
        print(f"DEBUG: Is Correct: {is_correct}")
    
    # Get points for this question in test
    test_question = db.execute(
        'SELECT points FROM test_questions WHERE test_id = ? AND question_id = ?',
        (test_id, question_id)
    ).fetchone()
    points = test_question['points'] if test_question else 1
    
    points_earned = points if is_correct else 0
    
    # Save or update answer
    existing = db.execute(
        'SELECT id FROM test_attempt_answers WHERE test_attempt_id = ? AND question_id = ?',
        (attempt['id'], question_id)
    ).fetchone()
    
    # Store is_correct as integer (1 or 0) for SQLite compatibility
    is_correct_int = 1 if is_correct else 0
    
    # Normalize selected_answer for storage (A, B, C, D)
    selected_answer_normalized = normalize_answer(selected_answer)
    
    try:
        if existing:
            db.execute(
                'UPDATE test_attempt_answers SET selected_answer = ?, is_correct = ?, points_earned = ? WHERE id = ?',
                (selected_answer_normalized, is_correct_int, points_earned, existing['id'])
            )
            if app.debug:
                print(f"DEBUG: Updated existing answer record {existing['id']}")
                print(f"DEBUG:   Stored: selected_answer='{selected_answer_normalized}', is_correct={is_correct_int}, points={points_earned}")
        else:
            db.execute(
                '''INSERT INTO test_attempt_answers (test_attempt_id, question_id, selected_answer, is_correct, points_earned, answered_at)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (attempt['id'], question_id, selected_answer_normalized, is_correct_int, points_earned, datetime.datetime.now())
            )
            if app.debug:
                print(f"DEBUG: Inserted new answer record for question {question_id}")
                print(f"DEBUG:   Stored: selected_answer='{selected_answer_normalized}', is_correct={is_correct_int}, points={points_earned}")
        
        db.commit()
        
        # Verify the save
        saved = db.execute(
            'SELECT * FROM test_attempt_answers WHERE test_attempt_id = ? AND question_id = ?',
            (attempt['id'], question_id)
        ).fetchone()
        
        if app.debug:
            if saved:
                print(f"DEBUG: Verified saved answer - question_id: {question_id}, selected: '{saved['selected_answer']}', is_correct: {saved['is_correct']}, points: {saved['points_earned']}")
            else:
                print(f"DEBUG: ERROR - Answer was not saved! question_id: {question_id}, attempt_id: {attempt['id']}")
            
    except Exception as e:
        db.rollback()
        if app.debug:
            print(f"DEBUG: Error saving answer: {str(e)}")
        return jsonify({'success': False, 'message': f'Failed to save answer: {str(e)}'}), 500
    
    return jsonify({
        'success': True,
        'is_correct': 1 if is_correct else 0,  # Return as integer for consistency with SQLite
        'correct_answer': question['correct_answer'],
        'selected_answer': selected_answer_normalized,  # Return normalized for consistency
        'explanation': question['explanation'] if question['explanation'] else '',
        'points_earned': points_earned,
        'total_points': points,
        'message': 'Answer saved successfully' + (' - Correct!' if is_correct else ' - Incorrect')
    })


@app.route('/test/<int:test_id>/finish', methods=['POST'])
@login_required
def finish_test(test_id):
    """Student: Submit and finish test"""
    db = get_db()
    user_id = session['user_id']
    
    # Get active attempt
    attempt = db.execute(
        'SELECT * FROM test_attempts WHERE test_id = ? AND user_id = ? AND status = "in_progress" ORDER BY started_at DESC LIMIT 1',
        (test_id, user_id)
    ).fetchone()
    
    if not attempt:
        flash('No active test attempt found.', 'danger')
        return redirect(url_for('view_test', test_id=test_id))
    
    # CRITICAL FIX: Also capture answers from form submission (backup in case AJAX failed)
    # Get all test questions to match form data
    test_questions = db.execute(
        'SELECT question_id FROM test_questions WHERE test_id = ?',
        (test_id,)
    ).fetchall()
    
    # Process form data if present (backup for answers not saved via AJAX)
    form_answers_saved = 0
    for tq in test_questions:
        question_id = tq['question_id']
        form_answer_key = f'answer_{question_id}'
        form_answer = request.form.get(form_answer_key, '').strip()
        
        if form_answer:
            # Check if answer already exists in database
            existing = db.execute(
                'SELECT id FROM test_attempt_answers WHERE test_attempt_id = ? AND question_id = ?',
                (attempt['id'], question_id)
            ).fetchone()
            
            if not existing:
                # Answer not saved via AJAX, save it now from form
                question = db.execute('SELECT correct_answer FROM questions WHERE id = ?', (question_id,)).fetchone()
                if question:
                    is_correct = compare_answers(form_answer, question['correct_answer'])
                    test_q = db.execute('SELECT points FROM test_questions WHERE test_id = ? AND question_id = ?', 
                                       (test_id, question_id)).fetchone()
                    points = test_q['points'] if test_q else 1
                    points_earned = points if is_correct else 0
                    
                    db.execute(
                        '''INSERT INTO test_attempt_answers (test_attempt_id, question_id, selected_answer, is_correct, points_earned, answered_at)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (attempt['id'], question_id, normalize_answer(form_answer), 1 if is_correct else 0, points_earned, datetime.datetime.now())
                    )
                    form_answers_saved += 1
                    if app.debug:
                        print(f"DEBUG: Saved answer from form for question {question_id}: '{form_answer}' -> is_correct={is_correct}")
    
    if form_answers_saved > 0:
        db.commit()
        if app.debug:
            print(f"DEBUG: Saved {form_answers_saved} answers from form submission")
    
    # Calculate score - re-verify all answers to ensure correctness
    answers = db.execute(
        'SELECT * FROM test_attempt_answers WHERE test_attempt_id = ?',
        (attempt['id'],)
    ).fetchall()
    
    if app.debug:
        print(f"DEBUG: finish_test - Found {len(answers)} saved answers")
        print(f"DEBUG: request.form keys: {list(request.form.keys())}")
        for key in request.form.keys():
            if key.startswith('answer_'):
                print(f"DEBUG:   Form answer {key}: {request.form.get(key)}")
    
    # Re-verify all answers to ensure correctness (double-check)
    for answer in answers:
        question = db.execute('SELECT correct_answer FROM questions WHERE id = ?', (answer['question_id'],)).fetchone()
        if question:
            # Use normalized comparison function
            selected_ans = answer['selected_answer']
            correct_ans = question['correct_answer']
            
            # Handle None or empty selected_answer
            if not selected_ans or selected_ans == 'None' or selected_ans == '':
                if app.debug:
                    print(f"DEBUG: WARNING - Answer {answer['id']} (question_id: {answer['question_id']}) has empty selected_answer: {repr(selected_ans)}")
                should_be_correct = False
            else:
                should_be_correct = compare_answers(selected_ans, correct_ans)
            
            # Update if mismatch found
            current_is_correct = bool(answer['is_correct'] == 1 or answer['is_correct'] is True)
            
            if app.debug:
                print(f"DEBUG: finish_test - Re-verifying answer {answer['id']} (question_id: {answer['question_id']})")
                print(f"DEBUG:   Current is_correct: {current_is_correct}")
                print(f"DEBUG:   Should be correct: {should_be_correct}")
                print(f"DEBUG:   Selected (raw): {repr(selected_ans)}")
                print(f"DEBUG:   Correct (raw): {repr(correct_ans)}")
            
            if current_is_correct != should_be_correct:
                points = answer['points_earned'] if answer['points_earned'] else 0
                if should_be_correct:
                    # Get points for this question
                    test_q = db.execute('SELECT points FROM test_questions WHERE test_id = ? AND question_id = ?', 
                                       (test_id, answer['question_id'])).fetchone()
                    points = test_q['points'] if test_q else 1
                else:
                    points = 0
                
                db.execute(
                    'UPDATE test_attempt_answers SET is_correct = ?, points_earned = ? WHERE id = ?',
                    (1 if should_be_correct else 0, points, answer['id'])
                )
                if app.debug:
                    print(f"DEBUG: Fixed answer {answer['id']} - was {current_is_correct}, should be {should_be_correct}")
    
    # Recalculate after fixes
    db.commit()
    answers = db.execute('SELECT * FROM test_attempt_answers WHERE test_attempt_id = ?', (attempt['id'],)).fetchall()
    
    # Get total questions in test (not just answered)
    total_questions_in_test = db.execute(
        'SELECT COUNT(*) as count FROM test_questions WHERE test_id = ?',
        (test_id,)
    ).fetchone()['count']
    
    # Get max possible score
    max_score = db.execute(
        'SELECT SUM(points) as total FROM test_questions WHERE test_id = ?',
        (test_id,)
    ).fetchone()['total'] or total_questions_in_test
    
    # Count correct answers from saved answers (handle both int and bool)
    correct_answers = sum(1 for a in answers if int(a['is_correct']) == 1)
    total_score = sum(int(a['points_earned'] or 0) for a in answers)
    
    # Use total questions in test, not just answered ones
    total_questions = total_questions_in_test
    
    if app.debug:
        print(f"DEBUG: finish_test - Final Score Calculation:")
        print(f"DEBUG:   Total questions in test: {total_questions_in_test}")
        print(f"DEBUG:   Total answers saved: {len(answers)}")
        print(f"DEBUG:   Correct answers: {correct_answers}")
        print(f"DEBUG:   Total score: {total_score}")
        print(f"DEBUG:   Max possible score: {max_score}")
        for a in answers:
            print(f"DEBUG:     Answer {a['question_id']}: selected='{a['selected_answer']}', is_correct={a['is_correct']}, points={a['points_earned']}")
    
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    # Update attempt
    db.execute(
        '''UPDATE test_attempts SET submitted_at = ?, status = 'completed', 
           score = ?, total_questions = ?, correct_answers = ? WHERE id = ?''',
        (datetime.datetime.now(), int(percentage), total_questions, correct_answers, attempt['id'])
    )
    db.commit()
    
    flash(f'Test submitted! Your score: {percentage:.1f}%', 'success')
    return redirect(url_for('test_results', test_id=test_id))


@app.route('/test/<int:test_id>/results')
@login_required
def test_results(test_id):
    """Student: View test results (shows latest completed attempt)"""
    db = get_db()
    user_id = session['user_id']
    
    # Get latest completed attempt (or allow viewing any attempt)
    attempt_id = request.args.get('attempt_id', type=int)
    
    if attempt_id:
        attempt = db.execute(
            'SELECT * FROM test_attempts WHERE id = ? AND user_id = ? AND test_id = ?',
            (attempt_id, user_id, test_id)
        ).fetchone()
    else:
        attempt = db.execute(
            'SELECT * FROM test_attempts WHERE test_id = ? AND user_id = ? AND status = "completed" ORDER BY submitted_at DESC LIMIT 1',
            (test_id, user_id)
        ).fetchone()
    
    if not attempt:
        flash('Test results not found.', 'danger')
        return redirect(url_for('view_test', test_id=test_id))
    
    # Get all test questions and their answers
    # First get all questions in the test
    # CRITICAL: Use tq.question_id (not q.id) to match saved answers
    test_questions = db.execute(
        '''SELECT tq.question_id, tq.points as question_points, tq.order_index,
                  q.id, q.title, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d, 
                  q.correct_answer, q.explanation, q.difficulty
           FROM test_questions tq
           JOIN questions q ON tq.question_id = q.id
           WHERE tq.test_id = ?
           ORDER BY tq.order_index''',
        (test_id,)
    ).fetchall()
    
    # Get all saved answers for this attempt
    saved_answers = db.execute(
        'SELECT * FROM test_attempt_answers WHERE test_attempt_id = ?',
        (attempt['id'],)
    ).fetchall()
    saved_answers_dict = {a['question_id']: a for a in saved_answers}
    
    if app.debug:
        print(f"DEBUG: test_results - Attempt ID: {attempt['id']}")
        print(f"DEBUG:   Found {len(saved_answers)} saved answers")
        for a in saved_answers:
            print(f"DEBUG:     Question {a['question_id']}: selected='{a['selected_answer']}', is_correct={a['is_correct']}")
    
    # Combine test questions with their answers
    answers = []
    if app.debug:
        print(f"DEBUG: test_results - Processing {len(test_questions)} questions")
        print(f"DEBUG:   Saved answers dict has {len(saved_answers_dict)} entries")
        print(f"DEBUG:   Saved answers: {[(a['question_id'], a['selected_answer']) for a in saved_answers]}")
    
    for tq in test_questions:
        question_id = tq['question_id']
        answer_data = saved_answers_dict.get(question_id)
        if answer_data:
            # Merge question data with answer data
            combined = dict(tq)
            selected_ans = answer_data['selected_answer']
            
            # Handle None or empty selected_answer
            if not selected_ans or selected_ans == 'None' or selected_ans == '':
                if app.debug:
                    print(f"DEBUG: WARNING - Answer data for question {question_id} has empty selected_answer: {repr(selected_ans)}")
                selected_ans = None
            
            combined.update({
                'selected_answer': selected_ans,
                'is_correct': answer_data['is_correct'],
                'points_earned': answer_data['points_earned'],
                'answered_at': answer_data['answered_at'] if 'answered_at' in answer_data.keys() else None
            })
            answers.append(combined)
            
            if app.debug:
                print(f"DEBUG: test_results - Question {question_id}: selected='{selected_ans}', is_correct={answer_data['is_correct']}, points={answer_data['points_earned']}")
        else:
            # Question not answered - still show it
            combined = dict(tq)
            combined.update({
                'selected_answer': None,
                'is_correct': 0,
                'points_earned': 0,
                'answered_at': None
            })
            answers.append(combined)
            
            if app.debug:
                print(f"DEBUG: test_results - Question {question_id}: NO ANSWER SAVED")
    
    # Get all attempts for this test (for retake history)
    all_attempts = db.execute(
        'SELECT * FROM test_attempts WHERE test_id = ? AND user_id = ? ORDER BY submitted_at DESC, started_at DESC',
        (test_id, user_id)
    ).fetchall()
    
    test = db.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    
    return render_template('tests/results.html', test=test, attempt=attempt, answers=answers, all_attempts=all_attempts)


# ==================== ADMIN: TEST MANAGEMENT ====================

@app.route('/admin/tests')
@admin_required
def admin_tests():
    """Admin: Manage tests"""
    db = get_db()
    tests = db.execute(
        '''SELECT t.*, 
                  (SELECT COUNT(*) FROM test_questions WHERE test_id = t.id) as question_count,
                  (SELECT COUNT(*) FROM test_attempts WHERE test_id = t.id) as attempt_count
           FROM tests t
           ORDER BY t.created_at DESC'''
    ).fetchall()
    return render_template('admin/tests.html', tests=tests)


@app.route('/admin/test/add', methods=['GET', 'POST'])
@admin_required
def admin_add_test():
    """Admin: Create new test"""
    db = get_db()
    subjects = db.execute('SELECT * FROM subjects ORDER BY name').fetchall()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        subject_id = request.form.get('subject_id', '') or None
        time_limit = int(request.form.get('time_limit_minutes', 60))
        passing_score = int(request.form.get('passing_score', 50))
        status = request.form.get('status', 'draft')
        assigned_to_all = 1 if request.form.get('assigned_to_all') == 'on' else 0
        
        if not title:
            flash('Test title is required.', 'danger')
            return render_template('admin/add_test.html', subjects=subjects)
        
        try:
            cursor = db.execute(
                '''INSERT INTO tests (title, description, subject_id, time_limit_minutes, passing_score, 
                   status, assigned_to_all, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (title, description, subject_id, time_limit, passing_score, status, assigned_to_all,
                 datetime.datetime.now(), session['user_id'])
            )
            test_id = cursor.lastrowid
            
            # Add questions if provided
            question_ids = request.form.getlist('question_ids')
            for idx, qid in enumerate(question_ids):
                if qid:
                    db.execute(
                        'INSERT INTO test_questions (test_id, question_id, order_index, points) VALUES (?, ?, ?, ?)',
                        (test_id, int(qid), idx, 1)
                    )
            
            db.commit()
            flash('Test created successfully!', 'success')
            return redirect(url_for('admin_edit_test', test_id=test_id))
        except Exception as e:
            db.rollback()
            flash(f'Failed to create test: {str(e)}', 'danger')
    
    # Get questions for selection
    questions = db.execute('SELECT * FROM questions ORDER BY topic, difficulty').fetchall()
    return render_template('admin/add_test.html', subjects=subjects, questions=questions)


@app.route('/admin/test/<int:test_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_test(test_id):
    """Admin: Edit test"""
    db = get_db()
    test = db.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    
    if not test:
        flash('Test not found.', 'danger')
        return redirect(url_for('admin_tests'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        subject_id = request.form.get('subject_id', '') or None
        time_limit = int(request.form.get('time_limit_minutes', 60))
        passing_score = int(request.form.get('passing_score', 50))
        status = request.form.get('status', 'draft')
        assigned_to_all = 1 if request.form.get('assigned_to_all') == 'on' else 0
        
        try:
            db.execute(
                '''UPDATE tests SET title = ?, description = ?, subject_id = ?, time_limit_minutes = ?,
                   passing_score = ?, status = ?, assigned_to_all = ? WHERE id = ?''',
                (title, description, subject_id, time_limit, passing_score, status, assigned_to_all, test_id)
            )
            
            # Update questions
            question_ids = request.form.getlist('question_ids')
            # Remove old questions
            db.execute('DELETE FROM test_questions WHERE test_id = ?', (test_id,))
            # Add new questions
            for idx, qid in enumerate(question_ids):
                if qid:
                    db.execute(
                        'INSERT INTO test_questions (test_id, question_id, order_index, points) VALUES (?, ?, ?, ?)',
                        (test_id, int(qid), idx, 1)
                    )
            
            db.commit()
            flash('Test updated successfully!', 'success')
            return redirect(url_for('admin_tests'))
        except Exception as e:
            db.rollback()
            flash(f'Failed to update test: {str(e)}', 'danger')
    
    # Get current questions
    test_questions = db.execute(
        'SELECT question_id FROM test_questions WHERE test_id = ? ORDER BY order_index',
        (test_id,)
    ).fetchall()
    selected_question_ids = [q['question_id'] for q in test_questions]
    
    subjects = db.execute('SELECT * FROM subjects ORDER BY name').fetchall()
    # Order questions by difficulty (hard first) to make it easier to add challenging questions
    questions = db.execute('SELECT * FROM questions ORDER BY CASE difficulty WHEN "hard" THEN 1 WHEN "advanced" THEN 2 WHEN "medium" THEN 3 WHEN "intermediate" THEN 4 ELSE 5 END, topic').fetchall()
    
    # Get assigned students
    assigned_students = db.execute(
        '''SELECT u.id, u.username, ta.assigned_at
           FROM test_assignments ta
           JOIN users u ON ta.user_id = u.id
           WHERE ta.test_id = ?''',
        (test_id,)
    ).fetchall()
    
    # Get all students for assignment
    all_students = db.execute(
        'SELECT id, username FROM users WHERE role = "student" ORDER BY username'
    ).fetchall()
    
    return render_template('admin/edit_test.html', test=test, subjects=subjects, questions=questions,
                         selected_question_ids=selected_question_ids, assigned_students=assigned_students,
                         all_students=all_students)


@app.route('/admin/test/<int:test_id>/assign', methods=['POST'])
@admin_required
def admin_assign_test(test_id):
    """Admin: Assign test to students"""
    db = get_db()
    user_ids_str = request.form.get('user_ids', '').strip()
    
    try:
        if user_ids_str:
            # Parse comma-separated user IDs
            user_ids = [int(uid.strip()) for uid in user_ids_str.split(',') if uid.strip().isdigit()]
            
            for user_id in user_ids:
                db.execute(
                    'INSERT OR IGNORE INTO test_assignments (test_id, user_id, assigned_at, assigned_by) VALUES (?, ?, ?, ?)',
                    (test_id, user_id, datetime.datetime.now(), session['user_id'])
                )
            db.commit()
            flash(f'Test assigned to {len(user_ids)} student(s) successfully!', 'success')
        else:
            flash('Please provide user IDs.', 'warning')
    except Exception as e:
        db.rollback()
        flash(f'Failed to assign test: {str(e)}', 'danger')
    
    return redirect(url_for('admin_edit_test', test_id=test_id))


@app.route('/admin/test/<int:test_id>/results')
@admin_required
def admin_test_results(test_id):
    """Admin: View all test results"""
    db = get_db()
    test = db.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    
    attempts = db.execute(
        '''SELECT ta.*, u.username
           FROM test_attempts ta
           JOIN users u ON ta.user_id = u.id
           WHERE ta.test_id = ? AND ta.status = 'completed'
           ORDER BY ta.submitted_at DESC''',
        (test_id,)
    ).fetchall()
    
    return render_template('admin/test_results.html', test=test, attempts=attempts)


# ==================== MODULE 4: ROLE MANAGEMENT ====================

@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin: View all users"""
    db = get_db()
    users = db.execute(
        '''SELECT u.*, us.xp, us.level, COALESCE(u.is_super_admin, 0) as is_super_admin
           FROM users u
           LEFT JOIN user_stats us ON u.id = us.user_id
           ORDER BY u.role, u.username'''
    ).fetchall()
    
    # Check if current user is super admin
    current_user = db.execute(
        'SELECT is_super_admin FROM users WHERE id = ?',
        (session['user_id'],)
    ).fetchone()
    # Handle sqlite3.Row objects (they don't have .get() method)
    is_super_admin = False
    if current_user:
        is_super_admin = current_user['is_super_admin'] if 'is_super_admin' in current_user.keys() else 0
    
    return render_template('admin/users.html', users=users, is_super_admin=is_super_admin)


@app.route('/admin/user/<int:user_id>/promote', methods=['POST'])
@super_admin_required
def admin_promote_user(user_id):
    """Super Admin: Promote user to admin"""
    db = get_db()
    try:
        db.execute('UPDATE users SET role = "admin" WHERE id = ?', (user_id,))
        db.commit()
        flash('User promoted to admin successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Failed to promote user: {str(e)}', 'danger')
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/demote', methods=['POST'])
@super_admin_required
def admin_demote_user(user_id):
    """Super Admin: Demote admin to student"""
    db = get_db()
    try:
        db.execute('UPDATE users SET role = "student", is_super_admin = 0 WHERE id = ?', (user_id,))
        db.commit()
        flash('Admin demoted to student successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Failed to demote user: {str(e)}', 'danger')
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/make_super_admin', methods=['POST'])
@super_admin_required
def admin_make_super_admin(user_id):
    """Super Admin: Make user super admin"""
    db = get_db()
    try:
        db.execute('UPDATE users SET role = "admin", is_super_admin = 1 WHERE id = ?', (user_id,))
        db.commit()
        flash('User made super admin successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Failed to make super admin: {str(e)}', 'danger')
    return redirect(url_for('admin_users'))


# ==================== MODULE 5: COURSES/ENROLLMENT ====================

@app.route('/courses')
@login_required
def student_courses():
    """Student: View enrolled courses"""
    db = get_db()
    user_id = session['user_id']
    
    enrolled = db.execute(
        '''SELECT c.*, ce.enrolled_at, ce.status
           FROM courses c
           JOIN course_enrollments ce ON c.id = ce.course_id
           WHERE ce.user_id = ? AND ce.status = 'active'
           ORDER BY ce.enrolled_at DESC''',
        (user_id,)
    ).fetchall()
    
    # Get available courses
    available = db.execute(
        '''SELECT c.* FROM courses c
           WHERE c.status = 'active'
             AND c.id NOT IN (SELECT course_id FROM course_enrollments WHERE user_id = ?)
           ORDER BY c.name''',
        (user_id,)
    ).fetchall()
    
    return render_template('courses/list.html', enrolled=enrolled, available=available)


@app.route('/admin/courses')
@admin_required
def admin_courses():
    """Admin: Manage courses"""
    db = get_db()
    courses = db.execute(
        '''SELECT c.*, 
                  (SELECT COUNT(*) FROM course_enrollments WHERE course_id = c.id AND status = 'active') as student_count
           FROM courses c
           ORDER BY c.created_at DESC'''
    ).fetchall()
    return render_template('admin/courses.html', courses=courses)


@app.route('/admin/course/add', methods=['GET', 'POST'])
@admin_required
def admin_add_course():
    """Admin: Create new course"""
    db = get_db()
    subjects = db.execute('SELECT * FROM subjects ORDER BY name').fetchall()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'active')
        subject_ids = request.form.getlist('subject_ids')
        
        if not name:
            flash('Course name is required.', 'danger')
            return render_template('admin/add_course.html', subjects=subjects)
        
        try:
            cursor = db.execute(
                'INSERT INTO courses (name, description, status, created_at, created_by) VALUES (?, ?, ?, ?, ?)',
                (name, description, status, datetime.datetime.now(), session['user_id'])
            )
            course_id = cursor.lastrowid
            
            # Add subjects
            for idx, subject_id in enumerate(subject_ids):
                if subject_id:
                    db.execute(
                        'INSERT INTO course_subjects (course_id, subject_id, order_index) VALUES (?, ?, ?)',
                        (course_id, int(subject_id), idx)
                    )
            
            db.commit()
            flash('Course created successfully!', 'success')
            return redirect(url_for('admin_courses'))
        except Exception as e:
            db.rollback()
            flash(f'Failed to create course: {str(e)}', 'danger')
    
    return render_template('admin/add_course.html', subjects=subjects)


@app.route('/admin/course/<int:course_id>/enroll', methods=['POST'])
@admin_required
def admin_enroll_students(course_id):
    """Admin: Enroll students in course"""
    db = get_db()
    user_ids_str = request.form.get('user_ids', '').strip()
    
    try:
        if user_ids_str:
            # Parse comma-separated user IDs
            user_ids = [int(uid.strip()) for uid in user_ids_str.split(',') if uid.strip().isdigit()]
            
            for user_id in user_ids:
                db.execute(
                    'INSERT OR IGNORE INTO course_enrollments (course_id, user_id, enrolled_at, enrolled_by) VALUES (?, ?, ?, ?)',
                    (course_id, user_id, datetime.datetime.now(), session['user_id'])
                )
            db.commit()
            flash(f'{len(user_ids)} student(s) enrolled successfully!', 'success')
        else:
            flash('Please provide user IDs.', 'warning')
    except Exception as e:
        db.rollback()
        flash(f'Failed to enroll students: {str(e)}', 'danger')
    
    return redirect(url_for('admin_edit_course', course_id=course_id))


@app.route('/admin/course/<int:course_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_course(course_id):
    """Admin: Edit course"""
    db = get_db()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('admin_courses'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'active')
        subject_ids = request.form.getlist('subject_ids')
        
        try:
            db.execute(
                'UPDATE courses SET name = ?, description = ?, status = ? WHERE id = ?',
                (name, description, status, course_id)
            )
            
            # Update subjects
            db.execute('DELETE FROM course_subjects WHERE course_id = ?', (course_id,))
            for idx, subject_id in enumerate(subject_ids):
                if subject_id:
                    db.execute(
                        'INSERT INTO course_subjects (course_id, subject_id, order_index) VALUES (?, ?, ?)',
                        (course_id, int(subject_id), idx)
                    )
            
            db.commit()
            flash('Course updated successfully!', 'success')
            return redirect(url_for('admin_courses'))
        except Exception as e:
            db.rollback()
            flash(f'Failed to update course: {str(e)}', 'danger')
    
    # Get current subjects
    course_subjects = db.execute(
        'SELECT subject_id FROM course_subjects WHERE course_id = ? ORDER BY order_index',
        (course_id,)
    ).fetchall()
    selected_subject_ids = [s['subject_id'] for s in course_subjects]
    
    subjects = db.execute('SELECT * FROM subjects ORDER BY name').fetchall()
    enrolled_students = db.execute(
        '''SELECT u.id, u.username, ce.enrolled_at
           FROM course_enrollments ce
           JOIN users u ON ce.user_id = u.id
           WHERE ce.course_id = ? AND ce.status = 'active' ''',
        (course_id,)
    ).fetchall()
    
    # Get all students for enrollment
    all_students = db.execute(
        'SELECT id, username FROM users WHERE role = "student" ORDER BY username'
    ).fetchall()
    
    return render_template('admin/edit_course.html', course=course, subjects=subjects,
                         selected_subject_ids=selected_subject_ids, enrolled_students=enrolled_students,
                         all_students=all_students)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db = get_db()
    db.rollback()
    return render_template('errors/500.html'), 500


# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    # Create default super admin user if not exists
    db = get_db()
    admin = db.execute('SELECT id FROM users WHERE role="admin"').fetchone()
    if not admin:
        hashed = generate_password_hash('admin123')
        cursor = db.execute(
            '''INSERT INTO users (username, email, password, role, is_super_admin, created_at)
               VALUES (?, ?, ?, 'admin', 1, ?)''',
            ('admin', 'admin@codingapp.com', hashed, datetime.datetime.now())
        )
        db.commit()
        print("Default super admin user created: username='admin', password='admin123'")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
