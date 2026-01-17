"""
Seed Data Script
Combines all data seeding functions into one file
"""

from database import init_db, get_db
from datetime import datetime
from werkzeug.security import generate_password_hash

def init_demo_data():
    """Add demo data for academy, courses, and tests"""
    # Initialize database first
    init_db()
    
    db = get_db()
    
    print("=" * 60)
    print("Initializing Demo Data for Academy-Ready Platform")
    print("=" * 60)
    
    # ==================== CREATE SUBJECTS ====================
    print("\n1. Creating Subjects...")
    
    subjects_data = [
        {
            'name': 'Python Basics',
            'description': 'Introduction to Python programming fundamentals',
            'language_track': 'python',
            'order_index': 1
        },
        {
            'name': 'Data Structures',
            'description': 'Learn about lists, dictionaries, tuples, and sets',
            'language_track': 'python',
            'order_index': 2
        },
        {
            'name': 'Control Flow',
            'description': 'Loops, conditionals, and program control',
            'language_track': 'python',
            'order_index': 3
        },
        {
            'name': 'Functions & Modules',
            'description': 'Creating and using functions and modules',
            'language_track': 'python',
            'order_index': 4
        }
    ]
    
    subject_ids = {}
    for subj in subjects_data:
        try:
            cursor = db.execute(
                '''INSERT OR IGNORE INTO subjects (name, description, language_track, order_index, created_at)
                   VALUES (?, ?, ?, ?, ?)''',
                (subj['name'], subj['description'], subj['language_track'], subj['order_index'], datetime.now())
            )
            db.commit()
            subject_id = cursor.lastrowid
            if not subject_id:
                # Get existing subject ID
                existing = db.execute('SELECT id FROM subjects WHERE name = ?', (subj['name'],)).fetchone()
                subject_id = existing['id'] if existing else None
            if subject_id:
                subject_ids[subj['name']] = subject_id
                print(f"   [OK] Created subject: {subj['name']}")
        except Exception as e:
            print(f"   [ERROR] Error creating subject '{subj['name']}': {str(e)}")
    
    # ==================== CREATE TOPICS ====================
    print("\n2. Creating Topics...")
    
    topics_data = [
        {
            'subject': 'Python Basics',
            'name': 'Variables and Data Types',
            'description': 'Understanding variables, integers, floats, strings, and booleans',
            'order_index': 1
        },
        {
            'subject': 'Python Basics',
            'name': 'Input and Output',
            'description': 'Using print() and input() functions',
            'order_index': 2
        },
        {
            'subject': 'Data Structures',
            'name': 'Lists',
            'description': 'Working with Python lists',
            'order_index': 1
        },
        {
            'subject': 'Data Structures',
            'name': 'Dictionaries',
            'description': 'Understanding key-value pairs',
            'order_index': 2
        },
        {
            'subject': 'Control Flow',
            'name': 'If-Else Statements',
            'description': 'Conditional execution',
            'order_index': 1
        },
        {
            'subject': 'Control Flow',
            'name': 'Loops',
            'description': 'For and while loops',
            'order_index': 2
        },
        {
            'subject': 'Functions & Modules',
            'name': 'Defining Functions',
            'description': 'Creating your own functions',
            'order_index': 1
        }
    ]
    
    topic_ids = {}
    for topic in topics_data:
        try:
            subject_id = subject_ids.get(topic['subject'])
            if not subject_id:
                print(f"   [WARNING] Subject '{topic['subject']}' not found, skipping topic '{topic['name']}'")
                continue
            
            cursor = db.execute(
                '''INSERT OR IGNORE INTO topics (subject_id, name, description, order_index, created_at)
                   VALUES (?, ?, ?, ?, ?)''',
                (subject_id, topic['name'], topic['description'], topic['order_index'], datetime.now())
            )
            db.commit()
            topic_id = cursor.lastrowid
            if not topic_id:
                existing = db.execute('SELECT id FROM topics WHERE subject_id = ? AND name = ?', 
                                    (subject_id, topic['name'])).fetchone()
                topic_id = existing['id'] if existing else None
            if topic_id:
                topic_ids[topic['name']] = topic_id
                print(f"   [OK] Created topic: {topic['name']}")
        except Exception as e:
            print(f"   [ERROR] Error creating topic '{topic['name']}': {str(e)}")
    
    # ==================== CREATE NOTES ====================
    print("\n3. Creating Notes...")
    
    notes_data = [
        {
            'topic': 'Variables and Data Types',
            'title': 'Introduction to Variables',
            'content': '''
            <h2>What are Variables?</h2>
            <p>Variables are containers that store data values. In Python, you don't need to declare the type of a variable - Python automatically detects it.</p>
            
            <h3>Creating Variables</h3>
            <pre><code># String variable
name = "Alice"

# Integer variable
age = 25

# Float variable
height = 5.6

# Boolean variable
is_student = True</code></pre>
            
            <h3>Variable Naming Rules</h3>
            <ul>
                <li>Must start with a letter or underscore</li>
                <li>Can contain letters, numbers, and underscores</li>
                <li>Case-sensitive (age ≠ Age)</li>
                <li>Cannot use Python keywords (if, for, def, etc.)</li>
            </ul>
            
            <h3>Data Types</h3>
            <p>Python has several built-in data types:</p>
            <ul>
                <li><strong>int:</strong> Integers (1, 2, -5)</li>
                <li><strong>float:</strong> Floating point numbers (3.14, -0.5)</li>
                <li><strong>str:</strong> Strings ("hello", 'world')</li>
                <li><strong>bool:</strong> Boolean (True, False)</li>
            </ul>
            ''',
            'visibility': 'published',
            'order_index': 1
        },
        {
            'topic': 'Lists',
            'title': 'Working with Python Lists',
            'content': '''
            <h2>Python Lists</h2>
            <p>Lists are ordered, mutable collections of items. They are one of the most versatile data structures in Python.</p>
            
            <h3>Creating Lists</h3>
            <pre><code># Empty list
my_list = []

# List with elements
fruits = ["apple", "banana", "orange"]
numbers = [1, 2, 3, 4, 5]

# Mixed types
mixed = [1, "hello", 3.14, True]</code></pre>
            
            <h3>Accessing Elements</h3>
            <pre><code>fruits = ["apple", "banana", "orange"]
print(fruits[0])   # Output: apple (first element)
print(fruits[-1])  # Output: orange (last element)</code></pre>
            
            <h3>List Methods</h3>
            <ul>
                <li><code>append(item)</code> - Add item to end</li>
                <li><code>insert(index, item)</code> - Insert at position</li>
                <li><code>remove(item)</code> - Remove first occurrence</li>
                <li><code>pop()</code> - Remove and return last item</li>
                <li><code>sort()</code> - Sort list in place</li>
            </ul>
            ''',
            'visibility': 'published',
            'order_index': 1
        },
        {
            'topic': 'Dictionaries',
            'title': 'Understanding Python Dictionaries',
            'content': '''
            <h2>Dictionaries in Python</h2>
            <p>Dictionaries are unordered collections of key-value pairs. They are incredibly useful for storing and retrieving data efficiently.</p>
            
            <h3>Creating Dictionaries</h3>
            <pre><code># Empty dictionary
my_dict = {}

# Dictionary with key-value pairs
student = {
    "name": "Alice",
    "age": 20,
    "grade": "A"
}</code></pre>
            
            <h3>Accessing Values</h3>
            <pre><code>print(student["name"])  # Output: Alice
print(student.get("age"))  # Output: 20
print(student.get("city", "Unknown"))  # Output: Unknown (default)</code></pre>
            
            <h3>Dictionary Methods</h3>
            <ul>
                <li><code>keys()</code> - Get all keys</li>
                <li><code>values()</code> - Get all values</li>
                <li><code>items()</code> - Get key-value pairs</li>
                <li><code>get(key, default)</code> - Safely get value</li>
            </ul>
            ''',
            'visibility': 'published',
            'order_index': 1
        },
        {
            'topic': 'Loops',
            'title': 'For and While Loops',
            'content': '''
            <h2>Loops in Python</h2>
            <p>Loops allow you to execute a block of code repeatedly. Python has two main loop types: <code>for</code> and <code>while</code>.</p>
            
            <h3>For Loop</h3>
            <pre><code># Iterate over a list
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(fruit)

# Using range()
for i in range(5):
    print(i)  # Output: 0, 1, 2, 3, 4</code></pre>
            
            <h3>While Loop</h3>
            <pre><code>count = 0
while count < 5:
    print(count)
    count += 1</code></pre>
            
            <h3>Loop Control</h3>
            <ul>
                <li><code>break</code> - Exit the loop completely</li>
                <li><code>continue</code> - Skip current iteration</li>
            </ul>
            ''',
            'visibility': 'published',
            'order_index': 1
        }
    ]
    
    note_count = 0
    for note in notes_data:
        try:
            topic_id = topic_ids.get(note['topic'])
            if not topic_id:
                print(f"   [WARNING] Topic '{note['topic']}' not found, skipping note '{note['title']}'")
                continue
            
            db.execute(
                '''INSERT OR IGNORE INTO notes (topic_id, title, content, visibility, order_index, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (topic_id, note['title'], note['content'], note['visibility'], note['order_index'], 
                 datetime.now(), datetime.now())
            )
            db.commit()
            note_count += 1
            print(f"   [OK] Created note: {note['title']}")
        except Exception as e:
            print(f"   [ERROR] Error creating note '{note['title']}': {str(e)}")
    
    # ==================== CREATE COURSE ====================
    print("\n4. Creating Course...")
    
    try:
        # Get first subject ID for course
        first_subject_id = list(subject_ids.values())[0] if subject_ids else None
        
        cursor = db.execute(
            '''INSERT OR IGNORE INTO courses (name, description, status, created_at)
               VALUES (?, ?, ?, ?)''',
            ('Python Programming Fundamentals', 
             'A comprehensive course covering Python basics, data structures, and programming concepts',
             'active', datetime.now())
        )
        db.commit()
        course_id = cursor.lastrowid
        if not course_id:
            existing = db.execute('SELECT id FROM courses WHERE name = ?', 
                                ('Python Programming Fundamentals',)).fetchone()
            course_id = existing['id'] if existing else None
        
        if course_id:
            # Add all subjects to course
            for subj_id in subject_ids.values():
                try:
                    db.execute(
                        'INSERT OR IGNORE INTO course_subjects (course_id, subject_id, order_index) VALUES (?, ?, ?)',
                        (course_id, subj_id, 1)
                    )
                except:
                    pass
            db.commit()
            print(f"   [OK] Created course: Python Programming Fundamentals")
            print(f"   [OK] Added {len(subject_ids)} subjects to course")
        else:
            print("   [WARNING] Could not create course")
    except Exception as e:
        print(f"   [ERROR] Error creating course: {str(e)}")
    
    # ==================== CREATE TEST ====================
    print("\n5. Creating Test...")
    
    try:
        # Get questions with mix of difficulties (prefer hard questions)
        hard_questions = db.execute('SELECT id FROM questions WHERE difficulty = "hard" LIMIT 3').fetchall()
        medium_questions = db.execute('SELECT id FROM questions WHERE difficulty = "medium" LIMIT 2').fetchall()
        easy_questions = db.execute('SELECT id FROM questions WHERE difficulty IN ("easy", "beginner") LIMIT 2').fetchall()
        
        question_ids = []
        for q in hard_questions:
            question_ids.append(q['id'])
        for q in medium_questions:
            question_ids.append(q['id'])
        for q in easy_questions:
            question_ids.append(q['id'])
        
        # If not enough questions, get any available
        if len(question_ids) < 5:
            if question_ids:
                placeholders = ','.join('?' * len(question_ids))
                remaining = db.execute(f'SELECT id FROM questions WHERE id NOT IN ({placeholders}) LIMIT ?',
                                      question_ids + [5 - len(question_ids)]).fetchall()
            else:
                remaining = db.execute('SELECT id FROM questions LIMIT 5').fetchall()
            for q in remaining:
                if q['id'] not in question_ids:
                    question_ids.append(q['id'])
        
        if question_ids:
            # Get first subject for test
            test_subject_id = list(subject_ids.values())[0] if subject_ids else None
            
            cursor = db.execute(
                '''INSERT OR IGNORE INTO tests (title, description, subject_id, time_limit_minutes, 
                   passing_score, status, assigned_to_all, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                ('Python Basics Assessment',
                 'Test your knowledge of Python fundamentals including variables, data types, and basic operations',
                 test_subject_id, 30, 50, 'published', 1, datetime.now())
            )
            db.commit()
            test_id = cursor.lastrowid
            if not test_id:
                existing = db.execute('SELECT id FROM tests WHERE title = ?', 
                                    ('Python Basics Assessment',)).fetchone()
                test_id = existing['id'] if existing else None
            
            if test_id:
                # Add questions to test
                for idx, qid in enumerate(question_ids[:5]):  # Use first 5 questions
                    try:
                        db.execute(
                            'INSERT OR IGNORE INTO test_questions (test_id, question_id, order_index, points) VALUES (?, ?, ?, ?)',
                            (test_id, qid, idx, 1)
                        )
                    except:
                        pass
                db.commit()
                
                # Update test question count
                question_count = db.execute('SELECT COUNT(*) as count FROM test_questions WHERE test_id = ?', 
                                          (test_id,)).fetchone()['count']
                db.execute('UPDATE tests SET total_questions = ? WHERE id = ?', (question_count, test_id))
                db.commit()
                
                print(f"   [OK] Created test: Python Basics Assessment")
                print(f"   [OK] Added {question_count} questions to test")
            else:
                print("   [WARNING] Could not create test")
        else:
            print("   [WARNING] No questions found in database. Please run init_sample_questions.py first.")
    except Exception as e:
        print(f"   [ERROR] Error creating test: {str(e)}")
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 60)
    print("Demo Data Initialization Complete!")
    print("=" * 60)
    
    # Print summary
    subjects_count = db.execute('SELECT COUNT(*) as count FROM subjects').fetchone()['count']
    topics_count = db.execute('SELECT COUNT(*) as count FROM topics').fetchone()['count']
    notes_count = db.execute('SELECT COUNT(*) as count FROM notes').fetchone()['count']
    courses_count = db.execute('SELECT COUNT(*) as count FROM courses').fetchone()['count']
    tests_count = db.execute('SELECT COUNT(*) as count FROM tests').fetchone()['count']
    
    print(f"\n[SUMMARY] Summary:")
    print(f"   - Subjects: {subjects_count}")
    print(f"   - Topics: {topics_count}")
    print(f"   - Notes: {notes_count}")
    print(f"   - Courses: {courses_count}")
    print(f"   - Tests: {tests_count}")
    
    print(f"\n[INFO] You can now:")
    print(f"   1. Browse Academy: /academy/learning")
    print(f"   2. View Courses: /courses")
    print(f"   3. Take Tests: /tests")
    print(f"   4. Admin can manage all content from Admin Dashboard")
    
    print("\n[INFO] Note: Make sure you have questions in the database.")
    print("   Run: python init_sample_questions.py (if not already done)")



def init_learning_materials():
    """Add sample learning materials to the database"""
    # Initialize database
    init_db()
    
    db = get_db()
    
    # Sample learning materials
    materials = [
        {
            'title': 'Introduction to Python',
            'content': '''
            <h2>What is Python?</h2>
            <p>Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.</p>
            
            <h3>Key Features:</h3>
            <ul>
                <li><strong>Easy to Learn:</strong> Python has a simple syntax that is easy to read and write.</li>
                <li><strong>Versatile:</strong> Used in web development, data science, AI, automation, and more.</li>
                <li><strong>Interpreted:</strong> No need to compile code before running.</li>
                <li><strong>Dynamic Typing:</strong> Variables don't need explicit type declaration.</li>
            </ul>
            
            <h3>Example: Your First Python Program</h3>
            <pre><code>print("Hello, World!")</code></pre>
            
            <p>This simple program prints "Hello, World!" to the console. Python makes it that easy to get started!</p>
            ''',
            'topic': 'Variables',
            'language_track': 'python',
            'level': 'beginner',
            'order_index': 1
        },
        {
            'title': 'Python Variables and Data Types',
            'content': '''
            <h2>Variables in Python</h2>
            <p>Variables are containers that store data values. In Python, you don't need to declare the type of a variable - Python automatically detects it.</p>
            
            <h3>Creating Variables</h3>
            <pre><code># String variable
name = "Alice"

# Integer variable
age = 25

# Float variable
height = 5.6

# Boolean variable
is_student = True</code></pre>
            
            <h3>Data Types</h3>
            <ul>
                <li><strong>int:</strong> Integers (1, 2, -5)</li>
                <li><strong>float:</strong> Floating point numbers (3.14, -0.5)</li>
                <li><strong>str:</strong> Strings ("hello", 'world')</li>
                <li><strong>bool:</strong> Boolean (True, False)</li>
                <li><strong>list:</strong> Ordered collection [1, 2, 3]</li>
                <li><strong>dict:</strong> Key-value pairs {"key": "value"}</li>
            </ul>
            
            <h3>Type Conversion</h3>
            <pre><code># Convert string to integer
number = int("10")

# Convert integer to string
text = str(42)

# Convert to float
decimal = float("3.14")</code></pre>
            ''',
            'topic': 'Variables',
            'language_track': 'python',
            'level': 'beginner',
            'order_index': 2
        },
        {
            'title': 'Python Lists',
            'content': '''
            <h2>Lists in Python</h2>
            <p>Lists are ordered, mutable collections of items. They are one of the most versatile data structures in Python.</p>
            
            <h3>Creating Lists</h3>
            <pre><code># Empty list
my_list = []

# List with elements
fruits = ["apple", "banana", "orange"]
numbers = [1, 2, 3, 4, 5]

# Mixed types
mixed = [1, "hello", 3.14, True]</code></pre>
            
            <h3>Accessing Elements</h3>
            <pre><code>fruits = ["apple", "banana", "orange"]
print(fruits[0])  # Output: apple (first element)
print(fruits[-1])  # Output: orange (last element)</code></pre>
            
            <h3>Common List Methods</h3>
            <ul>
                <li><code>append()</code>: Add item to end</li>
                <li><code>insert()</code>: Insert at specific position</li>
                <li><code>remove()</code>: Remove first occurrence</li>
                <li><code>pop()</code>: Remove and return item</li>
                <li><code>sort()</code>: Sort list in place</li>
                <li><code>reverse()</code>: Reverse list</li>
            </ul>
            
            <h3>List Slicing</h3>
            <pre><code>numbers = [1, 2, 3, 4, 5]
print(numbers[1:3])  # Output: [2, 3]
print(numbers[:3])   # Output: [1, 2, 3]
print(numbers[2:])   # Output: [3, 4, 5]</code></pre>
            ''',
            'topic': 'Data Structures',
            'language_track': 'python',
            'level': 'beginner',
            'order_index': 1
        },
        {
            'title': 'Python Dictionaries',
            'content': '''
            <h2>Dictionaries in Python</h2>
            <p>Dictionaries are unordered collections of key-value pairs. They are incredibly useful for storing and retrieving data efficiently.</p>
            
            <h3>Creating Dictionaries</h3>
            <pre><code># Empty dictionary
my_dict = {}

# Dictionary with key-value pairs
student = {
    "name": "Alice",
    "age": 20,
    "grade": "A"
}</code></pre>
            
            <h3>Accessing Values</h3>
            <pre><code>print(student["name"])  # Output: Alice
print(student.get("age"))  # Output: 20
print(student.get("city", "Unknown"))  # Output: Unknown (default)</code></pre>
            
            <h3>Dictionary Methods</h3>
            <ul>
                <li><code>keys()</code>: Get all keys</li>
                <li><code>values()</code>: Get all values</li>
                <li><code>items()</code>: Get key-value pairs</li>
                <li><code>get()</code>: Safely get value (returns None if key not found)</li>
                <li><code>update()</code>: Update with another dictionary</li>
            </ul>
            ''',
            'topic': 'Data Structures',
            'language_track': 'python',
            'level': 'intermediate',
            'order_index': 2
        },
        {
            'title': 'Python Loops - For and While',
            'content': '''
            <h2>Loops in Python</h2>
            <p>Loops allow you to execute a block of code repeatedly. Python has two main loop types: <code>for</code> and <code>while</code>.</p>
            
            <h3>For Loop</h3>
            <pre><code># Iterate over a list
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(fruit)

# Using range()
for i in range(5):
    print(i)  # Output: 0, 1, 2, 3, 4</code></pre>
            
            <h3>While Loop</h3>
            <pre><code>count = 0
while count < 5:
    print(count)
    count += 1</code></pre>
            
            <h3>Loop Control Statements</h3>
            <ul>
                <li><code>break</code>: Exit the loop completely</li>
                <li><code>continue</code>: Skip current iteration</li>
                <li><code>else</code>: Execute when loop completes normally (no break)</li>
            </ul>
            
            <h3>Nested Loops</h3>
            <pre><code>for i in range(3):
    for j in range(2):
        print(f"({i}, {j})")</code></pre>
            ''',
            'topic': 'Loops',
            'language_track': 'python',
            'level': 'beginner',
            'order_index': 1
        },
        {
            'title': 'Python Functions',
            'content': '''
            <h2>Functions in Python</h2>
            <p>Functions are reusable blocks of code that perform specific tasks. They help organize code and avoid repetition.</p>
            
            <h3>Defining Functions</h3>
            <pre><code>def greet(name):
    return f"Hello, {name}!"

print(greet("Alice"))  # Output: Hello, Alice!</code></pre>
            
            <h3>Parameters and Arguments</h3>
            <pre><code># Function with default parameter
def greet(name="Guest"):
    return f"Hello, {name}!"

print(greet())  # Output: Hello, Guest!
print(greet("Bob"))  # Output: Hello, Bob!</code></pre>
            
            <h3>Return Values</h3>
            <pre><code>def add(a, b):
    return a + b

result = add(3, 5)  # result = 8</code></pre>
            
            <h3>Lambda Functions</h3>
            <pre><code># Anonymous functions
square = lambda x: x ** 2
print(square(5))  # Output: 25</code></pre>
            ''',
            'topic': 'Functions',
            'language_track': 'python',
            'level': 'beginner',
            'order_index': 1
        },
        {
            'title': 'String Operations in Python',
            'content': '''
            <h2>Working with Strings</h2>
            <p>Strings are sequences of characters. Python provides many methods for string manipulation.</p>
            
            <h3>String Methods</h3>
            <pre><code>text = "Hello World"

# Convert to uppercase
print(text.upper())  # HELLO WORLD

# Convert to lowercase
print(text.lower())  # hello world

# Split into list
words = text.split()  # ["Hello", "World"]

# Replace substring
new_text = text.replace("World", "Python")  # "Hello Python"

# Strip whitespace
spaced = "  hello  ".strip()  # "hello"</code></pre>
            
            <h3>String Formatting</h3>
            <pre><code>name = "Alice"
age = 25

# f-string (Python 3.6+)
message = f"My name is {name} and I'm {age} years old"

# format() method
message = "My name is {} and I'm {} years old".format(name, age)</code></pre>
            ''',
            'topic': 'Strings',
            'language_track': 'python',
            'level': 'beginner',
            'order_index': 1
        },
        {
            'title': 'Exception Handling in Python',
            'content': '''
            <h2>Exception Handling</h2>
            <p>Exceptions are errors that occur during program execution. Python provides try-except blocks to handle them gracefully.</p>
            
            <h3>Basic Try-Except</h3>
            <pre><code>try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")</code></pre>
            
            <h3>Multiple Exception Types</h3>
            <pre><code>try:
    value = int(input("Enter a number: "))
except ValueError:
    print("Invalid input! Please enter a number.")
except Exception as e:
    print(f"An error occurred: {e}")</code></pre>
            
            <h3>Try-Except-Finally</h3>
            <pre><code>try:
    file = open("data.txt", "r")
    content = file.read()
except FileNotFoundError:
    print("File not found!")
finally:
    file.close()  # Always executes</code></pre>
            
            <h3>Raising Exceptions</h3>
            <pre><code>def check_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return age</code></pre>
            ''',
            'topic': 'Exception Handling',
            'language_track': 'python',
            'level': 'intermediate',
            'order_index': 1
        },
        {
            'title': 'List Comprehensions',
            'content': '''
            <h2>List Comprehensions</h2>
            <p>List comprehensions provide a concise way to create lists. They're more Pythonic and often faster than traditional loops.</p>
            
            <h3>Basic Syntax</h3>
            <pre><code># Traditional way
squares = []
for x in range(10):
    squares.append(x**2)

# List comprehension
squares = [x**2 for x in range(10)]</code></pre>
            
            <h3>With Conditions</h3>
            <pre><code># Even numbers
evens = [x for x in range(20) if x % 2 == 0]

# Conditional values
values = [x if x > 0 else 0 for x in range(-5, 6)]</code></pre>
            
            <h3>Nested Comprehensions</h3>
            <pre><code># Matrix creation
matrix = [[x*y for y in range(3)] for x in range(3)]
# Result: [[0, 0, 0], [0, 1, 2], [0, 2, 4]]</code></pre>
            ''',
            'topic': 'List Comprehension',
            'language_track': 'python',
            'level': 'intermediate',
            'order_index': 1
        },
        {
            'title': 'Object-Oriented Programming in Python',
            'content': '''
            <h2>Classes and Objects</h2>
            <p>Python supports object-oriented programming through classes and objects. Classes are blueprints for creating objects.</p>
            
            <h3>Defining a Class</h3>
            <pre><code>class Dog:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed
    
    def bark(self):
        return f"{self.name} says Woof!"

# Creating an object
my_dog = Dog("Buddy", "Golden Retriever")
print(my_dog.bark())  # Buddy says Woof!</code></pre>
            
            <h3>Class Inheritance</h3>
            <pre><code>class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def bark(self):
        return f"{self.name} barks!"

my_dog = Dog("Buddy")
print(my_dog.bark())</code></pre>
            ''',
            'topic': 'Object-Oriented Programming',
            'language_track': 'python',
            'level': 'advanced',
            'order_index': 1
        }
    ]
    
    # Check if materials already exist
    existing_count = db.execute('SELECT COUNT(*) as count FROM learning_materials').fetchone()['count']
    
    if existing_count > 0:
        print(f"Database already has {existing_count} learning materials.")
        response = input("Do you want to add sample materials anyway? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    # Insert learning materials
    inserted_count = 0
    for material in materials:
        try:
            db.execute(
                '''INSERT INTO learning_materials (title, content, topic, language_track, level, order_index, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    material['title'],
                    material['content'],
                    material['topic'],
                    material['language_track'],
                    material['level'],
                    material['order_index'],
                    datetime.now(),
                    datetime.now()
                )
            )
            inserted_count += 1
        except Exception as e:
            print(f"Error inserting material '{material['title']}': {str(e)}")
    
    db.commit()
    print(f"Successfully added {inserted_count} learning materials to the database!")
    print(f"Total materials in database: {db.execute('SELECT COUNT(*) as count FROM learning_materials').fetchone()['count']}")



def init_sample_questions():
    """Add sample questions to the database"""
    # Initialize database
    init_db()
    
    db = get_db()
    
    # Extensive Python Questions Collection (50+ questions)
    sample_questions = [
        {
            'title': 'Variable Assignment in Python',
            'question_text': 'What is the output of the following code?\n\nx = 10\ny = 20\nx = y\nprint(x)',
            'option_a': '10',
            'option_b': '20',
            'option_c': '30',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'When x = y is executed, x gets the value of y which is 20. So print(x) outputs 20.',
            'difficulty': 'easy',
            'topic': 'Variables',
            'language_track': 'python',
            'points': 10
        },
        {
            'title': 'Python List Indexing',
            'question_text': 'What is the output of the following code?\n\nmy_list = [1, 2, 3, 4, 5]\nprint(my_list[2])',
            'option_a': '1',
            'option_b': '2',
            'option_c': '3',
            'option_d': '4',
            'correct_answer': 'C',
            'explanation': 'Python uses zero-based indexing. my_list[2] refers to the third element (index 2), which is 3.',
            'difficulty': 'easy',
            'topic': 'Data Structures',
            'language_track': 'python',
            'points': 10
        },
        {
            'title': 'For Loop in Python',
            'question_text': 'What is the output of the following code?\n\nfor i in range(3):\n    print(i, end=" ")',
            'option_a': '0 1 2',
            'option_b': '1 2 3',
            'option_c': '0 1 2 3',
            'option_d': '1 2',
            'correct_answer': 'A',
            'explanation': 'range(3) generates numbers from 0 to 2 (exclusive of 3). So the output is 0 1 2.',
            'difficulty': 'easy',
            'topic': 'Loops',
            'language_track': 'python',
            'points': 10
        },
        {
            'title': 'Python Dictionary Access',
            'question_text': 'What happens when you try to access a non-existent key in a dictionary using dict[key]?',
            'option_a': 'Returns None',
            'option_b': 'Returns empty string',
            'option_c': 'Raises KeyError',
            'option_d': 'Returns 0',
            'correct_answer': 'C',
            'explanation': 'Accessing a non-existent key using dict[key] raises a KeyError exception in Python.',
            'difficulty': 'medium',
            'topic': 'Data Structures',
            'language_track': 'python',
            'points': 15
        },
        {
            'title': 'Function Scope in Python',
            'question_text': 'What is the output of the following code?\n\ndef func():\n    x = 10\n    return x\n\nx = 5\nprint(func())\nprint(x)',
            'option_a': '10\n10',
            'option_b': '10\n5',
            'option_c': '5\n5',
            'option_d': '5\n10',
            'correct_answer': 'B',
            'explanation': 'The variable x inside func() is local to the function. The global x = 5 is not affected by the local x = 10.',
            'difficulty': 'medium',
            'topic': 'Functions',
            'language_track': 'python',
            'points': 15
        },
        {
            'title': 'List Comprehension',
            'question_text': 'What does this list comprehension create?\n\n[x*2 for x in range(5)]',
            'option_a': '[0, 2, 4, 6, 8]',
            'option_b': '[2, 4, 6, 8, 10]',
            'option_c': '[1, 2, 3, 4, 5]',
            'option_d': '[0, 1, 2, 3, 4]',
            'correct_answer': 'A',
            'explanation': 'The comprehension takes each x from range(5) (0,1,2,3,4) and multiplies by 2, resulting in [0, 2, 4, 6, 8].',
            'difficulty': 'medium',
            'topic': 'List Comprehension',
            'language_track': 'python',
            'points': 15
        },
        {
            'title': 'Python String Slicing',
            'question_text': 'What is the output of the following code?\n\ns = "Python"\nprint(s[1:4])',
            'option_a': 'Pyth',
            'option_b': 'yth',
            'option_c': 'ytho',
            'option_d': 'Python',
            'correct_answer': 'B',
            'explanation': 'String slicing s[1:4] takes characters from index 1 to 3 (exclusive of 4), which is "yth".',
            'difficulty': 'easy',
            'topic': 'Strings',
            'language_track': 'python',
            'points': 10
        },
        {
            'title': 'Mutable vs Immutable',
            'question_text': 'Which of the following data types is mutable in Python?',
            'option_a': 'String',
            'option_b': 'Tuple',
            'option_c': 'List',
            'option_d': 'Integer',
            'correct_answer': 'C',
            'explanation': 'Lists are mutable in Python, meaning their contents can be changed. Strings, tuples, and integers are immutable.',
            'difficulty': 'medium',
            'topic': 'Data Types',
            'language_track': 'python',
            'points': 15
        },
        {
            'title': 'Nested Loop Complexity',
            'question_text': 'What is the output of the following code?\n\nresult = []\nfor i in range(2):\n    for j in range(3):\n        result.append((i, j))\nprint(len(result))',
            'option_a': '3',
            'option_b': '5',
            'option_c': '6',
            'option_d': '9',
            'correct_answer': 'C',
            'explanation': 'The outer loop runs 2 times (i=0,1), and the inner loop runs 3 times for each outer iteration. Total: 2*3 = 6 iterations.',
            'difficulty': 'hard',
            'topic': 'Loops',
            'language_track': 'python',
            'points': 20
        },
        {
            'title': 'Recursive Function',
            'question_text': 'What is the output of the following recursive function?\n\ndef factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)\n\nprint(factorial(4))',
            'option_a': '12',
            'option_b': '16',
            'option_c': '24',
            'option_d': '48',
            'correct_answer': 'C',
            'explanation': 'factorial(4) = 4 * factorial(3) = 4 * 3 * factorial(2) = 4 * 3 * 2 * factorial(1) = 4 * 3 * 2 * 1 = 24.',
            'difficulty': 'hard',
            'topic': 'Recursion',
            'language_track': 'python',
            'points': 20
        },
        {
            'title': 'Exception Handling',
            'question_text': 'What is the output of the following code?\n\ntry:\n    result = 10 / 0\n    print(result)\nexcept ZeroDivisionError:\n    print("Error occurred")\nelse:\n    print("No error")\nfinally:\n    print("Done")',
            'option_a': 'Error occurred\nDone',
            'option_b': 'No error\nDone',
            'option_c': 'Error occurred',
            'option_d': 'Done',
            'correct_answer': 'A',
            'explanation': 'When ZeroDivisionError occurs, the except block executes. The finally block always executes, regardless of exceptions.',
            'difficulty': 'medium',
            'topic': 'Exception Handling',
            'language_track': 'python',
            'points': 15
        },
        {
            'title': 'Lambda Functions',
            'question_text': 'What does this lambda function do?\n\nf = lambda x: x**2\nprint(f(5))',
            'option_a': '25',
            'option_b': '10',
            'option_c': '125',
            'option_d': '5',
            'correct_answer': 'A',
            'explanation': 'The lambda function squares the input. f(5) = 5**2 = 25.',
            'difficulty': 'medium',
            'topic': 'Functions',
            'language_track': 'python',
            'points': 15
        }
    ]
    
    # Check if questions already exist
    existing_count = db.execute('SELECT COUNT(*) as count FROM questions').fetchone()['count']
    
    if existing_count > 0:
        print(f"Database already has {existing_count} questions.")
        response = input("Do you want to add sample questions anyway? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    # Insert sample questions
    inserted_count = 0
    for question in sample_questions:
        try:
            db.execute(
                '''INSERT INTO questions (title, question_text, option_a, option_b, option_c, option_d,
                   correct_answer, explanation, difficulty, topic, language_track, points, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    question['title'], question['question_text'],
                    question['option_a'], question['option_b'],
                    question['option_c'], question['option_d'],
                    question['correct_answer'], question['explanation'],
                    question['difficulty'], question['topic'],
                    question['language_track'], question['points'],
                    datetime.now()
                )
            )
            inserted_count += 1
        except Exception as e:
            print(f"Error inserting question '{question['title']}': {str(e)}")
    
    db.commit()
    print(f"Successfully added {inserted_count} sample questions to the database!")
    print(f"Total questions in database: {db.execute('SELECT COUNT(*) as count FROM questions').fetchone()['count']}")



def seed_bulk_questions():
    """Add comprehensive question bank to database"""
    init_db()
    db = get_db()
    
    questions = [
        # ========== VARIABLES (14 questions) ==========
        {
            'title': 'Variable Assignment',
            'question_text': 'What is the output?\n\nx = 10\ny = 20\nx = y\nprint(x)',
            'option_a': '10',
            'option_b': '20',
            'option_c': '30',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'When x = y executes, x gets the value of y (20).',
            'difficulty': 'easy',
            'topic': 'Variables',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Multiple Assignment',
            'question_text': 'What is the output?\n\na, b = 5, 10\nprint(a, b)',
            'option_a': '5 10',
            'option_b': '(5, 10)',
            'option_c': 'Error',
            'option_d': '15',
            'correct_answer': 'A',
            'explanation': 'Multiple assignment assigns values in order: a=5, b=10.',
            'difficulty': 'easy',
            'topic': 'Variables',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Variable Naming',
            'question_text': 'Which is a valid variable name?',
            'option_a': '2variable',
            'option_b': 'my-variable',
            'option_c': 'my_variable',
            'option_d': 'my variable',
            'correct_answer': 'C',
            'explanation': 'Variable names can contain letters, numbers, and underscores, but cannot start with a number or contain hyphens/spaces.',
            'difficulty': 'easy',
            'topic': 'Variables',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'String Concatenation',
            'question_text': 'What is the output?\n\nname = "Python"\nresult = "Hello " + name\nprint(result)',
            'option_a': 'Hello Python',
            'option_b': 'Hello + Python',
            'option_c': 'Error',
            'option_d': 'Hello name',
            'correct_answer': 'A',
            'explanation': 'The + operator concatenates strings together.',
            'difficulty': 'easy',
            'topic': 'Variables',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Type Conversion',
            'question_text': 'What is the output?\n\nnum = "123"\nresult = int(num) + 5\nprint(result)',
            'option_a': '1235',
            'option_b': '128',
            'option_c': 'Error',
            'option_d': '123 + 5',
            'correct_answer': 'B',
            'explanation': 'int() converts string "123" to integer 123, then adds 5 to get 128.',
            'difficulty': 'easy',
            'topic': 'Variables',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Global vs Local',
            'question_text': 'What is the output?\n\nx = 10\ndef func():\n    x = 20\n    return x\nprint(func())\nprint(x)',
            'option_a': '20\n10',
            'option_b': '10\n20',
            'option_c': '20\n20',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'Inside func(), x=20 creates a local variable. The global x remains 10.',
            'difficulty': 'medium',
            'topic': 'Variables',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Variable Scope',
            'question_text': 'What is the output?\n\ndef test():\n    global x\n    x = 30\n    return x\nx = 10\nprint(test())\nprint(x)',
            'option_a': '30\n10',
            'option_b': '10\n30',
            'option_c': '30\n30',
            'option_d': 'Error',
            'correct_answer': 'C',
            'explanation': 'The global keyword allows modifying the global x inside the function.',
            'difficulty': 'medium',
            'topic': 'Variables',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Mutable Default Arguments',
            'question_text': 'What is the output?\n\ndef add_item(item, my_list=[]):\n    my_list.append(item)\n    return my_list\nprint(add_item(1))\nprint(add_item(2))',
            'option_a': '[1]\n[2]',
            'option_b': '[1]\n[1, 2]',
            'option_c': '[1, 2]\n[1, 2]',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'Default mutable arguments are shared across function calls, so the list persists.',
            'difficulty': 'hard',
            'topic': 'Variables',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== LOOPS (13 questions) ==========
        {
            'title': 'For Loop Basics',
            'question_text': 'What is the output?\n\nfor i in range(3):\n    print(i)',
            'option_a': '0 1 2',
            'option_b': '1 2 3',
            'option_c': '0 1 2 3',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'range(3) generates 0, 1, 2 (starts at 0, stops before 3).',
            'difficulty': 'easy',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'While Loop',
            'question_text': 'What is the output?\n\ncount = 0\nwhile count < 3:\n    print(count)\n    count += 1',
            'option_a': '0 1 2',
            'option_b': '1 2 3',
            'option_c': '0 1 2 3',
            'option_d': 'Infinite loop',
            'correct_answer': 'A',
            'explanation': 'Loop runs while count < 3, printing 0, 1, 2.',
            'difficulty': 'easy',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Nested Loops',
            'question_text': 'What is the output?\n\nfor i in range(2):\n    for j in range(2):\n        print(i, j)',
            'option_a': '0 0\n0 1\n1 0\n1 1',
            'option_b': '0 1\n1 0',
            'option_c': '0 0\n1 1',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'Nested loops: outer loop (i=0,1), inner loop (j=0,1) for each i.',
            'difficulty': 'medium',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Loop with Break',
            'question_text': 'What is the output?\n\nfor i in range(5):\n    if i == 3:\n        break\n    print(i)',
            'option_a': '0 1 2 3',
            'option_b': '0 1 2',
            'option_c': '1 2 3',
            'option_d': '0 1 2 3 4',
            'correct_answer': 'B',
            'explanation': 'break exits the loop when i==3, so only 0, 1, 2 are printed.',
            'difficulty': 'medium',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'List Comprehension',
            'question_text': 'What is the output?\n\nresult = [x*2 for x in range(3)]\nprint(result)',
            'option_a': '[0, 2, 4]',
            'option_b': '[2, 4, 6]',
            'option_c': '[0, 1, 2]',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'List comprehension: for each x in [0,1,2], multiply by 2 → [0,2,4].',
            'difficulty': 'medium',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Generator Expression',
            'question_text': 'What is the type of result?\n\nresult = (x*2 for x in range(3))',
            'option_a': 'list',
            'option_b': 'tuple',
            'option_c': 'generator',
            'option_d': 'Error',
            'correct_answer': 'C',
            'explanation': 'Parentheses create a generator expression, not a tuple. Generators are memory-efficient.',
            'difficulty': 'hard',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== FUNCTIONS (13 questions) ==========
        {
            'title': 'Function Definition',
            'question_text': 'What is the output?\n\ndef greet(name):\n    return f"Hello {name}"\nprint(greet("Python"))',
            'option_a': 'Hello Python',
            'option_b': 'Hello name',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'A',
            'explanation': 'Function returns formatted string with the name parameter.',
            'difficulty': 'easy',
            'topic': 'Functions',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Default Parameters',
            'question_text': 'What is the output?\n\ndef power(x, y=2):\n    return x ** y\nprint(power(3))\nprint(power(3, 3))',
            'option_a': '9\n27',
            'option_b': '6\n27',
            'option_c': '9\n9',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'First call uses default y=2 (3²=9), second call uses y=3 (3³=27).',
            'difficulty': 'easy',
            'topic': 'Functions',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Lambda Function',
            'question_text': 'What is the output?\n\nsquare = lambda x: x * x\nprint(square(5))',
            'option_a': '10',
            'option_b': '25',
            'option_c': '5',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'Lambda creates an anonymous function that squares the input: 5² = 25.',
            'difficulty': 'easy',
            'topic': 'Functions',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Variable Arguments',
            'question_text': 'What is the output?\n\ndef sum_all(*args):\n    return sum(args)\nprint(sum_all(1, 2, 3, 4))',
            'option_a': '10',
            'option_b': '(1, 2, 3, 4)',
            'option_c': 'Error',
            'option_d': '4',
            'correct_answer': 'A',
            'explanation': '*args collects all arguments into a tuple, sum() adds them: 1+2+3+4=10.',
            'difficulty': 'medium',
            'topic': 'Functions',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Keyword Arguments',
            'question_text': 'What is the output?\n\ndef info(name, age):\n    return f"{name} is {age}"\nprint(info(age=25, name="Alice"))',
            'option_a': 'Alice is 25',
            'option_b': 'Error',
            'option_c': 'name is age',
            'option_d': '25 is Alice',
            'correct_answer': 'A',
            'explanation': 'Keyword arguments can be passed in any order.',
            'difficulty': 'medium',
            'topic': 'Functions',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Closure',
            'question_text': 'What is the output?\n\ndef outer(x):\n    def inner(y):\n        return x + y\n    return inner\nfunc = outer(10)\nprint(func(5))',
            'option_a': '15',
            'option_b': '10',
            'option_c': '5',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'Closure: inner function remembers x=10 from outer scope, so func(5) returns 10+5=15.',
            'difficulty': 'hard',
            'topic': 'Functions',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== LISTS (12 questions) ==========
        {
            'title': 'List Indexing',
            'question_text': 'What is the output?\n\nmy_list = [10, 20, 30, 40]\nprint(my_list[1])',
            'option_a': '10',
            'option_b': '20',
            'option_c': '30',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'Python uses zero-based indexing. Index 1 refers to the second element (20).',
            'difficulty': 'easy',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'List Slicing',
            'question_text': 'What is the output?\n\nnums = [0, 1, 2, 3, 4, 5]\nprint(nums[1:4])',
            'option_a': '[1, 2, 3]',
            'option_b': '[1, 2, 3, 4]',
            'option_c': '[0, 1, 2, 3]',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'Slicing [1:4] includes indices 1, 2, 3 (stops before 4).',
            'difficulty': 'easy',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'List Methods',
            'question_text': 'What is the output?\n\nmy_list = [1, 2, 3]\nmy_list.append(4)\nprint(len(my_list))',
            'option_a': '3',
            'option_b': '4',
            'option_c': 'Error',
            'option_d': '7',
            'correct_answer': 'B',
            'explanation': 'append(4) adds 4 to the list, so length becomes 4.',
            'difficulty': 'easy',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'List Comprehension with Condition',
            'question_text': 'What is the output?\n\nresult = [x for x in range(5) if x % 2 == 0]\nprint(result)',
            'option_a': '[0, 2, 4]',
            'option_b': '[1, 3]',
            'option_c': '[0, 1, 2, 3, 4]',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'List comprehension filters even numbers: 0, 2, 4 (x % 2 == 0).',
            'difficulty': 'medium',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'List Aliasing',
            'question_text': 'What is the output?\n\na = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)',
            'option_a': '[1, 2, 3]',
            'option_b': '[1, 2, 3, 4]',
            'option_c': 'Error',
            'option_d': '[4]',
            'correct_answer': 'B',
            'explanation': 'b = a creates an alias (same object). Modifying b also modifies a.',
            'difficulty': 'medium',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'List Copy',
            'question_text': 'What is the output?\n\na = [1, 2, 3]\nb = a.copy()\nb.append(4)\nprint(a)\nprint(b)',
            'option_a': '[1, 2, 3]\n[1, 2, 3, 4]',
            'option_b': '[1, 2, 3, 4]\n[1, 2, 3, 4]',
            'option_c': '[1, 2, 3]\n[1, 2, 3]',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'copy() creates a shallow copy. Modifying b does not affect a.',
            'difficulty': 'hard',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== CONDITIONALS (12 questions) ==========
        {
            'title': 'If Statement',
            'question_text': 'What is the output?\n\nx = 10\nif x > 5:\n    print("Greater")\nelse:\n    print("Smaller")',
            'option_a': 'Greater',
            'option_b': 'Smaller',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'A',
            'explanation': 'x=10 is greater than 5, so the if block executes.',
            'difficulty': 'easy',
            'topic': 'Conditionals',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Elif Chain',
            'question_text': 'What is the output?\n\nscore = 85\nif score >= 90:\n    grade = "A"\nelif score >= 80:\n    grade = "B"\nelse:\n    grade = "C"\nprint(grade)',
            'option_a': 'A',
            'option_b': 'B',
            'option_c': 'C',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'score=85 is >= 80 but < 90, so elif block executes (grade="B").',
            'difficulty': 'easy',
            'topic': 'Conditionals',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Ternary Operator',
            'question_text': 'What is the output?\n\nx = 5\nresult = "Even" if x % 2 == 0 else "Odd"\nprint(result)',
            'option_a': 'Even',
            'option_b': 'Odd',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'B',
            'explanation': 'Ternary: if condition (x%2==0) is False, return "Odd".',
            'difficulty': 'easy',
            'topic': 'Conditionals',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Multiple Conditions',
            'question_text': 'What is the output?\n\nage = 25\nif age >= 18 and age <= 65:\n    print("Adult")\nelse:\n    print("Other")',
            'option_a': 'Adult',
            'option_b': 'Other',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'A',
            'explanation': 'Both conditions are True (25 >= 18 and 25 <= 65), so "Adult" is printed.',
            'difficulty': 'medium',
            'topic': 'Conditionals',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Short-Circuit Evaluation',
            'question_text': 'What is the output?\n\nx = 0\nif x != 0 and 10 / x > 1:\n    print("Safe")\nelse:\n    print("Skip")',
            'option_a': 'Safe',
            'option_b': 'Skip',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'B',
            'explanation': 'Short-circuit: x != 0 is False, so second condition is not evaluated (avoids division by zero).',
            'difficulty': 'hard',
            'topic': 'Conditionals',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== OOP BASICS (9 questions) ==========
        {
            'title': 'Class Definition',
            'question_text': 'What is the output?\n\nclass Dog:\n    def __init__(self, name):\n        self.name = name\n\ndog = Dog("Buddy")\nprint(dog.name)',
            'option_a': 'Buddy',
            'option_b': 'Dog',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'A',
            'explanation': '__init__ is the constructor. self.name = name sets the instance attribute.',
            'difficulty': 'easy',
            'topic': 'OOP Basics',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Instance Method',
            'question_text': 'What is the output?\n\nclass Calculator:\n    def add(self, a, b):\n        return a + b\n\ncalc = Calculator()\nprint(calc.add(3, 4))',
            'option_a': '7',
            'option_b': 'Error',
            'option_c': 'None',
            'option_d': 'Calculator',
            'correct_answer': 'A',
            'explanation': 'Instance method add() takes self and two parameters, returns their sum.',
            'difficulty': 'easy',
            'topic': 'OOP Basics',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Inheritance',
            'question_text': 'What is the output?\n\nclass Animal:\n    def speak(self):\n        return "Sound"\n\nclass Dog(Animal):\n    def speak(self):\n        return "Woof"\n\ndog = Dog()\nprint(dog.speak())',
            'option_a': 'Sound',
            'option_b': 'Woof',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'B',
            'explanation': 'Dog overrides speak() method from Animal parent class.',
            'difficulty': 'medium',
            'topic': 'OOP Basics',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Class vs Instance Variables',
            'question_text': 'What is the output?\n\nclass Counter:\n    count = 0\n    def __init__(self):\n        Counter.count += 1\n\nc1 = Counter()\nc2 = Counter()\nprint(Counter.count)',
            'option_a': '0',
            'option_b': '1',
            'option_c': '2',
            'option_d': 'Error',
            'correct_answer': 'C',
            'explanation': 'count is a class variable shared by all instances. Each __init__ increments it: 0→1→2.',
            'difficulty': 'hard',
            'topic': 'OOP Basics',
            'subject': 'Python',
            'points': 20
        },
    ]
    
    # Add more questions to reach 50+ total
    # Extending with additional questions across all topics
    additional_questions = [
        # More Variables
        {
            'title': 'String Formatting',
            'question_text': 'What is the output?\n\nname = "Python"\nresult = f"Hello {name}"\nprint(result)',
            'option_a': 'Hello Python',
            'option_b': 'Hello {name}',
            'option_c': 'Error',
            'option_d': 'Hello name',
            'correct_answer': 'A',
            'explanation': 'f-strings allow embedding expressions inside strings using {}.',
            'difficulty': 'easy',
            'topic': 'Variables',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Constants Convention',
            'question_text': 'Which naming convention is used for constants in Python?',
            'option_a': 'CONSTANT_NAME',
            'option_b': 'constantName',
            'option_c': 'constant_name',
            'option_d': 'ConstantName',
            'correct_answer': 'A',
            'explanation': 'Python convention: constants use UPPER_SNAKE_CASE.',
            'difficulty': 'easy',
            'topic': 'Variables',
            'subject': 'Python',
            'points': 10
        },
        
        # More Loops
        {
            'title': 'Range with Step',
            'question_text': 'What is the output?\n\nfor i in range(0, 10, 2):\n    print(i, end=" ")',
            'option_a': '0 2 4 6 8',
            'option_b': '0 1 2 3 4 5 6 7 8 9',
            'option_c': '2 4 6 8 10',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'range(0, 10, 2) generates numbers from 0 to 9, stepping by 2.',
            'difficulty': 'easy',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Continue Statement',
            'question_text': 'What is the output?\n\nfor i in range(5):\n    if i == 2:\n        continue\n    print(i, end=" ")',
            'option_a': '0 1 2 3 4',
            'option_b': '0 1 3 4',
            'option_c': '2',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'continue skips the current iteration when i==2, so 2 is not printed.',
            'difficulty': 'medium',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Enumerate Function',
            'question_text': 'What is the output?\n\nitems = ["a", "b", "c"]\nfor i, item in enumerate(items):\n    print(i, item, end=" ")',
            'option_a': '0 a 1 b 2 c',
            'option_b': 'a b c',
            'option_c': '1 a 2 b 3 c',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'enumerate() returns (index, value) pairs, starting from 0.',
            'difficulty': 'medium',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 15
        },
        
        # More Functions
        {
            'title': 'Return Statement',
            'question_text': 'What is the output?\n\ndef test():\n    return 10\n    print("After return")\nprint(test())',
            'option_a': '10',
            'option_b': '10\nAfter return',
            'option_c': 'After return\n10',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'return exits the function immediately. Code after return is unreachable.',
            'difficulty': 'easy',
            'topic': 'Functions',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Recursion',
            'question_text': 'What is the output?\n\ndef factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)\nprint(factorial(3))',
            'option_a': '3',
            'option_b': '6',
            'option_c': 'Error',
            'option_d': '1',
            'correct_answer': 'B',
            'explanation': 'factorial(3) = 3 * factorial(2) = 3 * 2 * factorial(1) = 3 * 2 * 1 = 6.',
            'difficulty': 'hard',
            'topic': 'Functions',
            'subject': 'Python',
            'points': 20
        },
        
        # More Lists
        {
            'title': 'List Methods - Remove',
            'question_text': 'What is the output?\n\nmy_list = [1, 2, 3, 2]\nmy_list.remove(2)\nprint(my_list)',
            'option_a': '[1, 3, 2]',
            'option_b': '[1, 2, 3]',
            'option_c': '[1, 3]',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'remove(2) removes the first occurrence of 2, leaving [1, 3, 2].',
            'difficulty': 'easy',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'List Sorting',
            'question_text': 'What is the output?\n\nnums = [3, 1, 4, 1, 5]\nnums.sort()\nprint(nums)',
            'option_a': '[1, 1, 3, 4, 5]',
            'option_b': '[3, 1, 4, 1, 5]',
            'option_c': '[5, 4, 3, 1, 1]',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'sort() modifies the list in-place, arranging elements in ascending order.',
            'difficulty': 'easy',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'List Extend vs Append',
            'question_text': 'What is the output?\n\na = [1, 2]\nb = [3, 4]\na.extend(b)\nprint(a)',
            'option_a': '[1, 2, [3, 4]]',
            'option_b': '[1, 2, 3, 4]',
            'option_c': 'Error',
            'option_d': '[1, 2]',
            'correct_answer': 'B',
            'explanation': 'extend() adds elements from b to a. append() would add the whole list.',
            'difficulty': 'medium',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 15
        },
        
        # More Conditionals
        {
            'title': 'Nested If',
            'question_text': 'What is the output?\n\nx = 10\ny = 5\nif x > 5:\n    if y > 3:\n        print("Both true")\n    else:\n        print("Only x true")\nelse:\n    print("Neither")',
            'option_a': 'Both true',
            'option_b': 'Only x true',
            'option_c': 'Neither',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'x=10 > 5 (True), y=5 > 3 (True), so nested if executes.',
            'difficulty': 'easy',
            'topic': 'Conditionals',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Boolean Logic',
            'question_text': 'What is the output?\n\nresult = not (True and False)\nprint(result)',
            'option_a': 'True',
            'option_b': 'False',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'A',
            'explanation': 'True and False = False, then not False = True.',
            'difficulty': 'medium',
            'topic': 'Conditionals',
            'subject': 'Python',
            'points': 15
        },
        
        # More OOP
        {
            'title': 'Method Overriding',
            'question_text': 'What is the output?\n\nclass Parent:\n    def show(self):\n        return "Parent"\n\nclass Child(Parent):\n    def show(self):\n        return "Child"\n\nobj = Child()\nprint(obj.show())',
            'option_a': 'Parent',
            'option_b': 'Child',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'B',
            'explanation': 'Child overrides show() method, so obj.show() calls Child\'s version.',
            'difficulty': 'medium',
            'topic': 'OOP Basics',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Self Parameter',
            'question_text': 'What does self refer to in a class method?',
            'option_a': 'The class itself',
            'option_b': 'The instance of the class',
            'option_c': 'A keyword in Python',
            'option_d': 'The parent class',
            'correct_answer': 'B',
            'explanation': 'self refers to the instance of the class calling the method.',
            'difficulty': 'easy',
            'topic': 'OOP Basics',
            'subject': 'Python',
            'points': 10
        },
    ]
    
    questions.extend(additional_questions)
    
    inserted = 0
    skipped = 0
    
    for q in questions:
        try:
            # Check if question already exists (by title)
            existing = db.execute(
                'SELECT id FROM questions WHERE title = ? AND topic = ?',
                (q['title'], q['topic'])
            ).fetchone()
            
            if existing:
                skipped += 1
                continue
            
            db.execute(
                '''INSERT INTO questions (title, question_text, option_a, option_b, option_c, option_d,
                   correct_answer, explanation, difficulty, topic, subject, language_track, points, is_active, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    q['title'], q['question_text'],
                    q['option_a'], q['option_b'], q['option_c'], q['option_d'],
                    q['correct_answer'], q['explanation'],
                    q['difficulty'], q['topic'], q['subject'],
                    'python', q['points'], 1, datetime.now()
                )
            )
            inserted += 1
        except Exception as e:
            print(f"Error inserting '{q['title']}': {e}")
    
    db.commit()
    total = db.execute('SELECT COUNT(*) as count FROM questions WHERE is_active = 1').fetchone()['count']
    
    print(f"\n{'='*50}")
    print(f"Bulk Questions Seeding Complete!")
    print(f"{'='*50}")
    print(f"Inserted: {inserted} new questions")
    print(f"Skipped: {skipped} duplicates")
    print(f"Total active questions: {total}")
    print(f"{'='*50}\n")
    
    db.close()



def seed_complete_questions():
    """Add questions to fill all gaps across all topics and difficulty levels"""
    init_db()
    db = get_db()
    
    # Comprehensive question set for all topics
    # Each topic gets questions at all three levels
    all_questions = [
        # ========== STRINGS - Additional Questions ==========
        {
            'title': 'String Length',
            'question_text': 'What is the output?\n\nword = "Python"\nprint(len(word))',
            'option_a': '5',
            'option_b': '6',
            'option_c': 'Error',
            'option_d': 'Python',
            'correct_answer': 'B',
            'explanation': 'len() returns the number of characters. "Python" has 6 characters.',
            'difficulty': 'easy',
            'topic': 'Strings',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'String Slicing Basics',
            'question_text': 'What is the output?\n\ntext = "Hello"\nprint(text[1:4])',
            'option_a': 'Hel',
            'option_b': 'ell',
            'option_c': 'ello',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'Slicing [1:4] gets characters at positions 1, 2, 3 (stops before 4).',
            'difficulty': 'easy',
            'topic': 'Strings',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'String Methods',
            'question_text': 'What is the output?\n\ntext = "hello world"\nprint(text.title())',
            'option_a': 'hello world',
            'option_b': 'Hello World',
            'option_c': 'HELLO WORLD',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'title() capitalizes the first letter of each word.',
            'difficulty': 'medium',
            'topic': 'Strings',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'String Replace',
            'question_text': 'What is the output?\n\ntext = "I like cats"\nresult = text.replace("cats", "dogs")\nprint(result)',
            'option_a': 'I like cats',
            'option_b': 'I like dogs',
            'option_c': 'Error',
            'option_d': 'I like',
            'correct_answer': 'B',
            'explanation': 'replace() finds "cats" and replaces it with "dogs".',
            'difficulty': 'medium',
            'topic': 'Strings',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'String Formatting Advanced',
            'question_text': 'What is the output?\n\nname = "Alice"\nage = 25\nresult = f"{name} is {age} years old"\nprint(result)',
            'option_a': 'name is age years old',
            'option_b': 'Alice is 25 years old',
            'option_c': 'Error',
            'option_d': '{name} is {age} years old',
            'correct_answer': 'B',
            'explanation': 'f-strings allow embedding variables inside curly braces.',
            'difficulty': 'hard',
            'topic': 'Strings',
            'subject': 'Python',
            'points': 20
        },
        {
            'title': 'String Join',
            'question_text': 'What is the output?\n\nwords = ["Hello", "World"]\nresult = " ".join(words)\nprint(result)',
            'option_a': 'HelloWorld',
            'option_b': 'Hello World',
            'option_c': 'Error',
            'option_d': '["Hello", "World"]',
            'correct_answer': 'B',
            'explanation': 'join() combines list items with the separator (space in this case).',
            'difficulty': 'hard',
            'topic': 'Strings',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== DATA TYPES - Additional Questions ==========
        {
            'title': 'Integer Type',
            'question_text': 'What is the type of this value: 42?',
            'option_a': 'string',
            'option_b': 'integer',
            'option_c': 'float',
            'option_d': 'boolean',
            'correct_answer': 'B',
            'explanation': '42 is a whole number, so it\'s an integer.',
            'difficulty': 'easy',
            'topic': 'Variables & Data Types',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Float Type',
            'question_text': 'What is the type of this value: 3.14?',
            'option_a': 'string',
            'option_b': 'integer',
            'option_c': 'float',
            'option_d': 'boolean',
            'correct_answer': 'C',
            'explanation': '3.14 has a decimal point, so it\'s a float.',
            'difficulty': 'easy',
            'topic': 'Variables & Data Types',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Type Checking',
            'question_text': 'What is the output?\n\nx = "25"\nprint(type(x))',
            'option_a': "<class 'int'>",
            'option_b': "<class 'str'>",
            'option_c': "<class 'float'>",
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'x has quotes, so it\'s a string, even though it looks like a number.',
            'difficulty': 'medium',
            'topic': 'Variables & Data Types',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Boolean Values',
            'question_text': 'What is the output?\n\nresult = 10 > 5\nprint(result)',
            'option_a': '10 > 5',
            'option_b': 'True',
            'option_c': 'False',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': '10 > 5 is True, so result is True (a boolean value).',
            'difficulty': 'medium',
            'topic': 'Variables & Data Types',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Type Conversion Chain',
            'question_text': 'What is the output?\n\nnum = "123"\nresult = int(num) + float(num)\nprint(result)',
            'option_a': '123123',
            'option_b': '246.0',
            'option_c': 'Error',
            'option_d': '123.123',
            'correct_answer': 'B',
            'explanation': 'int("123") = 123, float("123") = 123.0, so 123 + 123.0 = 246.0 (float).',
            'difficulty': 'hard',
            'topic': 'Variables & Data Types',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== LISTS - Additional Questions ==========
        {
            'title': 'List Creation',
            'question_text': 'Which creates an empty list?',
            'option_a': 'list = []',
            'option_b': 'list = ()',
            'option_c': 'list = {}',
            'option_d': 'list = ""',
            'correct_answer': 'A',
            'explanation': 'Empty lists use square brackets [].',
            'difficulty': 'easy',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'List Index',
            'question_text': 'What is the output?\n\nnums = [10, 20, 30]\nprint(nums[-1])',
            'option_a': '10',
            'option_b': '30',
            'option_c': 'Error',
            'option_d': '20',
            'correct_answer': 'B',
            'explanation': 'Negative index -1 means the last item in the list.',
            'difficulty': 'medium',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'List Insert',
            'question_text': 'What is the output?\n\nitems = [1, 2, 3]\nitems.insert(1, 5)\nprint(items)',
            'option_a': '[1, 5, 2, 3]',
            'option_b': '[1, 2, 5, 3]',
            'option_c': '[5, 1, 2, 3]',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'insert(1, 5) adds 5 at position 1, shifting other items to the right.',
            'difficulty': 'hard',
            'topic': 'Lists',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== CONDITIONALS - Additional Questions ==========
        {
            'title': 'Simple If',
            'question_text': 'What is the output?\n\nx = 5\nif x > 3:\n    print("Yes")\nelse:\n    print("No")',
            'option_a': 'Yes',
            'option_b': 'No',
            'option_c': 'Error',
            'option_d': 'Nothing',
            'correct_answer': 'A',
            'explanation': '5 > 3 is True, so the if block executes.',
            'difficulty': 'easy',
            'topic': 'Conditionals',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Multiple Conditions',
            'question_text': 'What is the output?\n\nage = 25\nif age >= 18 and age <= 65:\n    print("Working age")\nelse:\n    print("Other")',
            'option_a': 'Working age',
            'option_b': 'Other',
            'option_c': 'Error',
            'option_d': 'Nothing',
            'correct_answer': 'A',
            'explanation': 'Both conditions are True (25 >= 18 and 25 <= 65).',
            'difficulty': 'medium',
            'topic': 'Conditionals',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Nested Conditionals',
            'question_text': 'What is the output?\n\nx = 10\ny = 5\nif x > 5:\n    if y > 3:\n        print("Both true")\n    else:\n        print("Only x true")\nelse:\n    print("Neither")',
            'option_a': 'Both true',
            'option_b': 'Only x true',
            'option_c': 'Neither',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'x=10 > 5 (True), y=5 > 3 (True), so nested if executes.',
            'difficulty': 'hard',
            'topic': 'Conditionals',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== LOOPS - Additional Questions ==========
        {
            'title': 'Range Function',
            'question_text': 'What is the output?\n\nfor i in range(3):\n    print(i)',
            'option_a': '0 1 2',
            'option_b': '1 2 3',
            'option_c': '3',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'range(3) generates 0, 1, 2 (starts at 0, stops before 3).',
            'difficulty': 'easy',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'While Loop Counter',
            'question_text': 'What is the output?\n\ncount = 0\nwhile count < 3:\n    print(count)\n    count += 1',
            'option_a': '0 1 2',
            'option_b': '1 2 3',
            'option_c': '0 1 2 3',
            'option_d': 'Infinite loop',
            'correct_answer': 'A',
            'explanation': 'Loop runs while count < 3, printing 0, 1, 2.',
            'difficulty': 'easy',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Loop with Break',
            'question_text': 'What is the output?\n\nfor i in range(10):\n    if i == 5:\n        break\n    print(i)',
            'option_a': '0 1 2 3 4 5',
            'option_b': '0 1 2 3 4',
            'option_c': '1 2 3 4 5',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'break exits when i==5, so only 0-4 are printed.',
            'difficulty': 'medium',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Nested Loops',
            'question_text': 'What is the output?\n\nfor i in range(2):\n    for j in range(2):\n        print(i, j)',
            'option_a': '0 0\n0 1\n1 0\n1 1',
            'option_b': '0 1\n1 0',
            'option_c': '0 0\n1 1',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'Nested loops: outer (i=0,1), inner (j=0,1) for each i.',
            'difficulty': 'hard',
            'topic': 'Loops',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== FUNCTIONS - Additional Questions ==========
        {
            'title': 'Function Call',
            'question_text': 'What is the output?\n\ndef greet():\n    return "Hello"\nprint(greet())',
            'option_a': 'Hello',
            'option_b': 'greet()',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'A',
            'explanation': 'Function returns "Hello", which gets printed.',
            'difficulty': 'easy',
            'topic': 'Functions',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Function with Return',
            'question_text': 'What is the output?\n\ndef add(a, b):\n    return a + b\nresult = add(3, 4)\nprint(result)',
            'option_a': '7',
            'option_b': 'add(3, 4)',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'A',
            'explanation': 'Function returns 3 + 4 = 7.',
            'difficulty': 'easy',
            'topic': 'Functions',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Function Scope',
            'question_text': 'What is the output?\n\nx = 10\ndef test():\n    x = 20\n    return x\nprint(test())\nprint(x)',
            'option_a': '20\n10',
            'option_b': '10\n20',
            'option_c': '20\n20',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'Inside function, x=20 is local. Outside, x=10 remains unchanged.',
            'difficulty': 'hard',
            'topic': 'Functions',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== DICTIONARIES - Additional Questions ==========
        {
            'title': 'Dictionary Access',
            'question_text': 'What is the output?\n\nstudent = {"name": "John", "age": 20}\nprint(student["name"])',
            'option_a': 'name',
            'option_b': 'John',
            'option_c': 'Error',
            'option_d': '{"name": "John"}',
            'correct_answer': 'B',
            'explanation': 'student["name"] gets the value associated with key "name".',
            'difficulty': 'easy',
            'topic': 'Dictionaries',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Dictionary Update',
            'question_text': 'What is the output?\n\ninfo = {"name": "Alice"}\ninfo["age"] = 25\nprint(info)',
            'option_a': '{"name": "Alice"}',
            'option_b': '{"name": "Alice", "age": 25}',
            'option_c': 'Error',
            'option_d': '{"age": 25}',
            'correct_answer': 'B',
            'explanation': 'Adding a new key-value pair updates the dictionary.',
            'difficulty': 'medium',
            'topic': 'Dictionaries',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Dictionary Methods',
            'question_text': 'What is the output?\n\ndata = {"a": 1, "b": 2}\nkeys = list(data.keys())\nprint(keys)',
            'option_a': '[1, 2]',
            'option_b': '["a", "b"]',
            'option_c': 'Error',
            'option_d': '{"a", "b"}',
            'correct_answer': 'B',
            'explanation': 'keys() returns the dictionary keys, converted to a list.',
            'difficulty': 'hard',
            'topic': 'Dictionaries',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== TUPLES & SETS - Additional Questions ==========
        {
            'title': 'Tuple Creation',
            'question_text': 'Which creates a tuple?',
            'option_a': 'data = [1, 2, 3]',
            'option_b': 'data = (1, 2, 3)',
            'option_c': 'data = {1, 2, 3}',
            'option_d': 'data = {1: 2, 3: 4}',
            'correct_answer': 'B',
            'explanation': 'Tuples use parentheses ().',
            'difficulty': 'easy',
            'topic': 'Tuples & Sets',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Set Uniqueness',
            'question_text': 'What is the output?\n\nnumbers = {1, 2, 2, 3, 3, 3}\nprint(numbers)',
            'option_a': '{1, 2, 2, 3, 3, 3}',
            'option_b': '{1, 2, 3}',
            'option_c': 'Error',
            'option_d': '[1, 2, 3]',
            'correct_answer': 'B',
            'explanation': 'Sets automatically remove duplicates, keeping only unique values.',
            'difficulty': 'medium',
            'topic': 'Tuples & Sets',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Tuple Unpacking',
            'question_text': 'What is the output?\n\npoint = (3, 4)\nx, y = point\nprint(x, y)',
            'option_a': '(3, 4)',
            'option_b': '3 4',
            'option_c': 'Error',
            'option_d': 'point',
            'correct_answer': 'B',
            'explanation': 'Tuple unpacking assigns values: x=3, y=4.',
            'difficulty': 'hard',
            'topic': 'Tuples & Sets',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== ERROR HANDLING - Additional Questions ==========
        {
            'title': 'Try Except Basics',
            'question_text': 'What is the output?\n\ntry:\n    result = 10 / 0\n    print(result)\nexcept:\n    print("Error occurred")',
            'option_a': 'Error occurred',
            'option_b': '0',
            'option_c': '10',
            'option_d': 'Nothing',
            'correct_answer': 'A',
            'explanation': 'Division by zero causes an error, which is caught by except block.',
            'difficulty': 'easy',
            'topic': 'Basic Error Handling',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Input Error Handling',
            'question_text': 'What happens if user types "hello" here?\n\ntry:\n    age = int(input("Age: "))\n    print(age)\nexcept:\n    print("Invalid number")',
            'option_a': 'Prints "hello"',
            'option_b': 'Prints "Invalid number"',
            'option_c': 'Program crashes',
            'option_d': 'Nothing',
            'correct_answer': 'B',
            'explanation': 'int("hello") fails, so except block executes.',
            'difficulty': 'medium',
            'topic': 'Basic Error Handling',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Multiple Try Blocks',
            'question_text': 'What is the output?\n\ntry:\n    num = int("abc")\nexcept:\n    num = 0\nprint(num)',
            'option_a': 'abc',
            'option_b': '0',
            'option_c': 'Error',
            'option_d': 'None',
            'correct_answer': 'B',
            'explanation': 'int("abc") fails, except sets num=0, then prints 0.',
            'difficulty': 'hard',
            'topic': 'Basic Error Handling',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== FILE HANDLING - Additional Questions ==========
        {
            'title': 'File Write Mode',
            'question_text': 'What does "w" mean in open("file.txt", "w")?',
            'option_a': 'Write mode - creates new file or overwrites existing',
            'option_b': 'Read mode',
            'option_c': 'Append mode',
            'option_d': 'Binary mode',
            'correct_answer': 'A',
            'explanation': '"w" is write mode - it creates a new file or overwrites if it exists.',
            'difficulty': 'easy',
            'topic': 'File Handling',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'File Read',
            'question_text': 'What is the output if file contains "Hello"?\n\nwith open("test.txt", "r") as f:\n    content = f.read()\nprint(content)',
            'option_a': 'Hello',
            'option_b': 'test.txt',
            'option_c': 'Error',
            'option_d': 'Nothing',
            'correct_answer': 'A',
            'explanation': 'read() gets all content from the file.',
            'difficulty': 'medium',
            'topic': 'File Handling',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'File Append',
            'question_text': 'What happens if you run this twice?\n\nwith open("log.txt", "a") as f:\n    f.write("Entry\\n")',
            'option_a': 'File gets overwritten each time',
            'option_b': 'New entry is added each time',
            'option_c': 'Error occurs',
            'option_d': 'Nothing happens',
            'correct_answer': 'B',
            'explanation': '"a" mode appends - each run adds a new line without overwriting.',
            'difficulty': 'hard',
            'topic': 'File Handling',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== INPUT & OUTPUT - Additional Questions ==========
        {
            'title': 'Input Function',
            'question_text': 'What does input() return?',
            'option_a': 'A number',
            'option_b': 'A string (text)',
            'option_c': 'A boolean',
            'option_d': 'Nothing',
            'correct_answer': 'B',
            'explanation': 'input() always returns a string, even if the user types a number.',
            'difficulty': 'easy',
            'topic': 'Input & Output',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Print Multiple Values',
            'question_text': 'What is the output?\n\nprint("Hello", "World", 42)',
            'option_a': 'HelloWorld42',
            'option_b': 'Hello World 42',
            'option_c': 'Error',
            'option_d': '("Hello", "World", 42)',
            'correct_answer': 'B',
            'explanation': 'print() separates multiple arguments with spaces by default.',
            'difficulty': 'medium',
            'topic': 'Input & Output',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Input Conversion',
            'question_text': 'What is the output if user enters "10"?\n\nage = input("Age: ")\nprint(age + 5)',
            'option_a': '15',
            'option_b': '105',
            'option_c': 'Error',
            'option_d': '10 5',
            'correct_answer': 'C',
            'explanation': 'input() returns string "10", so "10" + 5 fails (can\'t add string and number).',
            'difficulty': 'hard',
            'topic': 'Input & Output',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== OPERATORS - Additional Questions ==========
        {
            'title': 'Modulus Operator',
            'question_text': 'What is the output?\n\nresult = 10 % 3\nprint(result)',
            'option_a': '3',
            'option_b': '1',
            'option_c': '0',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': '% gives remainder: 10 divided by 3 is 3 remainder 1.',
            'difficulty': 'easy',
            'topic': 'Operators',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Floor Division',
            'question_text': 'What is the output?\n\nresult = 10 // 3\nprint(result)',
            'option_a': '3.33',
            'option_b': '3',
            'option_c': '4',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': '// is floor division - drops decimal part, gives whole number result.',
            'difficulty': 'medium',
            'topic': 'Operators',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Operator Precedence',
            'question_text': 'What is the output?\n\nresult = 2 + 3 * 4\nprint(result)',
            'option_a': '20',
            'option_b': '14',
            'option_c': '24',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'Multiplication happens first: 3*4=12, then 2+12=14.',
            'difficulty': 'hard',
            'topic': 'Operators',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== INTRODUCTION TO PYTHON - Additional Questions ==========
        {
            'title': 'Print Statement',
            'question_text': 'What is the output?\n\nprint("Hello")\nprint("World")',
            'option_a': 'HelloWorld',
            'option_b': 'Hello\nWorld',
            'option_c': 'Error',
            'option_d': 'Nothing',
            'correct_answer': 'B',
            'explanation': 'Each print() statement creates a new line.',
            'difficulty': 'easy',
            'topic': 'Introduction to Python',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Comments',
            'question_text': 'What is the output?\n\n# This is a comment\nprint("Hello")',
            'option_a': '# This is a comment\nHello',
            'option_b': 'Hello',
            'option_c': 'Error',
            'option_d': 'Nothing',
            'correct_answer': 'B',
            'explanation': 'Comments (starting with #) are ignored by Python.',
            'difficulty': 'easy',
            'topic': 'Introduction to Python',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Multiple Prints',
            'question_text': 'What is the output?\n\nprint("A")\nprint("B")\nprint("C")',
            'option_a': 'ABC',
            'option_b': 'A\nB\nC',
            'option_c': 'Error',
            'option_d': 'A B C',
            'correct_answer': 'B',
            'explanation': 'Each print() puts output on a new line.',
            'difficulty': 'medium',
            'topic': 'Introduction to Python',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Print Formatting',
            'question_text': 'What is the output?\n\nname = "Python"\nprint("I love", name)',
            'option_a': 'I love Python',
            'option_b': 'I lovename',
            'option_c': 'Error',
            'option_d': 'I love',
            'correct_answer': 'A',
            'explanation': 'print() separates arguments with spaces automatically.',
            'difficulty': 'hard',
            'topic': 'Introduction to Python',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== DATA STRUCTURES - Additional Questions ==========
        {
            'title': 'List vs Tuple',
            'question_text': 'Which is mutable (can be changed)?',
            'option_a': 'List',
            'option_b': 'Tuple',
            'option_c': 'Both',
            'option_d': 'Neither',
            'correct_answer': 'A',
            'explanation': 'Lists are mutable (can be modified), tuples are immutable (cannot be changed).',
            'difficulty': 'easy',
            'topic': 'Data Structures',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Dictionary Keys',
            'question_text': 'What can be used as dictionary keys?',
            'option_a': 'Only strings',
            'option_b': 'Only numbers',
            'option_c': 'Immutable types (strings, numbers, tuples)',
            'option_d': 'Any type',
            'correct_answer': 'C',
            'explanation': 'Dictionary keys must be immutable (unchangeable) types like strings, numbers, or tuples.',
            'difficulty': 'medium',
            'topic': 'Data Structures',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Nested Data Structures',
            'question_text': 'What is the output?\n\ndata = {"students": [{"name": "John"}, {"name": "Jane"}]}\nprint(data["students"][0]["name"])',
            'option_a': 'students',
            'option_b': 'John',
            'option_c': 'Error',
            'option_d': '[{"name": "John"}]',
            'correct_answer': 'B',
            'explanation': 'Nested access: data["students"] gets list, [0] gets first dict, ["name"] gets value.',
            'difficulty': 'hard',
            'topic': 'Data Structures',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== DATA TYPES - Additional Questions ==========
        {
            'title': 'String Type',
            'question_text': 'What is the type of "hello"?',
            'option_a': 'int',
            'option_b': 'str',
            'option_c': 'float',
            'option_d': 'bool',
            'correct_answer': 'B',
            'explanation': 'Text in quotes is a string (str) type.',
            'difficulty': 'easy',
            'topic': 'Data Types',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Boolean Type',
            'question_text': 'What is the type of True?',
            'option_a': 'int',
            'option_b': 'str',
            'option_c': 'bool',
            'option_d': 'None',
            'correct_answer': 'C',
            'explanation': 'True and False are boolean (bool) values.',
            'difficulty': 'easy',
            'topic': 'Data Types',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Type Checking',
            'question_text': 'What is the output?\n\nx = 5.0\nprint(type(x) == int)',
            'option_a': 'True',
            'option_b': 'False',
            'option_c': 'Error',
            'option_d': '5.0',
            'correct_answer': 'B',
            'explanation': '5.0 is a float, not an int, so type(x) == int is False.',
            'difficulty': 'hard',
            'topic': 'Data Types',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== EXCEPTION HANDLING - Additional Questions ==========
        {
            'title': 'Try Except',
            'question_text': 'What is the output?\n\ntry:\n    x = 10 / 2\n    print(x)\nexcept:\n    print("Error")',
            'option_a': '5',
            'option_b': 'Error',
            'option_c': '10 / 2',
            'option_d': 'Nothing',
            'correct_answer': 'A',
            'explanation': '10/2 = 5, no error occurs, so try block executes normally.',
            'difficulty': 'easy',
            'topic': 'Exception Handling',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Specific Exception',
            'question_text': 'What is the output?\n\ntry:\n    num = int("abc")\nexcept ValueError:\n    print("Invalid number")\nexcept:\n    print("Other error")',
            'option_a': 'Invalid number',
            'option_b': 'Other error',
            'option_c': 'Error',
            'option_d': 'Nothing',
            'correct_answer': 'A',
            'explanation': 'int("abc") raises ValueError, which is caught by the first except block.',
            'difficulty': 'medium',
            'topic': 'Exception Handling',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Finally Block',
            'question_text': 'What is the output?\n\ntry:\n    x = 10 / 0\nexcept:\n    print("Error")\nfinally:\n    print("Done")',
            'option_a': 'Error',
            'option_b': 'Done',
            'option_c': 'Error\nDone',
            'option_d': 'Nothing',
            'correct_answer': 'C',
            'explanation': 'finally block always executes, even if an exception occurs.',
            'difficulty': 'hard',
            'topic': 'Exception Handling',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== LIST COMPREHENSION - Additional Questions ==========
        {
            'title': 'Basic List Comprehension',
            'question_text': 'What is the output?\n\nnumbers = [x*2 for x in range(3)]\nprint(numbers)',
            'option_a': '[0, 2, 4]',
            'option_b': '[2, 4, 6]',
            'option_c': 'Error',
            'option_d': '[0, 1, 2]',
            'correct_answer': 'A',
            'explanation': 'For each x in [0,1,2], multiply by 2: [0*2, 1*2, 2*2] = [0, 2, 4].',
            'difficulty': 'easy',
            'topic': 'List Comprehension',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'List Comprehension with Condition',
            'question_text': 'What is the output?\n\nnumbers = [x for x in range(5) if x % 2 == 0]\nprint(numbers)',
            'option_a': '[0, 1, 2, 3, 4]',
            'option_b': '[0, 2, 4]',
            'option_c': '[1, 3]',
            'option_d': 'Error',
            'correct_answer': 'B',
            'explanation': 'Only includes x where x % 2 == 0 (even numbers): 0, 2, 4.',
            'difficulty': 'medium',
            'topic': 'List Comprehension',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Nested List Comprehension',
            'question_text': 'What is the output?\n\nresult = [[i*j for j in range(2)] for i in range(2)]\nprint(result)',
            'option_a': '[[0, 0], [0, 1]]',
            'option_b': '[[0, 0], [0, 2]]',
            'option_c': 'Error',
            'option_d': '[0, 0, 0, 0]',
            'correct_answer': 'A',
            'explanation': 'Nested comprehension: for i=0: [0*0, 0*1]=[0,0]; for i=1: [1*0, 1*1]=[0,1].',
            'difficulty': 'hard',
            'topic': 'List Comprehension',
            'subject': 'Python',
            'points': 20
        },
        
        # ========== RECURSION - Additional Questions ==========
        {
            'title': 'Simple Recursion',
            'question_text': 'What does this function do?\n\ndef count_down(n):\n    if n <= 0:\n        return\n    print(n)\n    count_down(n-1)',
            'option_a': 'Prints numbers from n down to 1',
            'option_b': 'Prints numbers from 1 to n',
            'option_c': 'Prints n forever',
            'option_d': 'Error',
            'correct_answer': 'A',
            'explanation': 'Function calls itself with n-1 until n <= 0, printing each number.',
            'difficulty': 'easy',
            'topic': 'Recursion',
            'subject': 'Python',
            'points': 10
        },
        {
            'title': 'Recursive Factorial',
            'question_text': 'What is the output?\n\ndef fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n-1)\nprint(fact(4))',
            'option_a': '10',
            'option_b': '24',
            'option_c': 'Error',
            'option_d': '4',
            'correct_answer': 'B',
            'explanation': 'fact(4) = 4 * fact(3) = 4 * 3 * fact(2) = 4 * 3 * 2 * fact(1) = 4 * 3 * 2 * 1 = 24.',
            'difficulty': 'medium',
            'topic': 'Recursion',
            'subject': 'Python',
            'points': 15
        },
        {
            'title': 'Recursive Sum',
            'question_text': 'What is the output?\n\ndef sum_list(nums):\n    if not nums:\n        return 0\n    return nums[0] + sum_list(nums[1:])\nprint(sum_list([1, 2, 3]))',
            'option_a': '6',
            'option_b': '3',
            'option_c': 'Error',
            'option_d': '[1, 2, 3]',
            'correct_answer': 'A',
            'explanation': 'Recursively adds first element to sum of rest: 1 + sum([2,3]) = 1 + 2 + sum([3]) = 1 + 2 + 3 = 6.',
            'difficulty': 'hard',
            'topic': 'Recursion',
            'subject': 'Python',
            'points': 20
        }
    ]
    
    inserted = 0
    skipped = 0
    
    for q in all_questions:
        try:
            # Check if question already exists
            existing = db.execute(
                'SELECT id FROM questions WHERE title = ? AND topic = ? AND difficulty = ?',
                (q['title'], q['topic'], q['difficulty'])
            ).fetchone()
            
            if existing:
                skipped += 1
                continue
            
            db.execute(
                '''INSERT INTO questions (title, question_text, option_a, option_b, option_c, option_d,
                   correct_answer, explanation, difficulty, topic, subject, language_track, points, is_active, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    q['title'], q['question_text'],
                    q['option_a'], q['option_b'], q['option_c'], q['option_d'],
                    q['correct_answer'], q['explanation'],
                    q['difficulty'], q['topic'], q['subject'],
                    'python', q['points'], 1, datetime.now()
                )
            )
            inserted += 1
        except Exception as e:
            print(f"Error inserting '{q['title']}': {e}")
    
    db.commit()
    
    # Check coverage
    coverage = db.execute('''
        SELECT topic, difficulty, COUNT(*) as count
        FROM questions
        WHERE is_active = 1
        GROUP BY topic, difficulty
        ORDER BY topic, difficulty
    ''').fetchall()
    
    total = db.execute('SELECT COUNT(*) as count FROM questions WHERE is_active = 1').fetchone()['count']
    
    print(f"\n{'='*60}")
    print(f"Complete Questions Seeding Finished!")
    print(f"{'='*60}")
    print(f"Inserted: {inserted} new questions")
    print(f"Skipped: {skipped} duplicates")
    print(f"Total active questions: {total}")
    print(f"\nCoverage by Topic and Difficulty:")
    for row in coverage:
        print(f"  {row['topic']} - {row['difficulty']}: {row['count']} questions")
    print(f"{'='*60}\n")
    
    db.close()



def seed_learning_notes():
    """Add comprehensive learning notes and projects"""
    init_db()
    db = get_db()
    
    # Get or create Python subject
    python_subject = db.execute(
        'SELECT id FROM subjects WHERE name = ?', ('Python',)
    ).fetchone()
    
    if not python_subject:
        db.execute(
            '''INSERT INTO subjects (name, description, language_track, order_index, created_at)
               VALUES (?, ?, ?, ?, ?)''',
            ('Python', 'Learn Python programming from basics to advanced concepts', 'python', 1, datetime.now())
        )
        db.commit()
        python_subject = db.execute(
            'SELECT id FROM subjects WHERE name = ?', ('Python',)
        ).fetchone()
    
    subject_id = python_subject['id']
    
    # Topic definitions with their notes
    topics_data = [
        {
            'name': 'Introduction to Python',
            'description': 'Getting started with Python programming',
            'order': 1,
            'notes': [
                {
                    'title': 'What is Python?',
                    'content': '''<h2>What is Python?</h2>
<p>Python is a programming language that's really popular these days. The good news is, it's also one of the easiest languages to learn when you're starting out.</p>

<h3>Why Python?</h3>
<ul>
<li>It reads almost like English, so it's easier to understand</li>
<li>You don't need to worry about complicated syntax</li>
<li>It's used everywhere - websites, data science, automation, and more</li>
</ul>

<h3>Your First Program</h3>
<p>Let's start with the classic "Hello World" program. This is what everyone writes first:</p>

<pre><code>print("Hello, World!")
</code></pre>

<p>That's it! Just one line. When you run this, it will display "Hello, World!" on your screen.</p>

<h3>What's happening here?</h3>
<p>The word <code>print</code> is a function in Python. Think of it like a tool that displays text. The text you want to display goes inside the parentheses, and we put quotes around it to tell Python it's text (not code).</p>

<h3>Common Beginner Mistake</h3>
<p>If you forget the quotes, Python will think you're trying to use a variable. For example:</p>

<pre><code>print(Hello, World!)  # This will give an error!
</code></pre>

<p>Always remember to put quotes around text you want to display.</p>

<h3>Practice Task</h3>
<p>Try writing a program that prints your name. Then try printing three different messages on separate lines.</p>'''
                }
            ]
        },
        {
            'name': 'Variables & Data Types',
            'description': 'Understanding how to store and work with different types of data',
            'order': 2,
            'notes': [
                {
                    'title': 'Variables in Python',
                    'content': '''<h2>Variables in Python</h2>
<p>Variables are like boxes where you store information. You give the box a name, and you can put different things inside it.</p>

<h3>Creating a Variable</h3>
<p>Here's how you create a variable:</p>

<pre><code>name = "John"
age = 20
</code></pre>

<p>In the first line, we created a variable called <code>name</code> and stored the text "John" in it. In the second line, we created <code>age</code> and stored the number 20.</p>

<h3>Using Variables</h3>
<p>Once you create a variable, you can use it anywhere:</p>

<pre><code>name = "Sarah"
print(name)  # This will print: Sarah

age = 25
print(age)   # This will print: 25
</code></pre>

<h3>Data Types</h3>
<p>Python has different types of data:</p>

<ul>
<li><strong>String:</strong> Text, always in quotes. Example: <code>"Hello"</code></li>
<li><strong>Integer:</strong> Whole numbers. Example: <code>42</code></li>
<li><strong>Float:</strong> Decimal numbers. Example: <code>3.14</code></li>
<li><strong>Boolean:</strong> True or False. Example: <code>True</code></li>
</ul>

<h3>Example with Different Types</h3>
<pre><code>student_name = "Alex"        # String
student_age = 19            # Integer
student_height = 5.8         # Float
is_student = True           # Boolean

print(student_name)
print(student_age)
</code></pre>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Forgetting quotes around text: <code>name = John</code> (wrong) vs <code>name = "John"</code> (correct)</li>
<li>Using spaces in variable names: <code>my name = "John"</code> (wrong) vs <code>my_name = "John"</code> (correct)</li>
<li>Starting variable names with numbers: <code>2name = "John"</code> (wrong)</li>
</ul>

<h3>Practice Task</h3>
<p>Create variables for your favorite color, your age, and whether you like programming (True or False). Then print all three.</p>'''
                }
            ]
        },
        {
            'name': 'Input & Output',
            'description': 'Getting input from users and displaying output',
            'order': 3,
            'notes': [
                {
                    'title': 'Getting User Input',
                    'content': '''<h2>Getting User Input</h2>
<p>So far we've only printed things. But what if we want the program to ask the user for information? That's where <code>input()</code> comes in.</p>

<h3>Basic Input</h3>
<p>Here's a simple example:</p>

<pre><code>name = input("What is your name? ")
print("Hello, " + name)
</code></pre>

<p>When you run this, the program will wait for you to type something. After you press Enter, it will print "Hello, " followed by whatever you typed.</p>

<h3>How it Works</h3>
<p>The <code>input()</code> function shows a message (the text inside the quotes) and waits for the user to type something. Whatever they type gets stored in the variable.</p>

<h3>Input with Numbers</h3>
<p>Here's something important: <code>input()</code> always gives you text, even if the user types a number. So if you want to do math, you need to convert it:</p>

<pre><code>age = input("How old are you? ")
age = int(age)  # Convert text to number
print("Next year you'll be", age + 1)
</code></pre>

<p>The <code>int()</code> function converts text to a whole number. If you need decimals, use <code>float()</code> instead.</p>

<h3>Putting it Together</h3>
<pre><code>name = input("Enter your name: ")
age = input("Enter your age: ")
age = int(age)

print("Hi", name, "! You are", age, "years old.")
</code></pre>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Trying to do math with input without converting: <code>age = input("Age? ") + 1</code> (wrong)</li>
<li>Forgetting the space in the input message: <code>input("Name:")</code> looks better as <code>input("Name: ")</code></li>
</ul>

<h3>Practice Task</h3>
<p>Write a program that asks for the user's favorite food and favorite color, then prints a sentence using both.</p>'''
                }
            ]
        },
        {
            'name': 'Operators',
            'description': 'Mathematical and logical operators in Python',
            'order': 4,
            'notes': [
                {
                    'title': 'Basic Operators',
                    'content': '''<h2>Basic Operators in Python</h2>
<p>Operators let you do things with numbers and variables. You probably know most of them from math class.</p>

<h3>Math Operators</h3>
<p>Here are the basic math operators:</p>

<pre><code>a = 10
b = 3

print(a + b)  # Addition: 13
print(a - b)  # Subtraction: 7
print(a * b)  # Multiplication: 30
print(a / b)  # Division: 3.333...
print(a // b) # Floor division: 3 (drops decimal)
print(a % b)  # Modulus: 1 (remainder)
print(a ** b) # Exponentiation: 1000 (10 to power of 3)
</code></pre>

<h3>Understanding Each One</h3>
<ul>
<li><code>+</code> adds numbers together</li>
<li><code>-</code> subtracts</li>
<li><code>*</code> multiplies</li>
<li><code>/</code> divides and gives you a decimal result</li>
<li><code>//</code> divides but drops the decimal part</li>
<li><code>%</code> gives you the remainder (useful for checking if a number is even or odd)</li>
<li><code>**</code> raises a number to a power</li>
</ul>

<h3>Using with Variables</h3>
<pre><code>price = 50
discount = 10
final_price = price - discount
print("Final price:", final_price)
</code></pre>

<h3>Comparison Operators</h3>
<p>These compare two values and give you True or False:</p>

<pre><code>a = 5
b = 3

print(a > b)   # True (5 is greater than 3)
print(a < b)   # False
print(a == b)  # False (== means "is equal to")
print(a != b)  # True (!= means "is not equal to")
print(a >= b)  # True (>= means "greater than or equal")
print(a <= b)  # False
</code></pre>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Using <code>=</code> instead of <code>==</code> for comparison: <code>if a = 5:</code> (wrong) vs <code>if a == 5:</code> (correct)</li>
<li>Forgetting that division always gives decimals: <code>10 / 3</code> gives <code>3.333...</code>, not <code>3</code></li>
</ul>

<h3>Practice Task</h3>
<p>Create two variables with numbers. Calculate their sum, difference, product, and quotient. Print all four results.</p>'''
                }
            ]
        },
        {
            'name': 'Conditional Statements',
            'description': 'Making decisions in your code with if/else',
            'order': 5,
            'notes': [
                {
                    'title': 'If and Else Statements',
                    'content': '''<h2>If and Else Statements</h2>
<p>Sometimes you want your program to make decisions. Like "if the user is 18 or older, show this message, otherwise show a different message." That's what if/else is for.</p>

<h3>Basic If Statement</h3>
<p>Here's the simplest form:</p>

<pre><code>age = 20

if age >= 18:
    print("You are an adult")
</code></pre>

<p>If the condition (age >= 18) is true, the code inside runs. If it's false, nothing happens.</p>

<h3>If-Else</h3>
<p>What if you want to do something when the condition is false? Use else:</p>

<pre><code>age = 15

if age >= 18:
    print("You are an adult")
else:
    print("You are a minor")
</code></pre>

<p>Now one of the two messages will always print, depending on the age.</p>

<h3>If-Elif-Else</h3>
<p>You can check multiple conditions:</p>

<pre><code>score = 85

if score >= 90:
    print("Grade: A")
elif score >= 80:
    print("Grade: B")
elif score >= 70:
    print("Grade: C")
else:
    print("Grade: F")
</code></pre>

<p>Python checks each condition in order. As soon as one is true, it runs that code and stops checking the rest.</p>

<h3>Important: Indentation</h3>
<p>Notice how the code inside if/else is indented? That's how Python knows what code belongs to the if statement. If you forget the indentation, you'll get an error.</p>

<h3>Real Example</h3>
<pre><code>temperature = 25

if temperature > 30:
    print("It's hot outside!")
elif temperature > 20:
    print("Nice weather")
else:
    print("It's cold")
</code></pre>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Forgetting the colon at the end: <code>if age >= 18</code> (wrong) vs <code>if age >= 18:</code> (correct)</li>
<li>Wrong indentation: Python is very picky about this</li>
<li>Using <code>=</code> instead of <code>==</code> in conditions</li>
</ul>

<h3>Practice Task</h3>
<p>Write a program that asks for a number. If it's positive, print "Positive". If it's negative, print "Negative". If it's zero, print "Zero".</p>'''
                }
            ]
        },
        {
            'name': 'Loops',
            'description': 'Repeating code with for and while loops',
            'order': 6,
            'notes': [
                {
                    'title': 'For Loops',
                    'content': '''<h2>For Loops</h2>
<p>What if you want to do something multiple times? You could copy and paste the code, but that's not a good idea. Instead, use a loop.</p>

<h3>Basic For Loop</h3>
<p>Here's a simple example:</p>

<pre><code>for i in range(5):
    print("Hello")
</code></pre>

<p>This will print "Hello" five times. The <code>range(5)</code> creates numbers from 0 to 4 (five numbers total).</p>

<h3>Using the Loop Variable</h3>
<p>You can use the variable <code>i</code> (or whatever you name it) inside the loop:</p>

<pre><code>for i in range(5):
    print("Number:", i)
</code></pre>

<p>This prints: Number: 0, Number: 1, Number: 2, Number: 3, Number: 4</p>

<h3>Range with Start and End</h3>
<pre><code>for i in range(1, 6):
    print(i)
</code></pre>

<p>This prints numbers from 1 to 5. The first number is where to start, the second is where to stop (but not including that number).</p>

<h3>Looping Through a List</h3>
<pre><code>fruits = ["apple", "banana", "orange"]

for fruit in fruits:
    print(fruit)
</code></pre>

<p>This goes through each item in the list and prints it. Much easier than writing three separate print statements!</p>

<h3>While Loops</h3>
<p>While loops keep running as long as a condition is true:</p>

<pre><code>count = 0
while count < 5:
    print(count)
    count = count + 1
</code></pre>

<p>This prints 0, 1, 2, 3, 4. The loop stops when count becomes 5.</p>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Forgetting to update the counter in while loops (causes infinite loop!)</li>
<li>Using <code>range(5)</code> and expecting it to include 5 (it goes 0-4)</li>
<li>Forgetting the colon after <code>for</code> or <code>while</code></li>
</ul>

<h3>Practice Task</h3>
<p>Write a loop that prints the numbers 1 to 10. Then write another loop that prints "Python" 7 times.</p>'''
                }
            ]
        },
        {
            'name': 'Strings',
            'description': 'Working with text in Python',
            'order': 7,
            'notes': [
                {
                    'title': 'Working with Strings',
                    'content': '''<h2>Working with Strings</h2>
<p>Strings are just text. You've been using them already with <code>print()</code> and <code>input()</code>. But there's more you can do with them.</p>

<h3>String Basics</h3>
<pre><code>name = "Python"
message = 'Hello World'
</code></pre>

<p>You can use either single quotes or double quotes. Both work the same way.</p>

<h3>Combining Strings</h3>
<p>You can add strings together (this is called concatenation):</p>

<pre><code>first_name = "John"
last_name = "Doe"
full_name = first_name + " " + last_name
print(full_name)  # Prints: John Doe
</code></pre>

<p>Notice we added a space between them with <code>" "</code>.</p>

<h3>String Methods</h3>
<p>Python has built-in functions for strings. Here are some useful ones:</p>

<pre><code>text = "hello world"

print(text.upper())      # HELLO WORLD
print(text.lower())      # hello world
print(text.capitalize()) # Hello world
print(len(text))         # 11 (number of characters)
</code></pre>

<h3>Accessing Characters</h3>
<p>You can get individual characters from a string:</p>

<pre><code>word = "Python"
print(word[0])  # P (first character)
print(word[1])  # y
print(word[-1]) # n (last character)
</code></pre>

<p>Remember, counting starts at 0, not 1!</p>

<h3>String Formatting</h3>
<p>There's a nice way to put variables into strings:</p>

<pre><code>name = "Alice"
age = 20
message = f"My name is {name} and I am {age} years old"
print(message)
</code></pre>

<p>The <code>f</code> before the quotes means "format". You can put variables inside <code>{}</code>.</p>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Trying to add a number to a string: <code>"Age: " + 20</code> (wrong) - convert the number first: <code>"Age: " + str(20)</code></li>
<li>Forgetting that string positions start at 0</li>
</ul>

<h3>Practice Task</h3>
<p>Create a string with your name. Print it in uppercase, then print how many characters it has.</p>'''
                }
            ]
        },
        {
            'name': 'Lists',
            'description': 'Storing multiple items in a list',
            'order': 8,
            'notes': [
                {
                    'title': 'Lists in Python',
                    'content': '''<h2>Lists in Python</h2>
<p>A list is like a container that can hold multiple items. Think of it like a shopping list - you can have many items on it.</p>

<h3>Creating a List</h3>
<pre><code>fruits = ["apple", "banana", "orange"]
numbers = [1, 2, 3, 4, 5]
mixed = ["hello", 42, 3.14, True]
</code></pre>

<p>You can put anything in a list - strings, numbers, even other lists!</p>

<h3>Accessing Items</h3>
<p>You get items from a list by their position (starting from 0):</p>

<pre><code>fruits = ["apple", "banana", "orange"]
print(fruits[0])  # apple
print(fruits[1])  # banana
print(fruits[2])  # orange
</code></pre>

<h3>Adding Items</h3>
<p>You can add items to a list:</p>

<pre><code>fruits = ["apple", "banana"]
fruits.append("orange")
print(fruits)  # ["apple", "banana", "orange"]
</code></pre>

<p>The <code>append()</code> method adds an item to the end of the list.</p>

<h3>List Length</h3>
<pre><code>fruits = ["apple", "banana", "orange"]
print(len(fruits))  # 3
</code></pre>

<h3>Looping Through a List</h3>
<pre><code>fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(fruit)
</code></pre>

<p>This prints each fruit on a separate line.</p>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Forgetting that list positions start at 0, not 1</li>
<li>Trying to access position that doesn't exist: if list has 3 items, <code>list[3]</code> will give an error (use 0, 1, or 2)</li>
<li>Confusing <code>append()</code> with <code>add()</code> - it's append, not add</li>
</ul>

<h3>Practice Task</h3>
<p>Create a list of your three favorite colors. Print each one using a loop. Then add a fourth color and print the list again.</p>'''
                }
            ]
        },
        {
            'name': 'Tuples & Sets',
            'description': 'Other ways to store multiple items',
            'order': 9,
            'notes': [
                {
                    'title': 'Tuples and Sets',
                    'content': '''<h2>Tuples and Sets</h2>
<p>Lists aren't the only way to store multiple items. Python has tuples and sets too. They're similar but have some differences.</p>

<h3>Tuples</h3>
<p>Tuples are like lists, but you can't change them after creating them. You use parentheses instead of square brackets:</p>

<pre><code>coordinates = (10, 20)
print(coordinates[0])  # 10
</code></pre>

<p>You can access items the same way as lists, but you can't add or remove items. That's why they're called "immutable" (can't be changed).</p>

<h3>When to Use Tuples</h3>
<p>Use tuples when you have data that shouldn't change, like coordinates or a person's date of birth:</p>

<pre><code>birth_date = (1990, 5, 15)  # Year, month, day
point = (3, 4)  # x, y coordinates
</code></pre>

<h3>Sets</h3>
<p>Sets are like lists, but they can't have duplicate items. You use curly braces:</p>

<pre><code>fruits = {"apple", "banana", "orange"}
</code></pre>

<p>If you try to add a duplicate, it just ignores it:</p>

<pre><code>fruits = {"apple", "banana", "apple"}
print(fruits)  # {"apple", "banana"} - only one apple
</code></pre>

<h3>Common Operations</h3>
<pre><code># Adding to a set
fruits = {"apple", "banana"}
fruits.add("orange")

# Checking if something is in a set
if "apple" in fruits:
    print("We have apples!")
</code></pre>

<h3>When to Use What?</h3>
<ul>
<li><strong>List:</strong> When you need to change items, have duplicates, or care about order</li>
<li><strong>Tuple:</strong> When data shouldn't change (like coordinates)</li>
<li><strong>Set:</strong> When you need unique items and don't care about order</li>
</ul>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Trying to change a tuple (you can't!)</li>
<li>Confusing when to use parentheses vs brackets vs braces</li>
</ul>

<h3>Practice Task</h3>
<p>Create a tuple with your birth year, month, and day. Then create a set of your favorite programming languages (make sure to add a duplicate and see what happens).</p>'''
                }
            ]
        },
        {
            'name': 'Dictionaries',
            'description': 'Storing data in key-value pairs',
            'order': 10,
            'notes': [
                {
                    'title': 'Dictionaries',
                    'content': '''<h2>Dictionaries</h2>
<p>Dictionaries are like real dictionaries - you look up a word (key) to find its meaning (value). In Python, you store data in pairs like this.</p>

<h3>Creating a Dictionary</h3>
<pre><code>student = {
    "name": "John",
    "age": 20,
    "grade": "A"
}
</code></pre>

<p>Each item has a key (like "name") and a value (like "John"). The key is how you find the value later.</p>

<h3>Accessing Values</h3>
<pre><code>student = {"name": "John", "age": 20}
print(student["name"])  # John
print(student["age"])   # 20
</code></pre>

<p>You use the key in square brackets to get the value.</p>

<h3>Adding or Changing Values</h3>
<pre><code>student = {"name": "John"}
student["age"] = 20
student["grade"] = "A"
</code></pre>

<p>If the key doesn't exist, it gets added. If it exists, the value gets updated.</p>

<h3>Real Example</h3>
<pre><code>person = {
    "name": "Alice",
    "city": "New York",
    "age": 25
}

print(person["name"], "lives in", person["city"])
</code></pre>

<h3>Common Operations</h3>
<pre><code>student = {"name": "John", "age": 20}

# Check if key exists
if "name" in student:
    print("Name exists")

# Get all keys
print(student.keys())

# Get all values
print(student.values())
</code></pre>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Using the wrong brackets: dictionaries use <code>{}</code>, not <code>[]</code> for creation</li>
<li>Trying to access a key that doesn't exist: <code>student["phone"]</code> will give an error if "phone" key doesn't exist</li>
<li>Forgetting quotes around keys: <code>{name: "John"}</code> (wrong) vs <code>{"name": "John"}</code> (correct)</li>
</ul>

<h3>Practice Task</h3>
<p>Create a dictionary for a book with keys for title, author, and year. Print each piece of information.</p>'''
                }
            ]
        },
        {
            'name': 'Functions',
            'description': 'Creating reusable blocks of code',
            'order': 11,
            'notes': [
                {
                    'title': 'Creating Functions',
                    'content': '''<h2>Creating Functions</h2>
<p>Functions are like recipes. You write the steps once, and then you can use them over and over again. This saves you from writing the same code multiple times.</p>

<h3>Basic Function</h3>
<pre><code>def greet():
    print("Hello!")

greet()  # This calls the function
</code></pre>

<p>The word <code>def</code> means "define". We're defining a function called <code>greet</code>. When we write <code>greet()</code> later, it runs the code inside the function.</p>

<h3>Functions with Parameters</h3>
<p>You can give functions information to work with:</p>

<pre><code>def greet(name):
    print("Hello,", name)

greet("Alice")  # Prints: Hello, Alice
greet("Bob")    # Prints: Hello, Bob
</code></pre>

<p>The <code>name</code> in the function definition is called a parameter. When you call the function, you pass in a value (like "Alice").</p>

<h3>Functions that Return Values</h3>
<pre><code>def add_numbers(a, b):
    result = a + b
    return result

sum = add_numbers(5, 3)
print(sum)  # 8
</code></pre>

<p>The <code>return</code> statement sends a value back. You can use that value later.</p>

<h3>Real Example</h3>
<pre><code>def calculate_total(price, quantity):
    total = price * quantity
    return total

bill = calculate_total(10, 3)
print("Total:", bill)  # Total: 30
</code></pre>

<h3>Why Use Functions?</h3>
<ul>
<li>You write code once, use it many times</li>
<li>Makes your code easier to read</li>
<li>If you need to fix something, you only fix it in one place</li>
</ul>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Forgetting the colon after <code>def</code>: <code>def greet()</code> (wrong) vs <code>def greet():</code> (correct)</li>
<li>Forgetting to call the function: writing <code>def greet():</code> but never writing <code>greet()</code> to actually run it</li>
<li>Wrong indentation inside the function</li>
</ul>

<h3>Practice Task</h3>
<p>Create a function that takes two numbers and returns their product. Then call it with different numbers and print the results.</p>'''
                }
            ]
        },
        {
            'name': 'Basic Error Handling',
            'description': 'Dealing with errors in your code',
            'order': 12,
            'notes': [
                {
                    'title': 'Handling Errors',
                    'content': '''<h2>Handling Errors</h2>
<p>Sometimes things go wrong in your program. Maybe the user typed something unexpected, or you tried to divide by zero. Python will stop and show an error. But you can handle these errors gracefully.</p>

<h3>Try and Except</h3>
<p>The <code>try</code> and <code>except</code> blocks let you catch errors:</p>

<pre><code>try:
    number = int(input("Enter a number: "))
    print("You entered:", number)
except:
    print("That's not a valid number!")
</code></pre>

<p>If the user types something that can't be converted to a number, instead of crashing, the program will print the error message and continue.</p>

<h3>Why This Matters</h3>
<p>Without error handling, if someone types "hello" when you ask for a number, your program crashes. With try/except, you can handle it nicely.</p>

<h3>Real Example</h3>
<pre><code>try:
    age = int(input("How old are you? "))
    print("Next year you'll be", age + 1)
except:
    print("Please enter a valid number")
</code></pre>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Using try/except for everything (you don't always need it)</li>
<li>Not being specific about what error you're catching</li>
<li>Forgetting the colon after <code>try</code> and <code>except</code></li>
</ul>

<h3>Practice Task</h3>
<p>Write a program that asks for two numbers and divides them. Use try/except to handle the case where the user might enter zero or non-numbers.</p>'''
                }
            ]
        },
        {
            'name': 'File Handling',
            'description': 'Reading from and writing to files',
            'order': 13,
            'notes': [
                {
                    'title': 'Working with Files',
                    'content': '''<h2>Working with Files</h2>
<p>So far, all our data disappears when the program ends. What if you want to save information? That's where files come in.</p>

<h3>Writing to a File</h3>
<pre><code>file = open("notes.txt", "w")
file.write("Hello, this is my note")
file.close()
</code></pre>

<p>The <code>"w"</code> means "write mode" - it creates a new file or overwrites an existing one. After writing, always close the file with <code>close()</code>.</p>

<h3>Reading from a File</h3>
<pre><code>file = open("notes.txt", "r")
content = file.read()
print(content)
file.close()
</code></pre>

<p>The <code>"r"</code> means "read mode". The <code>read()</code> method gets all the content from the file.</p>

<h3>Better Way: With Statement</h3>
<p>There's a safer way that automatically closes the file:</p>

<pre><code>with open("notes.txt", "w") as file:
    file.write("Hello World")
</code></pre>

<p>When the code inside the <code>with</code> block finishes, the file automatically closes. This is the recommended way.</p>

<h3>Appending to a File</h3>
<pre><code>with open("notes.txt", "a") as file:
    file.write("\\nNew line")
</code></pre>

<p>The <code>"a"</code> means "append mode" - it adds to the end of the file instead of overwriting it. The <code>\\n</code> creates a new line.</p>

<h3>Common Beginner Mistakes</h3>
<ul>
<li>Forgetting to close the file (use <code>with</code> to avoid this)</li>
<li>Using the wrong mode: <code>"w"</code> overwrites, <code>"a"</code> appends</li>
<li>Not handling errors if the file doesn't exist when reading</li>
</ul>

<h3>Practice Task</h3>
<p>Write a program that asks the user for their name and saves it to a file called "name.txt". Then read it back and print it.</p>'''
                }
            ]
        }
    ]
    
    # Create topics and notes
    inserted_topics = 0
    inserted_notes = 0
    
    for topic_data in topics_data:
        # Check if topic exists
        existing_topic = db.execute(
            'SELECT id FROM topics WHERE subject_id = ? AND name = ?',
            (subject_id, topic_data['name'])
        ).fetchone()
        
        if existing_topic:
            topic_id = existing_topic['id']
        else:
            db.execute(
                '''INSERT INTO topics (subject_id, name, description, order_index, created_at)
                   VALUES (?, ?, ?, ?, ?)''',
                (subject_id, topic_data['name'], topic_data['description'], topic_data['order'], datetime.now())
            )
            db.commit()
            topic_id = db.execute(
                'SELECT id FROM topics WHERE subject_id = ? AND name = ?',
                (subject_id, topic_data['name'])
            ).fetchone()['id']
            inserted_topics += 1
        
        # Add notes for this topic
        for note_data in topic_data['notes']:
            existing_note = db.execute(
                'SELECT id FROM notes WHERE topic_id = ? AND title = ?',
                (topic_id, note_data['title'])
            ).fetchone()
            
            if not existing_note:
                db.execute(
                    '''INSERT INTO notes (topic_id, title, content, visibility, order_index, created_at, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (topic_id, note_data['title'], note_data['content'], 'published', 1, datetime.now(), None)
                )
                inserted_notes += 1
    
    db.commit()
    
    print(f"\n{'='*60}")
    print(f"Learning Notes Seeding Complete!")
    print(f"{'='*60}")
    print(f"Topics created/updated: {inserted_topics}")
    print(f"Notes inserted: {inserted_notes}")
    print(f"{'='*60}\n")
    
    db.close()



def seed_practice_questions():
    """Add practice questions for each topic"""
    init_db()
    db = get_db()
    
    # Get Python subject
    python_subject = db.execute(
        'SELECT id FROM subjects WHERE name = ?', ('Python',)
    ).fetchone()
    
    if not python_subject:
        print("Python subject not found. Please run seed_learning_notes.py first.")
        return
    
    subject_id = python_subject['id']
    
    # Practice questions for each topic
    topic_questions = {
        'Introduction to Python': {
            'easy': [
                'What does the print() function do? Write a simple example.',
                'Write a program that prints your name on the screen.',
                'Write a program that prints three different messages, each on a new line.',
                'What happens if you forget the quotes around text in print()? Try it and see.'
            ],
            'medium': [
                'Write a program that prints a welcome message, then asks the user for their name and prints a personalized greeting.',
                'Create a program that prints your favorite quote. Make sure to use proper quotes in the string.',
                'Write a program that prints a simple pattern using multiple print statements (like a triangle of stars).'
            ],
            'practice': [
                'Create a program that introduces yourself. Print your name, age, and one interesting fact about you.',
                'Write a program that prints a simple menu for a restaurant with at least 5 items, each on a new line.'
            ],
            'hint': 'Remember: text in print() needs quotes around it. Numbers don\'t need quotes.'
        },
        'Variables & Data Types': {
            'easy': [
                'Create a variable called "name" and store your name in it. Then print it.',
                'Create variables for your age (as a number) and your city (as text). Print both.',
                'What\'s the difference between these two: name = "25" and age = 25?',
                'Create a variable for a price (like 19.99) and print it.'
            ],
            'medium': [
                'Create variables for a product name, price, and quantity. Then calculate and print the total cost.',
                'Write a program that swaps the values of two variables. (Hint: you\'ll need a temporary variable)',
                'Create variables for a student\'s name, marks in three subjects, and calculate the average.'
            ],
            'practice': [
                'Create a program that stores information about a book (title, author, year) in variables and prints a formatted description.',
                'Write a program that converts temperature from Celsius to Fahrenheit. Store the Celsius value in a variable, calculate Fahrenheit, and print both.'
            ],
            'hint': 'Don\'t forget quotes around text. Numbers don\'t need quotes, but if you put quotes, they become text and you can\'t do math with them.'
        },
        'Input & Output': {
            'easy': [
                'Write a program that asks for the user\'s name and then greets them.',
                'Create a program that asks for two numbers and prints their sum.',
                'Write a program that asks "What is your favorite color?" and then repeats it back to the user.'
            ],
            'medium': [
                'Write a program that asks for the user\'s age and tells them how old they\'ll be in 10 years.',
                'Create a program that asks for a person\'s first name and last name separately, then prints the full name.',
                'Write a program that asks for the price of an item and the quantity, then calculates and displays the total cost.'
            ],
            'practice': [
                'Create a simple registration form that asks for name, email, and age, then displays all the information in a formatted way.',
                'Write a program that asks for the radius of a circle and calculates the area. (Area = 3.14 * radius * radius)'
            ],
            'hint': 'Remember: input() always gives you text. If you need a number, use int() or float() to convert it.'
        },
        'Operators': {
            'easy': [
                'Write a program that takes two numbers and prints their sum, difference, product, and quotient.',
                'What is the result of 15 % 4? Write a program to check your answer.',
                'Create a program that calculates 5 raised to the power of 3.'
            ],
            'medium': [
                'Write a program that checks if a number is even or odd using the modulus operator.',
                'Create a program that calculates the area of a rectangle (length * width) and the perimeter (2 * length + 2 * width).',
                'Write a program that converts seconds into minutes and remaining seconds. (For example, 125 seconds = 2 minutes and 5 seconds)'
            ],
            'practice': [
                'Create a simple tip calculator. Ask for the bill amount and tip percentage, then calculate and display the tip amount and total bill.',
                'Write a program that calculates the average of three test scores entered by the user.'
            ],
            'hint': 'The % operator gives you the remainder. It\'s useful for checking if a number is even (number % 2 == 0) or odd.'
        },
        'Conditional Statements': {
            'easy': [
                'Write a program that checks if a number is positive, negative, or zero.',
                'Create a program that asks for a person\'s age and tells them if they\'re a minor (under 18) or an adult.',
                'Write a program that checks if a number is greater than 10. Print "Greater" or "Not greater" accordingly.'
            ],
            'medium': [
                'Create a program that asks for a score and assigns a grade: A (90+), B (80-89), C (70-79), D (60-69), F (below 60).',
                'Write a program that checks if a year is a leap year. (Leap year: divisible by 4, but not by 100 unless also divisible by 400)',
                'Create a program that asks for two numbers and prints which one is larger, or if they\'re equal.'
            ],
            'practice': [
                'Write a simple password checker. Ask for a password, and if it\'s "python123", print "Access granted", otherwise print "Access denied".',
                'Create a program that asks for the day of the week and tells the user if it\'s a weekday or weekend.'
            ],
            'hint': 'Remember to use == for comparison, not =. Also, make sure your conditions cover all possible cases.'
        },
        'Loops': {
            'easy': [
                'Write a program that prints numbers from 1 to 10 using a for loop.',
                'Create a program that prints "Hello" 5 times using a loop.',
                'Write a program that prints all even numbers from 2 to 20.'
            ],
            'medium': [
                'Write a program that calculates the sum of numbers from 1 to 100.',
                'Create a program that asks the user for a number and prints its multiplication table (1 to 10).',
                'Write a program that counts down from 10 to 1, then prints "Blast off!"'
            ],
            'practice': [
                'Create a program that asks the user to guess a number. Keep asking until they guess 7. Give hints (too high/too low).',
                'Write a program that prints a pattern: first line has 1 star, second has 2 stars, up to 5 stars. Use nested loops if you can, or just multiple prints.'
            ],
            'hint': 'Be careful with while loops - make sure the condition will eventually become false, or you\'ll get an infinite loop!'
        },
        'Strings': {
            'easy': [
                'Write a program that takes your name and prints it in uppercase, lowercase, and with the first letter capitalized.',
                'Create a program that asks for a word and prints how many characters it has.',
                'Write a program that combines your first name and last name into a full name and prints it.'
            ],
            'medium': [
                'Write a program that checks if a word entered by the user is a palindrome (reads same forwards and backwards).',
                'Create a program that asks for a sentence and counts how many words are in it. (Hint: use split())',
                'Write a program that takes a name and creates an email address by adding "@gmail.com" to it.'
            ],
            'practice': [
                'Create a program that asks for a full name and displays it in "Last Name, First Name" format.',
                'Write a program that takes a sentence and prints each word on a separate line.'
            ],
            'hint': 'Remember: strings are immutable, so methods like upper() return a new string - they don\'t change the original. You need to store the result in a variable.'
        },
        'Lists': {
            'easy': [
                'Create a list of your three favorite fruits and print each one using a loop.',
                'Write a program that creates a list of numbers 1 to 5 and prints the first and last items.',
                'Create a list, add three items to it using append(), then print the list.'
            ],
            'medium': [
                'Write a program that finds the largest number in a list of numbers.',
                'Create a program that asks the user to enter 5 names, stores them in a list, then prints all names.',
                'Write a program that takes a list of numbers and calculates the sum of all numbers in it.'
            ],
            'practice': [
                'Create a simple shopping list program. Allow the user to add items, view the list, and remove items.',
                'Write a program that stores student names and their scores in separate lists, then finds and prints the student with the highest score.'
            ],
            'hint': 'Remember: list positions start at 0, not 1. So the first item is list[0], second is list[1], etc.'
        },
        'Tuples & Sets': {
            'easy': [
                'Create a tuple with your birth date (year, month, day) and print each value.',
                'Create a set of your favorite colors and print it. Try adding a duplicate color and see what happens.',
                'Write a program that checks if a specific color is in your set of favorite colors.'
            ],
            'medium': [
                'Create two sets of numbers and find which numbers are in both sets (intersection).',
                'Write a program that stores coordinates as tuples and calculates the distance between two points. (Use simple formula: distance = sqrt((x2-x1)^2 + (y2-y1)^2))',
                'Create a program that removes duplicates from a list by converting it to a set and back to a list.'
            ],
            'practice': [
                'Create a program that stores student IDs in a set. Allow adding new IDs and checking if an ID exists.',
                'Write a program that uses tuples to store information about 3 books (title, author, year) and displays them in a formatted way.'
            ],
            'hint': 'Tuples can\'t be changed after creation. If you need to modify data, use a list instead.'
        },
        'Dictionaries': {
            'easy': [
                'Create a dictionary for a person with keys: name, age, city. Print each piece of information.',
                'Write a program that stores phone numbers for three people in a dictionary, then looks up and prints a specific person\'s number.',
                'Create a dictionary for a product (name, price, quantity) and print all the details.'
            ],
            'medium': [
                'Write a program that stores student names and their grades in a dictionary, then finds and prints the student with the highest grade.',
                'Create a program that counts how many times each word appears in a sentence. Store the counts in a dictionary.',
                'Write a program that manages a simple inventory: add items, view items, and check if an item exists.'
            ],
            'practice': [
                'Create a simple contact book program. Store contacts as dictionaries with name, phone, and email. Allow adding, viewing, and searching contacts.',
                'Write a program that stores information about 3 movies (title, director, year) in a dictionary and displays them in a nice format.'
            ],
            'hint': 'When accessing dictionary values, make sure the key exists. You can check with "if key in dictionary:" before accessing.'
        },
        'Functions': {
            'easy': [
                'Write a function called greet() that prints "Hello!" Call it three times.',
                'Create a function that takes a name as parameter and prints a greeting with that name.',
                'Write a function that takes two numbers and returns their sum. Test it with different numbers.'
            ],
            'medium': [
                'Create a function that checks if a number is even. It should return True or False.',
                'Write a function that calculates the area of a circle given the radius. (Area = 3.14 * radius * radius)',
                'Create a function that takes a list of numbers and returns the average.'
            ],
            'practice': [
                'Write a program with functions to calculate the area of different shapes: rectangle, circle, and triangle. Ask the user which shape they want.',
                'Create a function that converts temperature from Celsius to Fahrenheit. Write another function that does the reverse. Test both.'
            ],
            'hint': 'Don\'t forget the colon after def and proper indentation. Also, if you want to use the result of a function, make sure it returns a value.'
        },
        'Basic Error Handling': {
            'easy': [
                'Write a program that asks for a number and divides 100 by it. Use try/except to handle division by zero.',
                'Create a program that asks for the user\'s age. Use try/except to handle cases where they don\'t enter a valid number.',
                'Write a program that tries to convert user input to an integer, and prints an error message if it fails.'
            ],
            'medium': [
                'Create a calculator program that uses try/except to handle invalid operations and invalid numbers.',
                'Write a program that asks for a filename and tries to read it. Handle the case where the file doesn\'t exist.',
                'Create a program that divides two numbers with proper error handling for both division by zero and invalid input.'
            ],
            'practice': [
                'Write a robust program that asks for student information (name, age, grade) and handles all possible input errors gracefully.',
                'Create a program that reads numbers from user input until they enter "done", then calculates the average. Handle invalid numbers with try/except.'
            ],
            'hint': 'Use try/except around code that might fail. Be specific about what could go wrong - don\'t just catch everything without thinking.'
        },
        'File Handling': {
            'easy': [
                'Write a program that creates a file called "notes.txt" and writes "Hello, this is my first file!" to it.',
                'Create a program that reads a file and prints its contents. Make sure the file exists first.',
                'Write a program that asks for your name and saves it to a file called "name.txt".'
            ],
            'medium': [
                'Create a program that writes a list of your favorite foods to a file, one per line.',
                'Write a program that reads a file line by line and prints each line with a line number.',
                'Create a program that appends a new note to an existing file without overwriting the old content.'
            ],
            'practice': [
                'Create a simple diary program. Allow the user to write entries that get saved to a file with timestamps.',
                'Write a program that reads student names and grades from a file, calculates the average, and writes the result to a new file.'
            ],
            'hint': 'Always close files after using them, or use the "with" statement which does it automatically. Also, remember "w" overwrites, "a" appends.'
        }
    }
    
    inserted = 0
    
    # Get all topics
    topics = db.execute(
        'SELECT id, name FROM topics WHERE subject_id = ? ORDER BY order_index',
        (subject_id,)
    ).fetchall()
    
    for topic in topics:
        topic_name = topic['name']
        topic_id = topic['id']
        
        if topic_name in topic_questions:
            questions_data = topic_questions[topic_name]
            
            # Build the practice questions content
            content = f'''<h2>Practice Questions - {topic_name}</h2>
<p>Here are some practice questions to help you understand {topic_name.lower()}. Start with the easy ones and work your way up!</p>

<h3>Easy Questions</h3>
<ol>'''
            
            for i, q in enumerate(questions_data['easy'], 1):
                content += f'<li>{q}</li>\n'
            
            content += '</ol>\n\n<h3>Medium Questions</h3>\n<ol>'
            
            for i, q in enumerate(questions_data['medium'], 1):
                content += f'<li>{q}</li>\n'
            
            content += '</ol>\n\n<h3>Practice Tasks</h3>\n<ol>'
            
            for i, q in enumerate(questions_data['practice'], 1):
                content += f'<li>{q}</li>\n'
            
            content += '</ol>'
            
            if 'hint' in questions_data:
                content += f'\n\n<div style="background: #fff3cd; padding: 1rem; border-radius: 6px; border-left: 4px solid #ff9800; margin-top: 1.5rem;">\n<strong>💡 Common Mistake to Avoid:</strong><br>\n{questions_data["hint"]}\n</div>'
            
            # Check if practice questions note already exists
            existing = db.execute(
                'SELECT id FROM notes WHERE topic_id = ? AND title LIKE ?',
                (topic_id, '%Practice Questions%')
            ).fetchone()
            
            if not existing:
                db.execute(
                    '''INSERT INTO notes (topic_id, title, content, visibility, order_index, created_at, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (topic_id, f'Practice Questions - {topic_name}', content, 'published', 999, datetime.now(), None)
                )
                inserted += 1
    
    db.commit()
    
    print(f"\n{'='*60}")
    print(f"Practice Questions Seeding Complete!")
    print(f"{'='*60}")
    print(f"Practice question sets inserted: {inserted}")
    print(f"{'='*60}\n")
    
    db.close()



def seed_projects():
    """Add beginner-friendly projects"""
    init_db()
    db = get_db()
    
    # Get or create Python subject
    python_subject = db.execute(
        'SELECT id FROM subjects WHERE name = ?', ('Python',)
    ).fetchone()
    
    if not python_subject:
        db.execute(
            '''INSERT INTO subjects (name, description, language_track, order_index, created_at)
               VALUES (?, ?, ?, ?, ?)''',
            ('Python', 'Learn Python programming from basics to advanced concepts', 'python', 1, datetime.now())
        )
        db.commit()
        python_subject = db.execute(
            'SELECT id FROM subjects WHERE name = ?', ('Python',)
        ).fetchone()
    
    subject_id = python_subject['id']
    
    # Get or create Projects topic
    projects_topic = db.execute(
        'SELECT id FROM topics WHERE subject_id = ? AND name = ?',
        (subject_id, 'Projects')
    ).fetchone()
    
    if not projects_topic:
        db.execute(
            '''INSERT INTO topics (subject_id, name, description, order_index, created_at)
               VALUES (?, ?, ?, ?, ?)''',
            (subject_id, 'Projects', 'Beginner-friendly projects to practice what you learned', 100, datetime.now())
        )
        db.commit()
        projects_topic = db.execute(
            'SELECT id FROM topics WHERE subject_id = ? AND name = ?',
            (subject_id, 'Projects')
        ).fetchone()
    
    topic_id = projects_topic['id']
    
    projects = [
        {
            'title': 'Number Guessing Game',
            'content': '''<h2>Number Guessing Game</h2>
<p>This is a simple game where the computer picks a number and you try to guess it. Great for practicing loops and conditionals!</p>

<h3>What You'll Learn</h3>
<ul>
<li>Using loops (while)</li>
<li>Conditional statements (if/else)</li>
<li>Getting user input</li>
<li>Generating random numbers</li>
</ul>

<h3>Step-by-Step Build</h3>

<p><strong>Step 1:</strong> Import the random module so we can generate a random number.</p>
<pre><code>import random
</code></pre>

<p><strong>Step 2:</strong> Pick a random number between 1 and 100.</p>
<pre><code>secret_number = random.randint(1, 100)
</code></pre>

<p><strong>Step 3:</strong> Create a loop that keeps asking until the user guesses correctly.</p>
<pre><code>guess = 0
attempts = 0

while guess != secret_number:
    guess = int(input("Guess a number between 1 and 100: "))
    attempts = attempts + 1
    
    if guess < secret_number:
        print("Too low! Try again.")
    elif guess > secret_number:
        print("Too high! Try again.")
    else:
        print("Congratulations! You got it in", attempts, "attempts!")
</code></pre>

<h3>Complete Code</h3>
<pre><code>import random

# Pick a random number
secret_number = random.randint(1, 100)
guess = 0
attempts = 0

print("I'm thinking of a number between 1 and 100. Can you guess it?")

# Keep asking until they get it right
while guess != secret_number:
    guess = int(input("Enter your guess: "))
    attempts = attempts + 1
    
    # Give hints
    if guess < secret_number:
        print("Too low! Try a higher number.")
    elif guess > secret_number:
        print("Too high! Try a lower number.")
    else:
        print("You got it! It took you", attempts, "guesses.")
</code></pre>

<h3>Try These Improvements</h3>
<ul>
<li>Limit the number of guesses (like 7 tries max)</li>
<li>Tell the user if they're getting close (within 5 numbers)</li>
<li>Ask if they want to play again after winning</li>
</ul>'''
        },
        {
            'title': 'Simple Calculator',
            'content': '''<h2>Simple Calculator</h2>
<p>A basic calculator that can add, subtract, multiply, and divide. This project helps you practice functions and user input.</p>

<h3>What You'll Learn</h3>
<ul>
<li>Creating functions</li>
<li>Using operators</li>
<li>Handling user input</li>
<li>Conditional statements</li>
</ul>

<h3>Step-by-Step Build</h3>

<p><strong>Step 1:</strong> Create functions for each operation.</p>
<pre><code>def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b
</code></pre>

<p><strong>Step 2:</strong> Get numbers and operation from the user.</p>
<pre><code>num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))
operation = input("Enter operation (+, -, *, /): ")
</code></pre>

<p><strong>Step 3:</strong> Use if/elif to call the right function.</p>
<pre><code>if operation == "+":
    result = add(num1, num2)
elif operation == "-":
    result = subtract(num1, num2)
elif operation == "*":
    result = multiply(num1, num2)
elif operation == "/":
    result = divide(num1, num2)
else:
    result = "Invalid operation"

print("Result:", result)
</code></pre>

<h3>Complete Code</h3>
<pre><code>def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Cannot divide by zero!"
    return a / b

# Get input from user
print("Simple Calculator")
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))
operation = input("Enter operation (+, -, *, /): ")

# Calculate based on operation
if operation == "+":
    result = add(num1, num2)
elif operation == "-":
    result = subtract(num1, num2)
elif operation == "*":
    result = multiply(num1, num2)
elif operation == "/":
    result = divide(num1, num2)
else:
    result = "Invalid operation"

print("Result:", result)
</code></pre>

<h3>Try These Improvements</h3>
<ul>
<li>Add a loop so the user can do multiple calculations</li>
<li>Handle division by zero (already done in the code above!)</li>
<li>Add more operations like power or square root</li>
</ul>'''
        },
        {
            'title': 'Student Record System',
            'content': '''<h2>Student Record System</h2>
<p>A simple program to store and view student information. This project teaches you about lists and dictionaries.</p>

<h3>What You'll Learn</h3>
<ul>
<li>Working with lists</li>
<li>Using dictionaries</li>
<li>Loops with lists</li>
<li>Adding and displaying data</li>
</ul>

<h3>Step-by-Step Build</h3>

<p><strong>Step 1:</strong> Create an empty list to store student records.</p>
<pre><code>students = []
</code></pre>

<p><strong>Step 2:</strong> Create a function to add a student.</p>
<pre><code>def add_student():
    name = input("Enter student name: ")
    age = int(input("Enter age: "))
    grade = input("Enter grade: ")
    
    student = {
        "name": name,
        "age": age,
        "grade": grade
    }
    
    students.append(student)
    print("Student added successfully!")
</code></pre>

<p><strong>Step 3:</strong> Create a function to display all students.</p>
<pre><code>def display_students():
    if len(students) == 0:
        print("No students in the system.")
    else:
        print("\\nStudent Records:")
        for student in students:
            print("Name:", student["name"])
            print("Age:", student["age"])
            print("Grade:", student["grade"])
            print("---")
</code></pre>

<h3>Complete Code</h3>
<pre><code># List to store all students
students = []

def add_student():
    name = input("Enter student name: ")
    age = int(input("Enter age: "))
    grade = input("Enter grade: ")
    
    # Create a dictionary for this student
    student = {
        "name": name,
        "age": age,
        "grade": grade
    }
    
    # Add to the list
    students.append(student)
    print("Student added!")

def display_students():
    if len(students) == 0:
        print("No students yet.")
    else:
        print("\\nAll Students:")
        for student in students:
            print("Name:", student["name"])
            print("Age:", student["age"])
            print("Grade:", student["grade"])
            print("-" * 20)

# Main program
while True:
    print("\\n1. Add Student")
    print("2. View All Students")
    print("3. Exit")
    
    choice = input("Enter choice: ")
    
    if choice == "1":
        add_student()
    elif choice == "2":
        display_students()
    elif choice == "3":
        print("Goodbye!")
        break
    else:
        print("Invalid choice!")
</code></pre>

<h3>Try These Improvements</h3>
<ul>
<li>Add a function to search for a student by name</li>
<li>Add a function to remove a student</li>
<li>Save the records to a file so they don't disappear when the program ends</li>
</ul>'''
        },
        {
            'title': 'To-Do List',
            'content': '''<h2>To-Do List</h2>
<p>A simple console-based to-do list where you can add tasks and mark them as done. Great for practicing lists and loops!</p>

<h3>What You'll Learn</h3>
<ul>
<li>Working with lists</li>
<li>Adding and removing items</li>
<li>Displaying numbered lists</li>
<li>Using loops effectively</li>
</ul>

<h3>Step-by-Step Build</h3>

<p><strong>Step 1:</strong> Create a list to store tasks.</p>
<pre><code>tasks = []
</code></pre>

<p><strong>Step 2:</strong> Create a function to add tasks.</p>
<pre><code>def add_task():
    task = input("Enter task: ")
    tasks.append(task)
    print("Task added!")
</code></pre>

<p><strong>Step 3:</strong> Create a function to show all tasks.</p>
<pre><code>def show_tasks():
    if len(tasks) == 0:
        print("No tasks yet!")
    else:
        print("\\nYour Tasks:")
        for i in range(len(tasks)):
            print(i + 1, ".", tasks[i])
</code></pre>

<p><strong>Step 4:</strong> Create a function to remove tasks.</p>
<pre><code>def remove_task():
    show_tasks()
    if len(tasks) > 0:
        task_num = int(input("Enter task number to remove: "))
        if 1 <= task_num <= len(tasks):
            removed = tasks.pop(task_num - 1)
            print("Removed:", removed)
        else:
            print("Invalid number!")
</code></pre>

<h3>Complete Code</h3>
<pre><code># List to store tasks
tasks = []

def add_task():
    task = input("Enter new task: ")
    tasks.append(task)
    print("Task added!")

def show_tasks():
    if len(tasks) == 0:
        print("\\nNo tasks in your list.")
    else:
        print("\\nYour To-Do List:")
        for i in range(len(tasks)):
            print(f"{i + 1}. {tasks[i]}")

def remove_task():
    show_tasks()
    if len(tasks) > 0:
        try:
            task_num = int(input("\\nEnter task number to remove: "))
            if 1 <= task_num <= len(tasks):
                removed = tasks.pop(task_num - 1)
                print(f"Removed: {removed}")
            else:
                print("Invalid task number!")
        except:
            print("Please enter a valid number!")

# Main program loop
while True:
    print("\\n=== To-Do List ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Remove Task")
    print("4. Exit")
    
    choice = input("Enter choice: ")
    
    if choice == "1":
        add_task()
    elif choice == "2":
        show_tasks()
    elif choice == "3":
        remove_task()
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid choice!")
</code></pre>

<h3>Try These Improvements</h3>
<ul>
<li>Add a "mark as done" feature instead of removing</li>
<li>Save tasks to a file</li>
<li>Add due dates to tasks</li>
</ul>'''
        },
        {
            'title': 'Quiz App',
            'content': '''<h2>Quiz App</h2>
<p>A simple multiple-choice quiz program. This project combines everything you've learned - lists, dictionaries, loops, and functions!</p>

<h3>What You'll Learn</h3>
<ul>
<li>Storing questions and answers</li>
<li>Using lists and dictionaries together</li>
<li>Keeping score</li>
<li>Displaying results</li>
</ul>

<h3>Step-by-Step Build</h3>

<p><strong>Step 1:</strong> Create a list of questions. Each question is a dictionary.</p>
<pre><code>questions = [
    {
        "question": "What is the capital of France?",
        "options": ["A) London", "B) Berlin", "C) Paris", "D) Madrid"],
        "correct": "C"
    },
    {
        "question": "What is 2 + 2?",
        "options": ["A) 3", "B) 4", "C) 5", "D) 6"],
        "correct": "B"
    }
]
</code></pre>

<p><strong>Step 2:</strong> Create a function to run the quiz.</p>
<pre><code>def run_quiz():
    score = 0
    
    for q in questions:
        print(q["question"])
        for option in q["options"]:
            print(option)
        
        answer = input("Enter your answer (A/B/C/D): ").upper()
        
        if answer == q["correct"]:
            print("Correct!")
            score = score + 1
        else:
            print("Wrong! Correct answer is", q["correct"])
        print()
    
    print("Your score:", score, "out of", len(questions))
</code></pre>

<h3>Complete Code</h3>
<pre><code># List of quiz questions
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["A) London", "B) Berlin", "C) Paris", "D) Madrid"],
        "correct": "C"
    },
    {
        "question": "What is 5 * 3?",
        "options": ["A) 10", "B) 15", "C) 20", "D) 25"],
        "correct": "B"
    },
    {
        "question": "Which is a Python data type?",
        "options": ["A) String", "B) Integer", "C) Float", "D) All of the above"],
        "correct": "D"
    }
]

def run_quiz():
    score = 0
    total = len(questions)
    
    print("Welcome to the Quiz!\\n")
    
    # Go through each question
    for i, q in enumerate(questions, 1):
        print(f"Question {i}: {q['question']}")
        
        # Show all options
        for option in q["options"]:
            print(option)
        
        # Get user's answer
        answer = input("Your answer (A/B/C/D): ").upper()
        
        # Check if correct
        if answer == q["correct"]:
            print("Correct!\\n")
            score = score + 1
        else:
            print(f"Wrong! The correct answer is {q['correct']}\\n")
    
    # Show final score
    print("=" * 30)
    print(f"Quiz Complete!")
    print(f"Your score: {score} out of {total}")
    percentage = (score / total) * 100
    print(f"Percentage: {percentage:.1f}%")
    print("=" * 30)

# Run the quiz
run_quiz()
</code></pre>

<h3>Try These Improvements</h3>
<ul>
<li>Add more questions</li>
<li>Add different difficulty levels</li>
<li>Save high scores to a file</li>
<li>Add a timer for each question</li>
</ul>'''
        }
    ]
    
    # Insert projects
    inserted = 0
    for project in projects:
        existing = db.execute(
            'SELECT id FROM notes WHERE topic_id = ? AND title = ?',
            (topic_id, project['title'])
        ).fetchone()
        
        if not existing:
            db.execute(
                '''INSERT INTO notes (topic_id, title, content, visibility, order_index, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (topic_id, project['title'], project['content'], 'published', inserted + 1, datetime.now(), None)
            )
            inserted += 1
    
    db.commit()
    
    print(f"\n{'='*60}")
    print(f"Projects Seeding Complete!")
    print(f"{'='*60}")
    print(f"Projects inserted: {inserted}")
    print(f"{'='*60}\n")
    
    db.close()



def seed_all():
    """Run all seeding functions and create admin user"""
    print("Starting data seeding...")
    print("=" * 60)
    
    # Run all seed functions
    print("\n[1/9] Seeding demo data...")
    init_demo_data()
    
    print("\n[2/9] Seeding learning materials...")
    init_learning_materials()
    
    print("\n[3/9] Seeding sample questions...")
    init_sample_questions()
    
    print("\n[4/9] Seeding bulk questions...")
    seed_bulk_questions()
    
    print("\n[5/9] Seeding complete questions...")
    seed_complete_questions()
    
    print("\n[6/9] Seeding learning notes...")
    seed_learning_notes()
    
    print("\n[7/9] Seeding practice questions...")
    seed_practice_questions()
    
    print("\n[8/9] Seeding projects...")
    seed_projects()
    
    # Create admin user if it doesn't exist
    print("\n[9/9] Creating admin user...")
    db = get_db()
    try:
        # Check if admin user already exists
        admin_check = db.execute(
            "SELECT id FROM users WHERE username = ? OR role = ?",
            ('admin', 'admin')
        ).fetchone()
        
        if not admin_check:
            # Create admin user with hashed password
            hashed_password = generate_password_hash('admin123')
            cursor = db.execute(
                '''INSERT INTO users (username, email, password, role, language_track, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                ('admin', 'admin@example.com', hashed_password, 'admin', 'python', datetime.now())
            )
            db.commit()
            admin_id = cursor.lastrowid
            
            # Initialize admin stats
            db.execute(
                '''INSERT INTO user_stats (user_id, xp, level, streak, last_activity_date)
                   VALUES (?, 0, 1, 0, ?)''',
                (admin_id, datetime.now().date())
            )
            db.commit()
            
            print("   ✅ Admin user created: username='admin', password='admin123'")
        else:
            print("   ℹ️ Admin user already exists. Skipping creation.")
    except Exception as e:
        print(f"   ⚠️ Error creating admin user: {e}")
        db.rollback()
    
    print("\n" + "=" * 60)
    print("✅ All seeding complete!")
    print("=" * 60)


if __name__ == '__main__':
    seed_all()