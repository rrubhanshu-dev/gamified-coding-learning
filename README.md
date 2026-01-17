# Gamified Coding Learning Web Application

A full-stack web application built with Flask for teaching coding through gamification. This is a **Final Year Major Project** that demonstrates full-stack development with Python Flask, database design, user authentication, and gamification systems.

## 🎯 Project Overview

This platform provides:
- Full-stack web development with Python Flask
- Database design and management (SQLite)
- User authentication and session management
- Gamification engine (XP, levels, badges, streaks)
- Academy-ready platform with courses and enrollment
- Test/Exam system with time limits and scoring
- Learning content management (Subjects → Topics → Notes)
- Super Admin role management
- XP farming prevention
- Admin panel for content management
- Data visualization with Chart.js
- Responsive web design

## 🛠️ Tech Stack

- **Backend:** Python 3.x, Flask 3.0.0
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Database:** SQLite
- **Charts:** Chart.js 4.4.0
- **Security:** Werkzeug password hashing, session-based authentication

## 📁 Project Structure

```
gamified-coding-learning/
├── app.py                 # Main Flask application (routes)
├── database.py            # Database connection and initialization
├── logic.py               # Business logic (XP, levels, badges, stats)
├── seed_data.py           # Data seeding functions
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── practice.html
│   ├── learn/             # Learning area templates
│   ├── tests/             # Test system templates
│   ├── courses/           # Course templates
│   └── admin/             # Admin panel templates
└── static/                # CSS, JS, images
    ├── css/style.css
    └── js/main.js
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 3: Load Demo Data (Recommended)

To populate the database with sample content:

```bash
python seed_data.py
```

Or run individual seeding functions:
```bash
python -c "from seed_data import init_demo_data, seed_learning_notes, seed_projects, seed_practice_questions, seed_bulk_questions, seed_complete_questions; init_demo_data(); seed_learning_notes(); seed_projects(); seed_practice_questions(); seed_bulk_questions(); seed_complete_questions()"
```

This creates:
- Demo subjects, topics, and learning notes
- Sample questions (120+ questions across all topics)
- Beginner-friendly projects
- Practice questions for each topic
- Demo courses and tests

### Step 4: Access the Application

**Default Admin Account:**
- Username: `admin`
- Password: `admin123`

**Student Registration:**
- Go to `http://localhost:5000/register`
- Create a new student account

## 📊 Database Schema

### Main Tables

- **users** - User accounts (students, admins, super admins)
- **questions** - Coding questions with MCQ options
- **user_stats** - XP, level, streak tracking
- **attempts** - Question attempts history
- **badges** - Available badges
- **user_badges** - User badge achievements
- **subjects** - Learning subjects
- **topics** - Topics within subjects
- **notes** - Learning notes for topics
- **tests** - Test/exam definitions
- **test_attempts** - Student test attempts
- **courses** - Course definitions
- **course_enrollments** - Student course enrollments

The database is automatically initialized when you run `app.py` for the first time.

## 🎮 Features

### Student Features

- User registration and login
- Choose programming language track (Python, JavaScript, Java)
- Browse learning materials (Subjects → Topics → Notes)
- Read learning notes before practicing
- Practice coding questions (MCQ format)
- XP farming prevention (can't repeat same question for XP)
- Earn XP based on correctness and difficulty
- Level up system (exponential XP requirements)
- Daily streak tracking
- Badge achievements
- Take tests/exams (one attempt only)
- View test results with detailed feedback
- View enrolled courses
- Dashboard with XP progress, accuracy, charts, and badges
- Leaderboard ranking

### Admin Features

- Secure admin login
- Admin dashboard with statistics
- Manage Subjects, Topics, and Notes
- Create and publish learning notes (HTML supported)
- Manage questions (Add, Edit, Delete, Enable/Disable)
- Filter questions by topic/difficulty/subject
- Create tests/exams with time limits
- Assign tests to students
- View test results and analytics
- Create courses and enroll students
- View user analytics
- Topic performance analysis

### Super Admin Features

- Promote students to admin
- Demote admins to students
- Create super admins
- Full role management system

### Gamification Engine

**XP Calculation:**
- Correct: `base_points × difficulty_multiplier`
- Incorrect: `base_points × 0.1` (participation points)
- Difficulty multipliers: Easy (1.0x), Medium (1.5x), Hard (2.0x)

**Level System:**
- Formula: `level = floor(sqrt(XP / 100)) + 1`
- Exponential progression

**Streak System:**
- Increments on consecutive daily attempts
- Resets if a day is missed

**Badge System:**
- Auto-unlocked based on achievements
- Types: First Steps, Level badges, Streak badges, XP badges

## 📝 Learning Content

The platform includes comprehensive learning materials:

- **13 Python Topics:** Introduction, Variables, Input/Output, Operators, Conditionals, Loops, Strings, Lists, Tuples & Sets, Dictionaries, Functions, Error Handling, File Handling
- **Learning Notes:** Beginner-friendly explanations with code examples
- **Practice Questions:** Easy, Medium, and Hard questions for each topic
- **Beginner Projects:** 5 student-level projects with step-by-step guides

## 🔒 Security Features

- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection (Flask sessions)
- Role-based access control (Admin/Student/Super Admin)
- SQL injection prevention (parameterized queries)

## 🐛 Troubleshooting

### Database Issues

If you encounter database errors:
```bash
# Delete the database file and restart
rm gamified_coding.db  # or delete manually
python app.py  # Database will be recreated
```

### Port Already in Use

If port 5000 is busy, edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### Module Not Found

Ensure you've activated the virtual environment and installed dependencies:
```bash
pip install -r requirements.txt
```

## 📈 Future Enhancements

- Upgrade to MySQL/PostgreSQL
- Add more programming languages
- Implement code execution for practice
- Add social features (forums, discussions)
- Email notifications
- Mobile app version
- Advanced analytics and reporting
- Video lessons support
- Assignment submission system

## 👨‍💻 Development Notes

### Code Organization

- **app.py:** Main Flask routes and application logic
- **database.py:** Database connection and initialization
- **logic.py:** Core business logic (XP, levels, badges, stats, question completion)
- **seed_data.py:** All data seeding functions

### Comments

All major functions include docstrings explaining their purpose. This aids in code understanding during viva and future maintenance.

## 📄 License

This project is created for educational purposes as a Final Year Major Project.

## 👤 Author

**Your Name**  
Final Year Project - [Your Institution]

---

**Built with ❤️ using Flask and Python**
# gamified-coding-learning
A student-built gamified coding learning web application using Python and Flask. Designed for beginners to learn Python concepts through notes, practice questions, tests, and mini projects.
