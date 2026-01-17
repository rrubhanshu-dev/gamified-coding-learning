"""
Business logic for XP, levels, badges, and stats
"""

from datetime import datetime, date
from database import get_db
import math


def calculate_xp(is_correct, difficulty, base_points=10):
    """Calculate XP based on answer correctness and difficulty"""
    difficulty_multipliers = {
        'easy': 1.0,
        'medium': 1.5,
        'hard': 2.0
    }
    
    multiplier = difficulty_multipliers.get(difficulty.lower(), 1.0)
    
    if is_correct:
        xp = int(base_points * multiplier)
    else:
        xp = int(base_points * 0.1)
    
    return xp


def check_level_up(current_xp):
    """Calculate level based on XP"""
    level = int(math.sqrt(current_xp / 100)) + 1
    return max(1, level)


def get_xp_for_level(level):
    """Get minimum XP required for a given level"""
    if level <= 1:
        return 0
    return int((level - 1) ** 2 * 100)


def get_xp_for_next_level(current_level):
    """Get XP required for next level"""
    return get_xp_for_level(current_level + 1)


def update_streak(user_id):
    """Update user's daily streak"""
    db = get_db()
    today = date.today()
    
    user_stats = db.execute(
        'SELECT streak, last_activity_date FROM user_stats WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    
    if not user_stats:
        db.execute(
            'INSERT INTO user_stats (user_id, streak, last_activity_date) VALUES (?, 1, ?)',
            (user_id, today)
        )
        db.commit()
        return
    
    last_activity = user_stats['last_activity_date']
    current_streak = user_stats['streak'] or 0
    
    if last_activity:
        if isinstance(last_activity, str):
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d').date()
        
        days_diff = (today - last_activity).days
        
        if days_diff == 0:
            pass
        elif days_diff == 1:
            current_streak += 1
        else:
            current_streak = 1
    else:
        current_streak = 1
    
    db.execute(
        'UPDATE user_stats SET streak = ?, last_activity_date = ? WHERE user_id = ?',
        (current_streak, today, user_id)
    )
    db.commit()


def check_badge_unlock(user_id, current_xp, current_level):
    """Check if user qualifies for any new badges"""
    db = get_db()
    unlocked_badges = []
    
    user_stats = db.execute(
        'SELECT streak FROM user_stats WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    
    current_streak = user_stats['streak'] if user_stats else 0
    
    all_badges = db.execute(
        '''SELECT id, name, badge_type, requirement_value
           FROM badges
           WHERE id NOT IN (SELECT badge_id FROM user_badges WHERE user_id = ?)''',
        (user_id,)
    ).fetchall()
    
    for badge in all_badges:
        badge_type = badge['badge_type']
        requirement = badge['requirement_value']
        
        unlocked = False
        
        if badge_type == 'level' and current_level >= requirement:
            unlocked = True
        elif badge_type == 'xp' and current_xp >= requirement:
            unlocked = True
        elif badge_type == 'streak' and current_streak >= requirement:
            unlocked = True
        elif badge_type == 'first_attempt':
            attempts = db.execute(
                'SELECT COUNT(*) as count FROM attempts WHERE user_id = ?',
                (user_id,)
            ).fetchone()
            if attempts and attempts['count'] >= requirement:
                unlocked = True
        
        if unlocked:
            db.execute(
                'INSERT INTO user_badges (user_id, badge_id, earned_at) VALUES (?, ?, ?)',
                (user_id, badge['id'], datetime.now())
            )
            unlocked_badges.append(badge['name'])
    
    if unlocked_badges:
        db.commit()
    
    return unlocked_badges


def get_streak_bonus(streak):
    """Calculate XP bonus based on streak"""
    if streak >= 30:
        return 0.2
    elif streak >= 14:
        return 0.15
    elif streak >= 7:
        return 0.10
    return 0


# ==================== QUESTION COMPLETION ====================

def check_question_completion(user_id, question_id):
    """Check if user has already correctly answered this question"""
    try:
        db = get_db()
        completion = db.execute(
            'SELECT first_correct_at FROM question_completions WHERE user_id = ? AND question_id = ? AND first_correct_at IS NOT NULL',
            (user_id, question_id)
        ).fetchone()
        return completion is not None
    except Exception as e:
        print(f"Error in check_question_completion: {str(e)}")
        return False


def record_question_completion(user_id, question_id, is_correct):
    """Record question completion status"""
    try:
        db = get_db()
        
        completion = db.execute(
            'SELECT * FROM question_completions WHERE user_id = ? AND question_id = ?',
            (user_id, question_id)
        ).fetchone()
        
        if completion:
            db.execute(
                'UPDATE question_completions SET total_attempts = total_attempts + 1 WHERE user_id = ? AND question_id = ?',
                (user_id, question_id)
            )
            if is_correct and not completion['first_correct_at']:
                db.execute(
                    'UPDATE question_completions SET first_correct_at = ? WHERE user_id = ? AND question_id = ?',
                    (datetime.now(), user_id, question_id)
                )
        else:
            db.execute(
                '''INSERT INTO question_completions (user_id, question_id, first_correct_at, total_attempts)
                   VALUES (?, ?, ?, 1)''',
                (user_id, question_id, datetime.now() if is_correct else None, 1)
            )
        
        db.commit()
    except Exception as e:
        print(f"Error in record_question_completion: {str(e)}")
        try:
            db.rollback()
        except:
            pass


def should_award_xp(user_id, question_id, is_correct):
    """Determine if XP should be awarded for this attempt"""
    if not is_correct:
        return True, "participation"
    
    if check_question_completion(user_id, question_id):
        return False, "already_completed"
    
    return True, "first_correct"


# ==================== CONTENT GENERATION ====================

def generate_note_content(topic_name, difficulty='beginner'):
    """Placeholder function for AI-generated notes"""
    content = f"""
    <h2>Introduction to {topic_name}</h2>
    <p>This is a placeholder for AI-generated content about <strong>{topic_name}</strong>.</p>
    <h3>Key Concepts</h3>
    <ul>
        <li>Concept 1: Understanding the basics</li>
        <li>Concept 2: Practical applications</li>
        <li>Concept 3: Advanced techniques</li>
    </ul>
    <p><em>Note: This content was generated using placeholder logic. In production, this would use AI APIs.</em></p>
    """
    return content


def generate_question_content(topic_name, difficulty='easy'):
    """Placeholder function for AI-generated questions"""
    return {
        'title': f'Sample Question about {topic_name}',
        'question_text': f'What is the main concept of {topic_name}?',
        'option_a': 'Option A',
        'option_b': 'Option B',
        'option_c': 'Option C',
        'option_d': 'Option D',
        'correct_answer': 'A',
        'explanation': f'This is a placeholder explanation for {topic_name}.',
        'difficulty': difficulty,
        'topic': topic_name,
        'points': 10 if difficulty == 'easy' else (15 if difficulty == 'medium' else 20)
    }


def log_content_generation(content_type, content_id, method='placeholder', user_id=None):
    """Log content generation for tracking"""
    db = get_db()
    try:
        db.execute(
            '''INSERT INTO content_generation_log (content_type, content_id, generation_method, generated_at, generated_by)
               VALUES (?, ?, ?, ?, ?)''',
            (content_type, content_id, method, datetime.now(), user_id)
        )
        db.commit()
    except Exception as e:
        print(f"Error logging content generation: {str(e)}")


# ==================== STATS & UTILITIES ====================

def get_user_stats(user_id):
    """Get comprehensive user statistics"""
    db = get_db()
    
    stats = db.execute(
        '''SELECT xp, level, streak, last_activity_date
           FROM user_stats WHERE user_id = ?''',
        (user_id,)
    ).fetchone()
    
    if not stats:
        xp_for_next = get_xp_for_next_level(1)
        return {
            'xp': 0,
            'level': 1,
            'streak': 0,
            'accuracy': 0,
            'total_attempts': 0,
            'correct_attempts': 0,
            'questions_attempted': 0,
            'xp_for_next_level': xp_for_next,
            'xp_needed': xp_for_next,
            'xp_progress': 0,
            'xp_range': xp_for_next - get_xp_for_level(1)
        }
    
    attempts_stats = db.execute(
        '''SELECT COUNT(*) as total_attempts,
                  SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_attempts,
                  COUNT(DISTINCT question_id) as questions_attempted
           FROM attempts WHERE user_id = ?''',
        (user_id,)
    ).fetchone()
    
    total_attempts = attempts_stats['total_attempts'] or 0
    correct_attempts = attempts_stats['correct_attempts'] or 0
    questions_attempted = attempts_stats['questions_attempted'] or 0
    
    accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    current_xp = stats['xp']
    current_level = stats['level']
    xp_for_next = get_xp_for_next_level(current_level)
    xp_needed = xp_for_next - current_xp
    
    return {
        'xp': current_xp,
        'level': current_level,
        'streak': stats['streak'] or 0,
        'accuracy': round(accuracy, 2),
        'total_attempts': total_attempts,
        'correct_attempts': correct_attempts,
        'questions_attempted': questions_attempted,
        'xp_for_next_level': xp_for_next,
        'xp_needed': max(0, xp_needed),
        'xp_progress': current_xp - get_xp_for_level(current_level),
        'xp_range': xp_for_next - get_xp_for_level(current_level)
    }


def get_accuracy_percentage(user_id):
    """Get user's overall accuracy percentage"""
    db = get_db()
    result = db.execute(
        '''SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
           FROM attempts WHERE user_id = ?''',
        (user_id,)
    ).fetchone()
    
    if result and result['total'] and result['total'] > 0:
        return round((result['correct'] / result['total']) * 100, 2)
    return 0


def get_leaderboard(limit=20):
    """Get leaderboard sorted by XP"""
    db = get_db()
    
    leaderboard = db.execute(
        '''SELECT u.id, u.username, us.xp, us.level, us.streak
           FROM users u
           JOIN user_stats us ON u.id = us.user_id
           WHERE u.role = 'student'
           ORDER BY us.xp DESC, us.level DESC
           LIMIT ?''',
        (limit,)
    ).fetchall()
    
    return leaderboard


def get_topic_performance(user_id):
    """Get user's performance breakdown by topic"""
    db = get_db()
    
    topic_stats = db.execute(
        '''SELECT q.topic,
                  COUNT(*) as total_attempts,
                  SUM(CASE WHEN a.is_correct = 1 THEN 1 ELSE 0 END) as correct_attempts,
                  AVG(a.xp_earned) as avg_xp
           FROM attempts a
           JOIN questions q ON a.question_id = q.id
           WHERE a.user_id = ?
           GROUP BY q.topic
           ORDER BY total_attempts DESC''',
        (user_id,)
    ).fetchall()
    
    result = []
    for topic in topic_stats:
        accuracy = 0
        if topic['total_attempts'] > 0:
            accuracy = (topic['correct_attempts'] / topic['total_attempts']) * 100
        
        result.append({
            'topic': topic['topic'],
            'total_attempts': topic['total_attempts'],
            'correct_attempts': topic['correct_attempts'],
            'accuracy': round(accuracy, 2),
            'avg_xp': round(topic['avg_xp'] or 0, 2)
        })
    
    return result
