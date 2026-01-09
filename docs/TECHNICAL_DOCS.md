# College Data Management System - Technical Documentation

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Data Models](#data-models)
5. [Authentication & Authorization](#authentication--authorization)
6. [Key Features Implementation](#key-features-implementation)
7. [API Reference](#api-reference)
8. [Database Schema](#database-schema)
9. [Testing](#testing)
10. [Performance Considerations](#performance-considerations)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Browser                             │
│  (HTML/CSS/JS + HTMX + Alpine.js + Chart.js)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django Application                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Views     │  │  Templates  │  │   Static    │         │
│  │  (Python)   │  │  (Jinja2)   │  │   Files     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Models    │  │ Middleware  │  │  Decorators │         │
│  │   (ORM)     │  │  (Security) │  │   (RBAC)    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQLite Database                           │
│  (Can be swapped for PostgreSQL in production)              │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Server-Side Rendering** - Django templates with HTMX for interactivity
2. **Progressive Enhancement** - Works without JavaScript, enhanced with it
3. **Role-Based Access Control** - Granular permissions per user role
4. **Modular Architecture** - Separate Django apps for each domain

---

## Technology Stack

### Backend
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Django | 4.2+ |
| Database | SQLite / PostgreSQL | 3.x / 14+ |
| PDF Generation | ReportLab | 4.x |
| Image Processing | Pillow | 10.x |
| Excel Support | openpyxl | 3.x |

### Frontend
| Component | Technology | Version |
|-----------|------------|---------|
| CSS Framework | Tailwind CSS | 4.x |
| Interactivity | HTMX | 1.9+ |
| UI State | Alpine.js | 3.x |
| Charts | Chart.js | 4.x |
| Build Tool | Vite | 5.x |

### Development
| Tool | Purpose |
|------|---------|
| pip | Python package management |
| npm | Frontend package management |
| Vite | CSS/JS build pipeline |

---

## Project Structure

```
college_data_cli/
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
├── tailwind.config.js      # Tailwind CSS config
├── vite.config.js          # Vite build config
│
├── college_data_cli/       # Main Django project
│   ├── settings.py         # Django settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI entry point
│   └── asgi.py            # ASGI entry point
│
├── core/                   # Core app (settings, sessions, levels)
│   ├── models.py          # Department model
│   ├── views.py           # Settings views
│   ├── urls.py            # Settings URLs
│   └── templates/
│
├── students/              # Student management
│   ├── models.py          # Student, Session, Level models
│   ├── views.py           # Student CRUD views
│   └── management/commands/  # CLI commands
│
├── courses/               # Course management
│   ├── models.py          # Course, CourseOffering models
│   ├── views.py           # Course CRUD views
│   └── registration_rules.py  # Enrollment validation
│
├── academics/             # Programs & curriculum
│   ├── models.py          # Program, CurriculumCourse, Prerequisite
│   ├── views.py           # Program management views
│   └── graduation.py      # Graduation eligibility logic
│
├── grading/               # Grades & enrollments
│   ├── models.py          # Enrollment, Grade, GradingSettings
│   ├── views.py           # Grade entry & approval views
│   └── repeat_policy.py   # Repeat course handling
│
├── teachers/              # Teacher management
│   ├── models.py          # Teacher model
│   └── views.py           # Teacher CRUD views
│
├── users/                 # Authentication & authorization
│   ├── models.py          # UserProfile, Role, UserRole, UserSession
│   ├── decorators.py      # RBAC decorators
│   ├── middleware.py      # Security middleware
│   └── permissions.py     # Permission checks
│
├── portal/                # Web portal
│   ├── views.py           # Dashboard views
│   ├── context_processors.py  # Template context
│   └── templates/         # Base templates
│
├── reporting/             # Transcripts & reports
│   ├── models.py          # Transcript model
│   ├── views.py           # Report views
│   ├── transcript_generator.py  # PDF generation
│   └── security_features.py     # QR codes, verification
│
├── analytics/             # Analytics & statistics
│   ├── views.py           # Analytics dashboard views
│   └── management/commands/  # Report generation commands
│
├── configuration/         # System configuration
│   ├── models.py          # CollegeSettings, AcademicPolicySettings
│   └── management/commands/  # Config commands
│
├── audit_log/             # Activity logging
│   └── models.py          # LogEntry model
│
├── static/                # Static files
│   └── css/app.css        # Compiled CSS
│
├── media/                 # User uploads
│   ├── college_logos/
│   ├── college_signatures/
│   └── signatures/
│
├── templates/             # Global templates
│   └── registration/      # Auth templates
│
└── docs/                  # Documentation
    ├── USER_GUIDE.md
    ├── TECHNICAL_DOCS.md
    └── ADMIN_GUIDE.md
```

---

## Data Models

### Core Domain Models

#### Student (`students.Student`)
```python
class Student(models.Model):
    student_id = CharField(max_length=20, unique=True)
    first_name = CharField(max_length=100)
    last_name = CharField(max_length=100)
    other_names = CharField(max_length=100, blank=True)
    email = EmailField(unique=True, blank=True, null=True)
    phone = CharField(max_length=20, blank=True)
    date_of_birth = DateField(blank=True, null=True)
    gender = CharField(max_length=1, choices=[('M','Male'),('F','Female')])
    address = TextField(blank=True)
    photo = ImageField(upload_to='students/photos/', blank=True)
    current_level = ForeignKey('Level', on_delete=SET_NULL, null=True)
    entry_session = ForeignKey('Session', on_delete=SET_NULL, null=True)
    program = ForeignKey('academics.Program', on_delete=SET_NULL, null=True)
    is_active = BooleanField(default=True)
    # ... computed fields: cumulative_gpa, total_units_earned
```

#### Session (`students.Session`)
```python
class Session(models.Model):
    name = CharField(max_length=100, unique=True)  # e.g., "2024/2025"
    is_active = BooleanField(default=False)  # Only one active at a time
```

#### Level (`students.Level`)
```python
class Level(models.Model):
    name = CharField(max_length=50, unique=True)  # e.g., "100", "200"
    order = IntegerField(default=0)  # For sorting
```

#### Course (`courses.Course`)
```python
class Course(models.Model):
    code = CharField(max_length=20, unique=True)
    title = CharField(max_length=200)
    units = PositiveIntegerField(default=0)
    default_semester = CharField(choices=SEMESTER_CHOICES, blank=True)
    department = ForeignKey('core.Department', on_delete=SET_NULL, null=True)
    levels = ManyToManyField('students.Level')
    sessions = ManyToManyField('students.Session')
```

#### CourseOffering (`courses.CourseOffering`)
```python
class CourseOffering(models.Model):
    course = ForeignKey(Course, on_delete=CASCADE)
    session = ForeignKey(Session, on_delete=CASCADE)
    semester = CharField(choices=SEMESTER_CHOICES)
    level = ForeignKey(Level, on_delete=SET_NULL, null=True)
    teacher = ForeignKey('teachers.Teacher', on_delete=SET_NULL, null=True)
    capacity = PositiveIntegerField(null=True)  # None = unlimited
    is_active = BooleanField(default=True)
    
    # Properties
    @property
    def enrollment_count(self): ...
    @property
    def available_seats(self): ...
    @property
    def is_full(self): ...
```

#### Program (`academics.Program`)
```python
class Program(models.Model):
    code = CharField(max_length=32, unique=True)
    name = CharField(max_length=255)
    department = ForeignKey('core.Department', on_delete=SET_NULL, null=True)
    min_units_to_graduate = PositiveIntegerField(default=0)
    classification_scheme = CharField(choices=[('BSC','University'),('ND','Polytechnic')])
```

#### Enrollment (`grading.Enrollment`)
```python
class Enrollment(models.Model):
    student = ForeignKey(Student, on_delete=CASCADE)
    course_offering = ForeignKey(CourseOffering, on_delete=CASCADE)
    enrollment_date = DateField(default=timezone.now)
    
    class Meta:
        unique_together = ('student', 'course_offering')
```

#### Grade (`grading.Grade`)
```python
class Grade(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    enrollment = OneToOneField(Enrollment, on_delete=CASCADE)
    ca_score = FloatField(default=0)
    exam_score = FloatField(default=0)
    total_score = FloatField(default=0)  # Auto-calculated
    grade = CharField(max_length=2)       # Auto-calculated
    status = CharField(choices=STATUS_CHOICES, default='DRAFT')
    submitted_at = DateTimeField(null=True)
    approved_at = DateTimeField(null=True)
    approved_by = ForeignKey(User, null=True)
    rejection_reason = TextField(null=True)
```

### Relationship Diagram

```
Session ──────┬──────── CourseOffering ──────── Course
              │              │                    │
              │              │                    │
Level ────────┤              │              Department
              │              │                    │
              │              ▼                    │
Student ──────┴──────── Enrollment ──────── Program
                             │
                             ▼
                          Grade
```

---

## Authentication & Authorization

### Role-Based Access Control (RBAC)

#### Role Model
```python
class Role(models.Model):
    name = CharField(max_length=50, unique=True)  # Admin, DataEntry, Teacher
    description = TextField(blank=True)

class UserRole(models.Model):
    user = ForeignKey(User, on_delete=CASCADE)
    role = ForeignKey(Role, on_delete=CASCADE)
    assigned_at = DateTimeField(auto_now_add=True)
    assigned_by = ForeignKey(User, null=True)
```

#### Decorators (`users/decorators.py`)
```python
# Check if user has a role
def has_role(user, role_name: str) -> bool: ...

# View decorators
@admin_required
def admin_only_view(request): ...

@admin_or_data_entry_required
def data_view(request): ...

@teacher_required
def teacher_view(request): ...

@role_required('Admin', 'DataEntry')
def custom_view(request): ...
```

#### Permission Matrix

| Feature | Admin | DataEntry | Teacher |
|---------|-------|-----------|---------|
| View Dashboard | ✅ | ✅ | ✅ |
| Manage Students | ✅ | ✅ | ❌ (view only) |
| Manage Courses | ✅ | ✅ | ❌ |
| Manage Programs | ✅ | ❌ | ❌ |
| Create Enrollments | ✅ | ✅ | ❌ |
| Enter Grades | ✅ | ❌ | ✅ (assigned only) |
| Approve Grades | ✅ | ❌ | ❌ |
| Generate Transcripts | ✅ | ✅ | ❌ |
| View Analytics | ✅ | ✅ | ✅ |
| System Settings | ✅ | ❌ | ❌ |
| User Management | ✅ | ❌ | ❌ |

### Security Middleware

#### Session Security (`users/middleware.py`)
```python
class SessionSecurityMiddleware:
    # Session timeout (configurable via SESSION_TIMEOUT_MINUTES)
    # Concurrent session limiting (MAX_CONCURRENT_SESSIONS)
    # Session tracking (IP, user agent)
```

#### Data Privacy
```python
class DataPrivacyMiddleware:
    # Security headers (X-Content-Type-Options, X-Frame-Options)
    # Cache control for sensitive pages
```

---

## Key Features Implementation

### Enrollment Rules Engine

Location: `courses/registration_rules.py`

```python
def can_enroll(student, offering, strict_prereqs=False) -> RegistrationResult:
    """
    Validates enrollment eligibility:
    1. Is offering active?
    2. Is student already enrolled?
    3. Level match (warning only)
    4. Capacity check
    5. Repeat limit check
    6. Prerequisites check
    
    Returns: RegistrationResult(ok=bool, error=str, warnings=list)
    """
```

### Grade Calculation

Location: `grading/models.py` - `Grade.save()`

```python
def save(self, *args, **kwargs):
    # Auto-calculate total score
    self.total_score = (self.ca_score or 0) + (self.exam_score or 0)
    
    # Auto-assign letter grade based on GradingSettings
    settings = GradingSettings.objects.filter(
        min_score__lte=self.total_score,
        max_score__gte=self.total_score
    ).first()
    if settings:
        self.grade = settings.grade_name
    
    super().save(*args, **kwargs)
```

### Transcript Generation

Location: `reporting/transcript_generator.py`

```python
class TranscriptGenerator:
    def generate(self, student, layout='standard') -> bytes:
        """
        Generates PDF transcript with:
        - College header (logo, name, address)
        - Student information
        - Session-by-session grade tables
        - GPA calculations
        - QR code for verification
        - Registrar signature
        """
```

### Graduation Eligibility

Location: `academics/graduation.py`

```python
def check_graduation_eligibility(student) -> dict:
    """
    Checks:
    - Total units earned >= program minimum
    - All required courses passed
    - Cumulative GPA >= minimum
    - No outstanding obligations
    
    Returns: {eligible: bool, reasons: list, missing_courses: list}
    """
```

---

## API Reference

### URL Patterns

#### Students (`/students/`)
| URL | View | Method | Description |
|-----|------|--------|-------------|
| `/` | `student_list` | GET | List all students |
| `/create/` | `student_create` | GET/POST | Create student |
| `/<id>/` | `student_detail` | GET | Student details |
| `/<id>/edit/` | `student_edit` | GET/POST | Edit student |
| `/<id>/delete/` | `student_delete` | POST | Delete student |
| `/import/` | `student_import` | GET/POST | Bulk import |
| `/promote/` | `student_promote` | GET/POST | Bulk promotion |

#### Courses (`/courses/`)
| URL | View | Method | Description |
|-----|------|--------|-------------|
| `/` | `course_list` | GET | List courses |
| `/create/` | `course_create` | GET/POST | Create course |
| `/<id>/` | `course_detail` | GET | Course details |
| `/<id>/edit/` | `course_edit` | GET/POST | Edit course |
| `/<id>/offerings/create/` | `offering_create` | GET/POST | Create offering |
| `/offerings/<id>/edit/` | `offering_edit` | GET/POST | Edit offering |

#### Programs (`/programs/`)
| URL | View | Method | Description |
|-----|------|--------|-------------|
| `/` | `program_list` | GET | List programs |
| `/create/` | `program_create` | GET/POST | Create program |
| `/<id>/` | `program_detail` | GET | Program details |
| `/<id>/curriculum/` | `curriculum_manage` | GET/POST | Manage curriculum |
| `/<id>/prerequisites/` | `prerequisites_manage` | GET/POST | Manage prereqs |

#### Grading (`/grading/`)
| URL | View | Method | Description |
|-----|------|--------|-------------|
| `/enrollments/` | `enrollment_list` | GET | List enrollments |
| `/enrollments/create/` | `enrollment_create` | GET/POST | Create enrollment |
| `/enrollments/bulk/` | `enrollment_bulk` | GET/POST | Bulk enrollment |
| `/teacher/courses/` | `teacher_courses` | GET | Teacher's offerings |
| `/entry/<offering_id>/` | `grade_entry` | GET/POST | Enter grades |
| `/approval/` | `approval_queue` | GET | Approval queue |
| `/history/` | `grade_history` | GET | Grade history |

#### Settings (`/settings/`)
| URL | View | Method | Description |
|-----|------|--------|-------------|
| `/sessions/` | `session_list` | GET | List sessions |
| `/levels/` | `level_list` | GET | List levels |
| `/departments/` | `department_list` | GET | List departments |
| `/college/` | `college_settings` | GET/POST | College info |
| `/academic-policy/` | `academic_policy_settings` | GET/POST | Academic policy |
| `/grading/` | `grading_settings` | GET | Grading scale |
| `/users/` | `user_list` | GET | User management |
| `/audit-log/` | `audit_log` | GET | Activity log |

---

## Database Schema

### Indexes

The following indexes are defined for query performance:

#### CourseOffering
- `(session, semester)` - Session/semester lookups
- `(course, session)` - Course history
- `(teacher)` - Teacher's courses
- `(is_active)` - Active offerings filter

#### Enrollment
- `(student)` - Student's enrollments
- `(course_offering)` - Offering's students
- `(enrollment_date)` - Date range queries
- `(student, course_offering)` - Duplicate check

#### Grade
- `(status)` - Approval workflow
- `(grade)` - Grade distribution
- `(total_score)` - Score analytics
- `(submitted_at)` - Submission tracking
- `(approved_at)` - Approval tracking

#### Student
- `(student_id)` - Unique lookup
- `(current_level)` - Level filtering
- `(program)` - Program filtering
- `(last_name, first_name)` - Name sorting

---

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test students
python manage.py test grading

# Run with coverage
coverage run manage.py test
coverage report
```

### Test Files

| File | Coverage |
|------|----------|
| `students/tests.py` | Student CRUD, import |
| `students/test_registration_rules.py` | Enrollment validation |
| `students/test_repeat_policy.py` | Repeat course handling |
| `grading/tests.py` | Grade calculation |
| `grading/test_approval_workflow.py` | Grade workflow |
| `academics/tests.py` | Program, curriculum |
| `reporting/tests.py` | Transcript generation |
| `reporting/test_rbac_and_tamper.py` | Security tests |
| `analytics/test_cohort_audit.py` | Analytics queries |

---

## Performance Considerations

### Database Optimization

1. **Use `select_related()`** for ForeignKey fields
```python
# Bad
students = Student.objects.all()
for s in students:
    print(s.current_level.name)  # N+1 queries!

# Good
students = Student.objects.select_related('current_level', 'program')
```

2. **Use `prefetch_related()`** for ManyToMany
```python
courses = Course.objects.prefetch_related('levels', 'sessions')
```

3. **Indexed queries** - All common filter fields are indexed

### Caching Recommendations

For production, consider:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Cache expensive queries
from django.core.cache import cache

def get_dashboard_stats():
    key = 'dashboard_stats'
    stats = cache.get(key)
    if not stats:
        stats = compute_stats()
        cache.set(key, stats, 300)  # 5 minutes
    return stats
```

### Session Settings

```python
# settings.py
SESSION_TIMEOUT_MINUTES = 60
MAX_CONCURRENT_SESSIONS = 3
TRACK_USER_SESSIONS = True
```

---

## Extending the System

### Adding a New Model

1. Create model in appropriate app's `models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Create views in `views.py`
5. Add URL patterns in `urls.py`
6. Create templates in `templates/`
7. Update navigation if needed

### Adding a New Role

1. Add to `Role.ROLE_CHOICES` in `users/models.py`
2. Run `python manage.py setup_roles`
3. Update `has_role()` in `users/decorators.py` if special logic needed
4. Update permission matrix in documentation

### Creating CLI Commands

```python
# myapp/management/commands/my_command.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Description of command'

    def add_arguments(self, parser):
        parser.add_argument('--option', type=str, help='Option description')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Done!'))
```

---

*Last Updated: January 2026*
