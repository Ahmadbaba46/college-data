# College Data Management System - User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Managing Students](#managing-students)
4. [Managing Programs](#managing-programs)
5. [Managing Courses](#managing-courses)
6. [Enrollment Management](#enrollment-management)
7. [Grading System](#grading-system)
8. [Transcripts](#transcripts)
9. [Analytics & Reports](#analytics--reports)
10. [Teacher Portal](#teacher-portal)

---

## Getting Started

### Logging In

1. Navigate to the application URL
2. Enter your username and password
3. Click "Sign In"

### User Roles

The system supports three primary roles:

| Role | Description | Access Level |
|------|-------------|--------------|
| **Admin** | Full system administrator | All features, settings, user management |
| **DataEntry** | Data entry staff | Students, courses, enrollments (no settings) |
| **Teacher** | Instructors | View assigned courses, enter grades |

### Navigation

The sidebar provides quick access to all modules:
- **Dashboard** - Overview and quick stats
- **Students** - Student management
- **Programs** - Academic programs
- **Courses** - Course catalog
- **Enrollments** - Student enrollments
- **Teachers** - Teacher management
- **Transcripts** - Generate transcripts
- **Reports** - Grading reports
- **Analytics** - Data analytics
- **Settings** (Admin only) - System configuration

---

## Dashboard Overview

The dashboard provides at-a-glance information:

### Statistics Cards
- Total Students
- Total Courses
- Active Enrollments
- Pending Grade Approvals

### Charts
- **Enrollment Trends** - Monthly enrollment statistics
- **Student Distribution** - Students by level and program
- **Grade Distribution** - Overall grade breakdown

### Quick Actions
- Add New Student
- Create Enrollment
- Generate Transcript

### Alerts
- **Repeated Courses Alert** - Students who have repeated courses
- **Graduation Eligibility** - Students eligible for graduation

---

## Managing Students

### Viewing Students

1. Click **Students** in the sidebar
2. Use the search box to find students by ID, name, or email
3. Use filters to narrow by level, program, or status

### Adding a New Student

1. Click **Add Student** button
2. Fill in required fields:
   - Student ID (unique identifier)
   - First Name
   - Last Name
   - Email (optional)
   - Current Level
   - Program (optional)
3. Upload a photo (optional)
4. Click **Create Student**

### Editing a Student

1. Find the student in the list
2. Click the student's name or the Edit icon
3. Modify the desired fields
4. Click **Save Changes**

### Student Detail Page

The student detail page shows:
- **Overview Tab** - Basic information, contact details, photo
- **Enrollments Tab** - All course enrollments with grades
- **Academic Record Tab** - Session-by-session breakdown with GPA

### Bulk Operations

#### Importing Students
1. Click **Import** button
2. Select file format (CSV, Excel, or JSON)
3. Upload your file
4. Review and confirm import

#### Promoting Students
1. Click **Promote** button
2. Select source level
3. Select destination level
4. Review students to be promoted
5. Confirm promotion

#### Assigning Programs
1. Select multiple students using checkboxes
2. Click **Assign Program**
3. Select the target program
4. Confirm assignment

---

## Managing Programs

### What is a Program?

A program represents an academic degree or certificate (e.g., "Bachelor of Computer Science").

### Viewing Programs

1. Click **Programs** in the sidebar
2. Browse the program cards
3. Use search and department filter to find specific programs

### Creating a Program

1. Click **Add Program**
2. Enter:
   - Program Code (e.g., "BSC-CS")
   - Program Name
   - Department
   - Minimum Units to Graduate
   - Classification Scheme (BSc or ND/HND)
3. Click **Create Program**

### Program Details

The program detail page shows:
- Program information
- **Curriculum** - Courses required for this program
- **Classification Thresholds** - GPA ranges for honors
- **Students** - Students enrolled in this program

### Managing Curriculum

#### Adding Courses to Curriculum
1. Go to program detail page
2. Scroll to Curriculum section
3. Click **Add Course**
4. Select course and set as required/elective
5. Optionally set semester recommendation

#### Managing Prerequisites
1. Click **Manage Prerequisites**
2. View the prerequisite chain visualization
3. Add/remove prerequisites for courses

#### Copying Curriculum
1. Click **Copy Curriculum**
2. Select source program
3. Courses and prerequisites will be copied

---

## Managing Courses

### Viewing Courses

1. Click **Courses** in the sidebar
2. Search by code or title
3. Filter by department, level, or semester

### Creating a Course

1. Click **Add Course**
2. Enter:
   - Course Code (e.g., "CS101")
   - Course Title
   - Credit Units
   - Department
   - Default Semester (optional)
3. Click **Create Course**

### Course Offerings

A course offering represents a specific instance of a course in a session/semester.

#### Creating an Offering
1. Go to course detail page
2. Click **Add Offering**
3. Select:
   - Session (e.g., "2024/2025")
   - Semester (First, Second, or Summer)
   - Level (optional)
   - Assigned Teacher
   - Capacity (optional)
4. Click **Create Offering**

---

## Enrollment Management

### Viewing Enrollments

1. Click **Enrollments** in the sidebar
2. Filter by session, semester, student, or course
3. Use multi-select for course filtering

### Single Enrollment

1. Click **Add Enrollment**
2. Select student
3. Select course offering
4. The system validates:
   - Prerequisites
   - Capacity limits
   - Repeat limits
5. Click **Enroll**

### Bulk Enrollment

1. Click **Bulk Enroll**
2. Filter students by level
3. Filter offerings by session/semester
4. Select students (use "Select All Visible")
5. Select course offerings
6. Click **Enroll Selected**

### Enrollment Validation

The system automatically checks:
- ✅ **Prerequisites** - Has student passed required courses?
- ✅ **Capacity** - Is the offering full?
- ✅ **Repeat Limit** - Has student exceeded max attempts?
- ✅ **Already Enrolled** - Is student already in this offering?

Warnings are shown for level mismatches but don't block enrollment.

---

## Grading System

### For Teachers

#### Viewing Your Courses
1. Click **Grading** → **My Courses**
2. See all offerings assigned to you
3. Click an offering to enter grades

#### Entering Grades
1. Select a course offering
2. For each student, enter:
   - CA Score (Continuous Assessment)
   - Exam Score
3. Total and letter grade calculate automatically
4. Click **Save as Draft** to save progress

#### Submitting Grades
1. Review all grades
2. Click **Submit for Approval**
3. Grades move to "Submitted" status
4. Wait for admin approval

### For Admins

#### Approval Queue
1. Click **Grading** → **Approval Queue**
2. View all pending submissions grouped by offering
3. Click to review grades

#### Approving/Rejecting
1. Review the submitted grades
2. Click **Approve** to finalize
3. Or click **Reject** with a reason
4. Teacher will be notified

### Grade History
- Click **Reports** → **Grade History**
- View all grade changes with timestamps
- Filter by student, course, or date

---

## Transcripts

### Generating a Single Transcript

1. Click **Transcripts** → **Generate**
2. Search and select a student
3. Choose layout style:
   - **Standard** - Traditional format
   - **Detailed** - With course descriptions
   - **Simple** - Minimal format
4. Click **Generate Transcript**
5. Download the PDF

### Batch Generation

1. Click **Transcripts** → **Batch Generate**
2. Select generation type:
   - All Students
   - By Program
   - By Level
   - By Graduation Status
3. Apply filters as needed
4. Click **Generate All**
5. Download as ZIP file

### Transcript Verification

1. Click **Transcripts** → **Verify**
2. Either:
   - Scan the QR code on a transcript
   - Enter the transaction ID manually
3. View verification result

---

## Analytics & Reports

### Overview Dashboard
- Key metrics and trends
- Quick navigation to detailed analytics

### Available Reports

#### Enrollment Analytics
- Enrollment trends over time
- Top courses by enrollment
- Session comparison

#### Student Analytics
- Demographics breakdown
- Performance by level
- GPA distribution

#### Grade Analytics
- Grade distribution by course
- Pass/fail rates
- Course difficulty analysis

#### Teacher Analytics
- Workload distribution
- Pass rates by teacher
- Department breakdown

#### Graduation Analytics
- Eligibility tracking
- Program completion rates
- Time to graduation

### Exporting Data
- Each analytics page has an **Export CSV** button
- Data can be downloaded for external analysis

---

## Teacher Portal

Teachers have a focused interface for their responsibilities:

### My Courses
View all course offerings assigned to you for the current session.

### Grade Entry
Enter CA and exam scores for enrolled students.

### Submit Grades
Submit completed grades for admin approval.

### View History
See past grades and approval status.

---

## Tips & Best Practices

### Data Entry
- Always verify student IDs before enrollment
- Use bulk operations for efficiency
- Review imports before confirming

### Grading
- Save drafts frequently
- Review all grades before submitting
- Check for outliers (very high/low scores)

### Reports
- Generate transcripts after grades are approved
- Use analytics to identify at-risk students
- Export data regularly for backup

---

## Troubleshooting

### Common Issues

**Can't log in?**
- Check username/password
- Contact admin if locked out

**Missing permissions?**
- Verify your role with admin
- Some features require Admin role

**Enrollment failed?**
- Check prerequisite requirements
- Verify offering has capacity
- Check repeat limits

**Grades not saving?**
- Ensure scores are within valid range (0-100)
- Check for required fields

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `/` | Focus search box |
| `Esc` | Close modal/dropdown |
| `Enter` | Submit form |

---

## Getting Help

- Contact your system administrator
- Check the error messages for guidance
- Review this guide for feature explanations

---

*Last Updated: January 2026*
