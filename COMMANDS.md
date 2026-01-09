# College Data Management System - CLI Commands Reference

This document provides a complete reference for all available management commands.

## Table of Contents

1. [Student Management](#student-management)
2. [Course Management](#course-management)
3. [Program & Curriculum](#program--curriculum)
4. [Teacher Management](#teacher-management)
5. [Enrollment & Grading](#enrollment--grading)
6. [Transcripts & Reports](#transcripts--reports)
7. [Analytics](#analytics)
8. [Configuration](#configuration)
9. [User Management](#user-management)
10. [System Utilities](#system-utilities)

---

## Student Management

### `add_student`
Create a new student record.

```bash
python manage.py add_student \
    --student-id "STU001" \
    --first-name "John" \
    --last-name "Doe" \
    --email "john@example.com" \
    --level "100" \
    --session "2024/2025"
```

**Options:**
- `--student-id` (required): Unique student identifier
- `--first-name` (required): Student's first name
- `--last-name` (required): Student's last name
- `--email`: Email address
- `--phone`: Phone number
- `--level`: Current level (e.g., "100", "200")
- `--session`: Entry session
- `--program`: Program code

### `update_student`
Update an existing student record.

```bash
python manage.py update_student STU001 \
    --email "newemail@example.com" \
    --level "200"
```

### `delete_student`
Delete a student record.

```bash
python manage.py delete_student STU001
```

### `list_students`
List students with optional filters.

```bash
python manage.py list_students
python manage.py list_students --level "100"
python manage.py list_students --program "BSC-CS"
python manage.py list_students --session "2024/2025"
```

### `search_students`
Search students by name or ID.

```bash
python manage.py search_students "John"
python manage.py search_students --id "STU"
```

### `import_students_csv`
Import students from CSV file.

```bash
python manage.py import_students_csv students.csv
```

**CSV Format:**
```csv
student_id,first_name,last_name,email,level,program
STU001,John,Doe,john@example.com,100,BSC-CS
```

### `import_students_excel`
Import students from Excel file.

```bash
python manage.py import_students_excel students.xlsx
```

### `import_students_json`
Import students from JSON file.

```bash
python manage.py import_students_json students.json
```

### `promote_students`
Promote students to the next level.

```bash
python manage.py promote_students --from-level "100" --to-level "200"
python manage.py promote_students --from-level "100" --to-level "200" --session "2024/2025"
```

### `enroll_student`
Enroll a student in a course.

```bash
python manage.py enroll_student \
    --student STU001 \
    --course CS101 \
    --session "2024/2025" \
    --semester FIRST
```

### `bulk_enroll_students`
Bulk enroll multiple students.

```bash
python manage.py bulk_enroll_students \
    --level "100" \
    --course CS101 \
    --session "2024/2025" \
    --semester FIRST
```

### `update_academic_metrics`
Recalculate GPA and units for students.

```bash
python manage.py update_academic_metrics
python manage.py update_academic_metrics --student STU001
```

### `validate_student_data`
Validate student data integrity.

```bash
python manage.py validate_student_data
```

### `student_analytics`
Generate student analytics report.

```bash
python manage.py student_analytics
python manage.py student_analytics --level "100"
```

---

## Course Management

### `add_course`
Create a new course.

```bash
python manage.py add_course \
    --code "CS101" \
    --title "Introduction to Computer Science" \
    --units 3 \
    --semester FIRST
```

**Options:**
- `--code` (required): Course code
- `--title` (required): Course title
- `--units`: Credit units (default: 3)
- `--semester`: Default semester (FIRST, SECOND)
- `--level`: Associated level(s)

### `update_course`
Update a course.

```bash
python manage.py update_course CS101 --units 4 --title "New Title"
```

### `delete_course`
Delete a course.

```bash
python manage.py delete_course CS101
```

### `list_courses`
List all courses.

```bash
python manage.py list_courses
python manage.py list_courses --level "100"
python manage.py list_courses --semester FIRST
```

### `search_courses`
Search courses by code or title.

```bash
python manage.py search_courses "computer"
python manage.py search_courses --code "CS"
```

---

## Program & Curriculum

### `add_program`
Create a new academic program.

```bash
python manage.py add_program \
    --code "BSC-CS" \
    --name "Bachelor of Science in Computer Science" \
    --min-units 120 \
    --classification BSC
```

**Options:**
- `--code` (required): Program code
- `--name` (required): Program name
- `--min-units`: Minimum units to graduate
- `--classification`: BSC or ND

### `add_curriculum_course`
Add a course to a program's curriculum.

```bash
python manage.py add_curriculum_course \
    --program BSC-CS \
    --course CS101 \
    --required \
    --semester 1
```

**Options:**
- `--program` (required): Program code
- `--course` (required): Course code
- `--required`: Mark as required course
- `--semester`: Recommended semester

### `add_prerequisite`
Add a prerequisite requirement.

```bash
python manage.py add_prerequisite \
    --course CS201 \
    --prerequisite CS101
```

### `suggest_courses`
Suggest courses for a student based on curriculum.

```bash
python manage.py suggest_courses --student STU001
```

---

## Teacher Management

### `add_teacher`
Create a new teacher record.

```bash
python manage.py add_teacher \
    --staff-id "T001" \
    --first-name "Jane" \
    --last-name "Smith" \
    --email "jane@university.edu" \
    --department "Computer Science"
```

### `list_teachers`
List all teachers.

```bash
python manage.py list_teachers
python manage.py list_teachers --department "Computer Science"
```

### `search_teachers`
Search teachers by name or ID.

```bash
python manage.py search_teachers "Smith"
```

### `assign_teacher`
Assign a teacher to a course.

```bash
python manage.py assign_teacher \
    --teacher T001 \
    --course CS101
```

### `bulk_assign_teachers`
Bulk assign teachers to courses.

```bash
python manage.py bulk_assign_teachers --file assignments.csv
```

---

## Enrollment & Grading

### `list_enrollments`
List enrollments with filters.

```bash
python manage.py list_enrollments
python manage.py list_enrollments --student STU001
python manage.py list_enrollments --course CS101
python manage.py list_enrollments --session "2024/2025"
```

### `record_scores`
Record CA and exam scores.

```bash
python manage.py record_scores \
    --student STU001 \
    --course CS101 \
    --session "2024/2025" \
    --semester FIRST \
    --ca 25 \
    --exam 55
```

### `add_grade`
Add or update a grade record.

```bash
python manage.py add_grade \
    --student STU001 \
    --course CS101 \
    --ca-score 25 \
    --exam-score 55
```

### `calculate_grades`
Auto-calculate grades from scores.

```bash
python manage.py calculate_grades
python manage.py calculate_grades --session "2024/2025"
```

### `list_grades`
List grades with filters.

```bash
python manage.py list_grades
python manage.py list_grades --student STU001
python manage.py list_grades --course CS101
python manage.py list_grades --status APPROVED
```

### `submit_grades`
Submit grades for approval.

```bash
python manage.py submit_grades \
    --course CS101 \
    --session "2024/2025" \
    --semester FIRST
```

### `approve_grades`
Approve submitted grades.

```bash
python manage.py approve_grades \
    --course CS101 \
    --session "2024/2025" \
    --semester FIRST
```

### `reject_grades`
Reject submitted grades.

```bash
python manage.py reject_grades \
    --course CS101 \
    --session "2024/2025" \
    --semester FIRST \
    --reason "Scores need verification"
```

### `export_grades_csv`
Export grades to CSV.

```bash
python manage.py export_grades_csv --output grades.csv
python manage.py export_grades_csv --session "2024/2025" --output grades.csv
```

### `export_grades_excel`
Export grades to Excel.

```bash
python manage.py export_grades_excel --output grades.xlsx
```

### `add_grading_setting`
Add a grade scale entry.

```bash
python manage.py add_grading_setting \
    --min 70 \
    --max 100 \
    --grade A \
    --point 4.0
```

### `check_null_sessions`
Check for enrollments with null sessions.

```bash
python manage.py check_null_sessions
```

### `populate_sessions`
Populate missing session data.

```bash
python manage.py populate_sessions
```

---

## Transcripts & Reports

### `generate_transcript`
Generate a transcript for a student.

```bash
python manage.py generate_transcript STU001
python manage.py generate_transcript STU001 --output transcript.pdf
python manage.py generate_transcript STU001 --layout detailed
```

**Options:**
- `--output`: Output file path
- `--layout`: standard, detailed, or simple

### `generate_secure_transcript`
Generate a secure transcript with QR code.

```bash
python manage.py generate_secure_transcript STU001
```

### `batch_generate_transcripts`
Generate transcripts for multiple students.

```bash
python manage.py batch_generate_transcripts --all
python manage.py batch_generate_transcripts --level "400"
python manage.py batch_generate_transcripts --program "BSC-CS"
```

### `verify_transcript`
Verify a transcript using its transaction ID.

```bash
python manage.py verify_transcript TXN-ABC123DEF456
```

### `repeated_courses_report`
Generate report of repeated courses.

```bash
python manage.py repeated_courses_report
python manage.py repeated_courses_report --session "2024/2025"
```

---

## Analytics

### `generate_enrollment_stats`
Generate enrollment statistics.

```bash
python manage.py generate_enrollment_stats
python manage.py generate_enrollment_stats --session "2024/2025"
```

### `generate_student_stats`
Generate student statistics.

```bash
python manage.py generate_student_stats
```

### `generate_teacher_stats`
Generate teacher workload statistics.

```bash
python manage.py generate_teacher_stats
```

### `graduation_audit_report`
Generate graduation eligibility report.

```bash
python manage.py graduation_audit_report
python manage.py graduation_audit_report --program "BSC-CS"
```

### `cohort_graduation_audit`
Audit graduation eligibility by cohort.

```bash
python manage.py cohort_graduation_audit --session "2020/2021"
```

### `student_distribution_report`
Generate student distribution report.

```bash
python manage.py student_distribution_report
```

---

## Configuration

### `update_college_settings`
Update college information.

```bash
python manage.py update_college_settings \
    --name "University of Technology" \
    --address "123 Main Street" \
    --phone "+1234567890" \
    --email "info@university.edu"
```

### `show_settings`
Display current system settings.

```bash
python manage.py show_settings
```

### `update_settings`
Update system settings.

```bash
python manage.py update_settings --key "some_key" --value "some_value"
```

### `show_academic_policy`
Display academic policy settings.

```bash
python manage.py show_academic_policy
```

### `update_academic_policy`
Update academic policy.

```bash
python manage.py update_academic_policy \
    --max-repeats 3 \
    --repeat-policy LAST \
    --probation-gpa 2.0
```

### `seed_data`
Seed sample data for testing.

```bash
python manage.py seed_data
```

### `seed_grading_settings`
Seed default grading scale.

```bash
python manage.py seed_grading_settings
```

---

## User Management

### `create_user`
Create a new user account.

```bash
python manage.py create_user \
    --username "john" \
    --email "john@example.com" \
    --role Teacher
```

### `assign_role`
Assign a role to a user.

```bash
python manage.py assign_role --user john --role Admin
python manage.py assign_role --user john --role DataEntry
python manage.py assign_role --user john --role Teacher
```

### `setup_roles`
Create default system roles.

```bash
python manage.py setup_roles
```

### `list_users`
List all users.

```bash
python manage.py list_users
python manage.py list_users --role Admin
```

### `link_teacher_user`
Link a user account to a teacher profile.

```bash
python manage.py link_teacher_user --user john --teacher-id T001
```

---

## System Utilities

### `log_action`
Manually log an action to audit log.

```bash
python manage.py log_action \
    --action "CUSTOM" \
    --details "Manual action performed"
```

### Django Built-in Commands

```bash
# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
python manage.py runserver 0.0.0.0:8000

# Database operations
python manage.py migrate
python manage.py makemigrations
python manage.py showmigrations

# Static files
python manage.py collectstatic

# Shell access
python manage.py shell
python manage.py dbshell

# Clear sessions
python manage.py clearsessions

# Check deployment
python manage.py check --deploy
```

---

## Command Help

Get help for any command:

```bash
python manage.py help <command_name>
python manage.py <command_name> --help
```

List all available commands:

```bash
python manage.py help
```

---

## Examples

### Complete Student Workflow

```bash
# 1. Create student
python manage.py add_student --student-id STU001 --first-name John --last-name Doe --level 100

# 2. Enroll in courses
python manage.py enroll_student --student STU001 --course CS101 --session "2024/2025" --semester FIRST
python manage.py enroll_student --student STU001 --course MTH101 --session "2024/2025" --semester FIRST

# 3. Record grades
python manage.py record_scores --student STU001 --course CS101 --ca 25 --exam 55
python manage.py record_scores --student STU001 --course MTH101 --ca 28 --exam 62

# 4. Calculate and submit grades
python manage.py calculate_grades --session "2024/2025"
python manage.py submit_grades --session "2024/2025" --semester FIRST

# 5. Approve grades (admin)
python manage.py approve_grades --session "2024/2025" --semester FIRST

# 6. Generate transcript
python manage.py generate_transcript STU001 --output transcript_STU001.pdf
```

### Bulk Operations

```bash
# Import all students
python manage.py import_students_excel new_students.xlsx

# Enroll all 100-level students in a course
python manage.py bulk_enroll_students --level 100 --course CS101 --session "2024/2025"

# Generate all transcripts
python manage.py batch_generate_transcripts --all

# Promote students
python manage.py promote_students --from-level 100 --to-level 200
```

---

*Last Updated: January 2026*
