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

## 📋 CLI Usage Examples

### Student Management
```bash
# Add a new student
python manage.py add_student --student-id "STU001" --first-name "John" --last-name "Doe" --email "john@example.com"

# Bulk enroll students
python manage.py bulk_enroll_students --csv-file students.csv --course-code "CS101"

# Generate student analytics
python manage.py student_analytics --level "300"
```

### Course Operations
```bash
# Create a new course
python manage.py add_course --code "CS201" --name "Data Structures" --units 3

# Add prerequisite relationship
python manage.py add_prerequisite --course "CS201" --prerequisite "CS101"

# Manage curriculum
python manage.py add_curriculum_course --program "CS" --course "CS201" --level "200"
```

### Grading Workflow
```bash
# Record scores
python manage.py record_scores --course-offering "CS201-FALL2024" --csv scores.csv

# Calculate final grades
python manage.py calculate_grades --course-offering "CS201-FALL2024"

# Approve grades (requires faculty role)
python manage.py approve_grades --course-offering "CS201-FALL2024"
```

### Reporting & Analytics
```bash
# Generate cohort graduation audit
python manage.py cohort_graduation_audit --cohort-year 2020

# Export grades to Excel
python manage.py export_grades_excel --course-offering "CS201-FALL2024"

# Generate student statistics
python manage.py generate_student_stats --start-date "2024-01-01"
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