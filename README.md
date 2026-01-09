# 🏫 College Data Management System

A comprehensive college administration platform built with Django and React, featuring both web interface and powerful CLI tools for managing student records, courses, enrollments, grading, and academic analytics.

## 🚀 Key Features

### 📊 Core Modules
- **Student Management**: Complete student lifecycle from admission to graduation
- **Course Administration**: Course creation, curriculum management, and offerings
- **Enrollment System**: Student-course enrollment with prerequisites checking
- **Grading & Assessment**: Grade recording, calculation, and approval workflows
- **Academic Programs**: Program management with curriculum mapping
- **Teacher Management**: Faculty profiles and course assignments
- **Analytics & Reporting**: Cohort analysis, graduation audits, and performance metrics

### 💻 Interface Options
- **Web Portal**: Modern React frontend with TailwindCSS styling
- **CLI Tools**: Powerful command-line interface for bulk operations
- **API Layer**: RESTful endpoints for integration

### 🔧 Technical Highlights
- **Role-Based Access Control**: Granular permissions system
- **Audit Logging**: Complete activity tracking and history
- **Data Validation**: Comprehensive business rule enforcement
- **Batch Processing**: Bulk import/export capabilities
- **Security Features**: Secure transcript generation and verification

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**
- **Django 4.x** - Web framework
- **SQLite** - Database (easily switchable to PostgreSQL)
- **Django REST Framework** - API development

### Frontend
- **React 18** - Component-based UI
- **Vite** - Build tool and development server
- **TailwindCSS** - Utility-first CSS framework
- **Chart.js** - Data visualization

### CLI & Dev Tools
- **Custom Django Management Commands**
- **Click** - CLI framework
- **Pandas** - Data processing

## 📁 Project Structure

```
college_data_cli/
├── academics/          # Academic programs and curriculum
├── analytics/          # Reporting and analytics
├── audit_log/          # Activity logging
├── college_data_cli/   # Main Django settings
├── configuration/      # System configuration
├── core/              # Shared models and utilities
├── courses/           # Course management
├── grading/           # Grading system
├── portal/            # Web portal frontend
├── reporting/         # Transcript generation
├── students/          # Student management
├── teachers/          # Faculty management
├── ui/                # Frontend components
└── users/             # Authentication and RBAC
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Ahmadbaba46/college-data.git
cd college-data
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Initialize database**
```bash
python manage.py migrate
python manage.py createsuperuser
```

4. **Install frontend dependencies**
```bash
npm install
```

5. **Start development servers**
```bash
# Terminal 1: Django backend
python manage.py runserver

# Terminal 2: React frontend
npm run dev
```

6. **Access the application**
- Web Portal: http://localhost:5173
- Django Admin: http://localhost:8000/admin
- API Browser: http://localhost:8000/api/

## 📋 Comprehensive CLI Usage Examples

### 👨‍🎓 Student Management
```bash
# Basic student operations
python manage.py add_student \
    --student-id "STU001" \
    --first-name "Ahmad" \
    --last-name "Baba" \
    --email "ahmad.baba@example.edu" \
    --phone "+1234567890" \
    --level "100" \
    --program "CS" \
    --session "2024/2025"

# Update existing student
python manage.py update_student STU001 \
    --email "ahmad.newemail@example.edu" \
    --phone "+0987654321"

# Bulk import from CSV
python manage.py import_students_csv --file-path "new_students.csv"

# Search students
python manage.py search_students --query "Ahmad" --level "200"

# Promote students to next level
python manage.py promote_students --from-level "100" --to-level "200"

# Validate student data integrity
python manage.py validate_student_data --full-report
```

### 📚 Course & Curriculum Management
```bash
# Course creation and management
python manage.py add_course \
    --code "CS301" \
    --name "Algorithms and Complexity" \
    --units 3 \
    --department "Computer Science"

# Curriculum mapping
python manage.py add_curriculum_course \
    --program "CS" \
    --course "CS301" \
    --level "300" \
    --semester "FALL"

# Prerequisites setup
python manage.py add_prerequisite \
    --course "CS301" \
    --prerequisite "CS201"

# Course offering creation
python manage.py create_course_offering \
    --course "CS301" \
    --session "2024/2025" \
    --semester "FALL" \
    --capacity 50

# Course search and listing
python manage.py search_courses --query "algorithms" --department "CS"
```

### 👩‍🏫 Teacher & Faculty Management
```bash
# Add new teacher
python manage.py add_teacher \
    --staff-id "TCH001" \
    --first-name "Dr. Sarah" \
    --last-name "Johnson" \
    --email "s.johnson@college.edu" \
    --department "Computer Science"

# Assign teacher to course
python manage.py assign_teacher \
    --teacher "TCH001" \
    --course-offering "CS301-FALL2024"

# Bulk teacher assignment
python manage.py bulk_assign_teachers --assignments-file "teacher_assignments.csv"

# Teacher workload report
python manage.py generate_teacher_stats --semester "FALL2024"
```

### 📊 Enrollment Operations
```bash
# Individual enrollment
python manage.py enroll_student \
    --student "STU001" \
    --course-offering "CS301-FALL2024"

# Bulk enrollment from file
python manage.py bulk_enroll_students \
    --csv-file "enrollments.csv" \
    --course-offering "CS301-FALL2024"

# List all enrollments
python manage.py list_enrollments --course-offering "CS301-FALL2024"

# Enrollment validation
python manage.py validate_enrollments --session "2024/2025"
```

### 📝 Grading & Assessment
```bash
# Score recording
python manage.py record_scores \
    --course-offering "CS301-FALL2024" \
    --scores-file "student_scores.csv"

# Grade calculation with custom rules
python manage.py calculate_grades \
    --course-offering "CS301-FALL2024" \
    --grading-scheme "standard"

# Grade submission workflow
python manage.py submit_grades --course-offering "CS301-FALL2024"

# Faculty grade approval
python manage.py approve_grades \
    --course-offering "CS301-FALL2024" \
    --approver "DEPT_HEAD_001"

# Grade rejection with feedback
python manage.py reject_grades \
    --course-offering "CS301-FALL2024" \
    --reason "Calculation error found"

# Export grades in multiple formats
python manage.py export_grades_excel --course-offering "CS301-FALL2024"
python manage.py export_grades_csv --course-offering "CS301-FALL2024" --include-comments
```

### 📈 Analytics & Reporting
```bash
# Student performance analytics
python manage.py student_analytics \
    --level "300" \
    --program "CS" \
    --semester "FALL2024"

# Cohort graduation audit
python manage.py cohort_graduation_audit \
    --cohort-year 2020 \
    --program "CS" \
    --detailed-report

# Repeated courses analysis
python manage.py repeated_courses_report \
    --session "2024/2025" \
    --threshold 2

# Enrollment statistics
python manage.py generate_enrollment_stats \
    --start-date "2024-09-01" \
    --end-date "2024-12-31"

# Grade distribution analysis
python manage.py generate_student_stats \
    --metric "gpa" \
    --min-value 2.0 \
    --group-by "program"
```

### 📄 Transcript Generation
```bash
# Individual transcript
python manage.py generate_transcript \
    --student "STU001" \
    --session "2024/2025"

# Secure tamper-proof transcript
python manage.py generate_secure_transcript \
    --student "STU001" \
    --verification-code "ABC123XYZ"

# Batch transcript generation
python manage.py batch_generate_transcripts \
    --student-list "graduating_students.csv" \
    --output-dir "./transcripts/"

# Transcript verification
python manage.py verify_transcript \
    --transcript-file "STU001_transcript.pdf" \
    --verification-code "ABC123XYZ"
```

### ⚙️ System Administration
```bash
# User and role management
python manage.py create_user \
    --username "registrar" \
    --email "registrar@college.edu" \
    --role "registrar"

python manage.py assign_role \
    --user "registrar" \
    --role "registrar" \
    --department "Administration"

python manage.py setup_roles --initialize-default-roles

# System configuration
python manage.py update_college_settings \
    --setting "max_credits_per_semester" \
    --value 18

python manage.py show_settings --category "academic"

# Academic policy updates
python manage.py update_academic_policy \
    --policy "grade_scale" \
    --effective-date "2025-01-01"

# Audit logging
python manage.py log_action \
    --user "admin" \
    --action "bulk_student_import" \
    --details "Imported 150 new students from CSV"
```

### 🌱 Data Seeding & Testing
```bash
# Seed sample data for testing
python manage.py seed_data \
    --students 100 \
    --courses 20 \
    --teachers 15

# Seed grading configurations
python manage.py seed_grading_settings \
    --scheme "standard" \
    --grade-points "A+=4.0,A=4.0,B+=3.3,B=3.0,C+=2.3,C=2.0,D=1.0,F=0.0"

# Populate academic sessions
python manage.py populate_sessions \
    --start-year 2020 \
    --end-year 2025

# Data integrity checks
python manage.py check_null_sessions --repair-missing
```

## 🔐 Roles & Permissions

The system implements Role-Based Access Control (RBAC):

- **Super Admin**: Full system access
- **Registrar**: Student and enrollment management
- **Faculty**: Course teaching and grade submission
- **Department Head**: Department-level oversight
- **Student**: Personal record viewing

## 📈 Analytics Capabilities

- Student progression tracking
- Graduation eligibility analysis
- Course performance metrics
- Faculty workload distribution
- Enrollment trends and patterns
- Repeated courses identification

## 🛡️ Security Features

- Secure transcript generation with tamper detection
- Audit trail for all critical operations
- Role-based access control
- Data validation and sanitization
- Secure file handling

## 📚 Documentation

- [COMMANDS.md](COMMANDS.md) - Complete CLI reference
- [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) - Frontend design guidelines
- [WEBAPP_IMPLEMENTATION_PLAN.md](WEBAPP_IMPLEMENTATION_PLAN.md) - Web application roadmap
- [FEATURE_SUGGESTIONS.md](FEATURE_SUGGESTIONS.md) - Planned enhancements

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Django and React ecosystems
- Inspired by real-world college administration needs
- Designed for scalability and maintainability

---

<p align="center">
  <strong>🏛️ Empowering Educational Institutions Through Technology 🏛️</strong>
</p>