"""
Reusable Academic Transcript Generator
====================================

This module provides a flexible, template-based system for generating
academic transcripts with consistent styling and multiple layout options.
"""

from django.utils import timezone
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, KeepTogether, PageTemplate, BaseDocTemplate, Frame
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, String, Line
from reportlab.graphics import renderPDF
from reportlab.lib import colors as rl_colors
import os
import datetime
from typing import Dict, List, Optional, Tuple

from students.models import Student, Session
from grading.models import Enrollment, Grade, GradingSettings
from configuration.models import CollegeSettings, AcademicPolicySettings
from reporting.models import Transcript, TranscriptVerificationRecord
from .transcript_style_guide import (
    TRANSCRIPT_STYLES, TRANSCRIPT_DIMENSIONS, TRANSCRIPT_COLORS,
    TranscriptTableStyles, TranscriptLayoutConfig
)
from .security_features import SecureTranscriptFeatures
from .canonical_payload import build_canonical_transcript_payload


class TranscriptGenerator:
    """
    Flexible transcript generator supporting multiple templates and layouts
    """
    
    def __init__(self, layout_config: str = 'STANDARD_LAYOUT'):
        """
        Initialize generator with specified layout configuration
        
        Args:
            layout_config: Layout configuration name from TranscriptLayoutConfig
        """
        self.layout_config = getattr(TranscriptLayoutConfig, layout_config)
        self.styles = TRANSCRIPT_STYLES
        self.dimensions = TRANSCRIPT_DIMENSIONS
        self.colors = TRANSCRIPT_COLORS
        self.table_styles = TranscriptTableStyles()
        self.security_features = SecureTranscriptFeatures()
    
    def _create_watermark(self, text: str, opacity: float = 0.15) -> Drawing:
        """
        Create a watermark drawing for the transcript
        
        Args:
            text: Watermark text
            opacity: Transparency level (0.0 to 1.0)
            
        Returns:
            Drawing object for watermark overlay
        """
        # Create drawing that covers the full page
        d = Drawing(self.dimensions.page_width, self.dimensions.page_height)
        
        # Calculate center position
        x_center = self.dimensions.page_width / 2
        y_center = self.dimensions.page_height / 2
        
        # Create watermark text with rotation
        watermark_color = rl_colors.Color(0.7, 0.7, 0.7, alpha=opacity)
        
        # Main watermark text (rotated manually by positioning)
        from reportlab.graphics.shapes import Group
        from math import cos, sin, radians
        
        # Create a group for the rotated text
        watermark_group = Group()
        
        # Create the text string
        watermark = String(
            0, 0, text,  # Position at origin for rotation
            fontName='Helvetica-Bold',
            fontSize=72,
            fillColor=watermark_color,
            textAnchor='middle'
        )
        
        watermark_group.add(watermark)
        
        # Apply rotation transform (45 degrees)
        angle = 45
        watermark_group.transform = (
            cos(radians(angle)), sin(radians(angle)),
            -sin(radians(angle)), cos(radians(angle)),
            x_center, y_center
        )
        
        d.add(watermark_group)
        
        # Add smaller watermarks in corners
        corner_size = 24
        corner_color = rl_colors.Color(0.8, 0.8, 0.8, alpha=opacity * 0.7)
        
        # Top corners
        d.add(String(1*inch, 10*inch, text, fontName='Helvetica', fontSize=corner_size, fillColor=corner_color))
        d.add(String(7*inch, 10*inch, text, fontName='Helvetica', fontSize=corner_size, fillColor=corner_color))
        
        # Bottom corners  
        d.add(String(1*inch, 0.5*inch, text, fontName='Helvetica', fontSize=corner_size, fillColor=corner_color))
        d.add(String(7*inch, 0.5*inch, text, fontName='Helvetica', fontSize=corner_size, fillColor=corner_color))
        
        return d
        
    def generate_transcript(
        self,
        student_id: str,
        output_file: str,
        custom_config: Optional[Dict] = None,
        *,
        return_security_data: bool = False,
        generated_by=None,
        layout_name: Optional[str] = None,
        create_transcript_record: bool = True,
    ) -> bool | Dict:

        """
        Generate a PDF transcript for the specified student
        
        Args:
            student_id: Student ID to generate transcript for
            output_file: Path to output PDF file
            custom_config: Optional custom configuration overrides
            
        Returns:
            bool: Success status
        """
        try:
            # Merge custom config if provided
            config = self.layout_config.copy()
            if custom_config:
                config.update(custom_config)
                
            # Get student and related data
            student = Student.objects.get(student_id=student_id)
            enrollments = Enrollment.objects.filter(
                student=student
            ).order_by('course_offering__session__name', 'course_offering__course__title')
            college_settings = CollegeSettings.objects.first()
            
            # Create custom document template with fixed footer and security features
            class SecureTranscriptDocTemplate(BaseDocTemplate):
                def __init__(self, filename, watermark_drawing=None, security_data=None, 
                           dimensions=None, colors=None, **kwargs):
                    self.watermark_drawing = watermark_drawing
                    self.security_data = security_data or {}
                    self.dimensions = dimensions or TRANSCRIPT_DIMENSIONS
                    self.colors = colors or TRANSCRIPT_COLORS
                    super().__init__(filename, **kwargs)
                    
                    # Define frames - main content area and footer area
                    content_frame = Frame(
                        self.dimensions.left_margin,
                        self.dimensions.bottom_margin + 1.2 * inch,  # Leave space for footer
                        self.dimensions.content_width,
                        self.dimensions.page_height - self.dimensions.top_margin - self.dimensions.bottom_margin - 1.2 * inch,
                        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0
                    )
                    
                    # Create page template with content frame
                    page_template = PageTemplate(id='transcript', frames=[content_frame])
                    self.addPageTemplates([page_template])
                
                def afterPage(self):
                    """Add watermark, footer elements, and security features to each page"""
                    canvas = self.canv

                    # Embed basic PDF metadata for tamper evidence / audit
                    try:
                        if self.security_data.get('verification_code'):
                            canvas.setTitle('Academic Transcript')
                            canvas.setSubject(f"Verification: {self.security_data.get('verification_code')}")
                    except Exception:
                        pass
                    
                    # Add watermark
                    if self.watermark_drawing:
                        renderPDF.draw(self.watermark_drawing, canvas, 0, 0)
                    
                    # Add fixed footer elements (signatures, QR code, verification info)
                    self._draw_fixed_footer(canvas)
                
                def _draw_fixed_footer(self, canvas):
                    """Draw fixed footer with signatures and security features"""
                    footer_y = self.dimensions.bottom_margin + 0.1 * inch
                    
                    # Security features section (left side)
                    if self.security_data:
                        self._draw_security_section(canvas, footer_y)
                    
                    # Signature section (center)
                    self._draw_signature_section(canvas, footer_y)
                    
                    # Generation timestamp (bottom center)
                    timestamp = timezone.now().strftime("%B %d, %Y at %I:%M %p")
                    canvas.setFont("Helvetica", 8)
                    canvas.setFillColor(self.colors.text_gray)
                    timestamp_text = f"Generated on {timestamp}"
                    text_width = canvas.stringWidth(timestamp_text, "Helvetica", 8)
                    canvas.drawString(
                        self.dimensions.page_width / 2 - text_width/2,
                        footer_y - 0.3 * inch,
                        timestamp_text
                    )
                
                def _draw_security_section(self, canvas, footer_y):
                    """Draw security features (QR code, verification code)"""
                    left_x = self.dimensions.left_margin
                    
                    # QR Code
                    if 'qr_code_path' in self.security_data and os.path.exists(self.security_data['qr_code_path']):
                        try:
                            qr_image = Image(self.security_data['qr_code_path'], width=0.8*inch, height=0.8*inch)
                            qr_image.drawOn(canvas, left_x, footer_y)
                        except:
                            pass  # Skip QR code if error
                    
                    # Verification code
                    if 'verification_code' in self.security_data:
                        canvas.setFont("Helvetica-Bold", 8)
                        canvas.setFillColor(self.colors.primary_navy)
                        canvas.drawString(left_x, footer_y - 0.1 * inch, "Verify at:")
                        
                        canvas.setFont("Helvetica", 7)
                        canvas.drawString(left_x, footer_y - 0.2 * inch, f"Code: {self.security_data['verification_code']}")
                        
                        if 'verification_url' in self.security_data:
                            canvas.setFillColor(self.colors.text_gray)
                            canvas.drawString(left_x, footer_y - 0.3 * inch, "college.edu/verify")
                
                def _draw_signature_section(self, canvas, footer_y):
                    """Draw signature lines in center"""
                    center_x = self.dimensions.page_width / 2
                    signature_width = 2 * inch
                    
                    # Registrar signature (left)
                    registrar_x = center_x - signature_width - 0.5 * inch
                    canvas.setLineWidth(1)
                    canvas.setStrokeColor(self.colors.text_black)
                    canvas.line(registrar_x, footer_y + 0.3 * inch, registrar_x + signature_width, footer_y + 0.3 * inch)
                    
                    canvas.setFont("Helvetica-Bold", 10)
                    canvas.setFillColor(self.colors.text_black)
                    text_width = canvas.stringWidth("Registrar", "Helvetica-Bold", 10)
                    canvas.drawString(registrar_x + signature_width/2 - text_width/2, footer_y + 0.1 * inch, "Registrar")
                    
                    # Principal signature (right)
                    principal_x = center_x + 0.5 * inch
                    canvas.line(principal_x, footer_y + 0.3 * inch, principal_x + signature_width, footer_y + 0.3 * inch)
                    text_width = canvas.stringWidth("Principal", "Helvetica-Bold", 10)
                    canvas.drawString(principal_x + signature_width/2 - text_width/2, footer_y + 0.1 * inch, "Principal")
                    
                    # Digital signature indicator
                    if self.security_data.get('signature_data'):
                        canvas.setFont("Helvetica", 6)
                        canvas.setFillColor(self.colors.text_gray)
                        text = "Digitally Signed Document"
                        text_width = canvas.stringWidth(text, "Helvetica", 6)
                        canvas.drawString(center_x - text_width/2, footer_y - 0.1 * inch, text)
            
            # Generate security features
            security_data = None
            if config.get('add_security_features', True):
                # Create canonical transcript payload for tamper-evident hashing
                payload = build_canonical_transcript_payload(
                    student=student,
                    enrollments=enrollments,
                    college_settings=college_settings,
                )
                security_data = self.security_features.create_secure_transcript_data(
                    student, payload, college_settings
                )
            
            # Check if watermark is requested
            watermark_drawing = None
            if config.get('add_watermark', False):
                watermark_text = config.get('watermark_text', 'OFFICIAL')
                watermark_drawing = self._create_watermark(watermark_text)
            
            # Create secure document template
            doc = SecureTranscriptDocTemplate(
                output_file,
                watermark_drawing=watermark_drawing,
                security_data=security_data,
                dimensions=self.dimensions,
                colors=self.colors,
                pagesize=letter,
                topMargin=self.dimensions.top_margin,
                bottomMargin=self.dimensions.bottom_margin,
                leftMargin=self.dimensions.left_margin,
                rightMargin=self.dimensions.right_margin
            )
            
            # Build document story
            story = []
            
            # Add header section
            story.extend(self._build_header(college_settings, config))
            
            # Add student information
            story.extend(self._build_student_info(student, config))
            
            # Add academic records
            story.extend(self._build_academic_records(enrollments, config))
            
            # Add footer elements (but not signatures - they're now fixed)
            story.extend(self._build_footer(college_settings, config, security_data))
            
            # Build PDF
            doc.build(story)

            # Persist Transcript record (history/audit trail)
            transcript_obj = None
            if create_transcript_record:
                verification_obj = None
                try:
                    if security_data and security_data.get('verification_code'):
                        verification_obj = TranscriptVerificationRecord.objects.filter(
                            verification_code=security_data['verification_code']
                        ).first()
                except Exception:
                    verification_obj = None

                transcript_obj = Transcript.objects.create(
                    student=student,
                    verification=verification_obj,
                    generated_by=generated_by,
                    layout=layout_name or getattr(self, 'layout_config', 'standard') or 'standard',
                    output_file=str(output_file),
                )

            if return_security_data:
                # Return a JSON-serializable payload for callers that need it.
                # `security_data` includes a datetime object; normalize it.
                if security_data and isinstance(security_data.get('generation_timestamp'), datetime.datetime):
                    security_data = dict(security_data)
                    security_data['generation_timestamp'] = security_data['generation_timestamp'].isoformat()
                return {
                    'success': True,
                    'student_id': student.student_id,
                    'output_file': output_file,
                    'security_data': security_data,
                    'transcript_id': transcript_obj.id if transcript_obj else None,
                }

            return True
            
        except Student.DoesNotExist:
            raise ValueError(f'Student with ID {student_id} does not exist.')
        except Exception as e:
            if return_security_data:
                return {
                    'success': False,
                    'student_id': student_id,
                    'output_file': output_file,
                    'error': str(e),
                }
            raise Exception(f'Error generating transcript: {e}')
    
    def _build_header(self, college_settings: CollegeSettings, config: Dict) -> List:
        """Build the header section of the transcript"""
        elements = []
        
        # College logo
        if config.get('show_logo', True) and college_settings and college_settings.college_logo:
            try:
                if os.path.exists(college_settings.college_logo.path):
                    logo = Image(
                        college_settings.college_logo.path,
                        width=self.dimensions.logo_width,
                        height=self.dimensions.logo_height
                    )
                    logo.hAlign = 'CENTER'
                    elements.append(logo)
                    elements.append(Spacer(1, 0.1 * inch))
            except:
                pass  # Skip logo if file issues
        
        # College name and address
        if college_settings:
            elements.append(Paragraph(
                college_settings.college_name or "College Name",
                self.styles['CollegeName']
            ))
            elements.append(Paragraph(
                college_settings.college_address or "College Address",
                self.styles['CollegeAddress']
            ))
        
        elements.append(Spacer(1, self.dimensions.header_spacing))
        
        # Document title
        elements.append(Paragraph(
            "Official Academic Transcript",
            self.styles['DocumentTitle']
        ))
        
        elements.append(Spacer(1, self.dimensions.section_spacing))
        
        return elements
    
    def _build_student_info(self, student: Student, config: Dict) -> List:
        """Build the student information section"""
        elements = []
        
        # Prepare student data
        student_data = [
            [
                Paragraph('<b>Student Name:</b>', self.styles['StudentInfoLabel']),
                Paragraph(f'{student.first_name} {student.last_name}', self.styles['StudentInfoValue'])
            ],
            [
                Paragraph('<b>Student ID:</b>', self.styles['StudentInfoLabel']),
                Paragraph(student.student_id, self.styles['StudentInfoValue'])
            ],
            [
                Paragraph('<b>Entry Level:</b>', self.styles['StudentInfoLabel']),
                Paragraph(
                    student.entry_level.name if student.entry_level else 'N/A',
                    self.styles['StudentInfoValue']
                )
            ]
        ]
        
        # Add current level if different from entry level
        if student.current_level and student.current_level != student.entry_level:
            student_data.append([
                Paragraph('<b>Current Level:</b>', self.styles['StudentInfoLabel']),
                Paragraph(student.current_level.name, self.styles['StudentInfoValue'])
            ])
        
        # Add current session
        if student.current_session:
            student_data.append([
                Paragraph('<b>Current Session:</b>', self.styles['StudentInfoLabel']),
                Paragraph(student.current_session.name, self.styles['StudentInfoValue'])
            ])
        
        # Create student info table - use more of the page width
        student_table = Table(
            student_data,
            colWidths=[1.8 * inch, self.dimensions.content_width - 1.8 * inch]
        )
        student_table.setStyle(self.table_styles.get_student_info_table_style())
        
        # Add student photo if configured
        if config.get('show_student_photo', False) and student.photo:
            try:
                if os.path.exists(student.photo.path):
                    photo = Image(
                        student.photo.path,
                        width=1 * inch,
                        height=1.2 * inch
                    )
                    photo.hAlign = 'RIGHT'
                    
                    # Create table with info and photo
                    combined_data = [[student_table, photo]]
                    combined_table = Table(combined_data, colWidths=[5.5 * inch, 1.5 * inch])
                    combined_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ]))
                    elements.append(combined_table)
                else:
                    elements.append(student_table)
            except:
                elements.append(student_table)
        else:
            elements.append(student_table)
        
        elements.append(Spacer(1, self.dimensions.subsection_spacing))
        
        return elements
    
    def _build_academic_records(self, enrollments, config: Dict) -> List:
        """Build the academic records section"""
        elements = []
        
        if not enrollments.exists():
            elements.append(Paragraph(
                "No academic records found.",
                self.styles['StudentInfoValue']
            ))
            return elements
        
        # Group by session if configured
        if config.get('group_by_session', True):
            elements.extend(self._build_records_by_session(enrollments, config))
        else:
            elements.extend(self._build_records_unified(enrollments, config))
        
        return elements
    
    def _build_records_by_session(self, enrollments, config: Dict) -> List:
        """Build academic records grouped by session, with separate tables per semester."""
        elements = []

        sessions = enrollments.values_list('course_offering__session', flat=True).distinct()
        total_grade_points = 0
        total_units = 0

        # Semester ordering and display names
        semester_order = [
            (Enrollment.SEMESTER_FIRST, 'First Semester'),
            (Enrollment.SEMESTER_SECOND, 'Second Semester'),
            (Enrollment.SEMESTER_SUMMER, 'Summer'),
        ]

        for session_id in sessions:
            session = Session.objects.get(id=session_id)
            session_enrollments = enrollments.filter(course_offering__session=session)

            # Session header
            elements.append(Paragraph(f"Session: {session.name}", self.styles['SessionHeader']))

            session_grade_points = 0
            session_units = 0

            for sem_code, sem_label in semester_order:
                sem_enrollments = session_enrollments.filter(course_offering__semester=sem_code)
                if not sem_enrollments.exists():
                    continue

                # Semester subheader
                elements.append(Paragraph(sem_label, self.styles['SubSectionHeader']))

                table_data, sem_stats = self._build_grade_table_data(sem_enrollments, config)
                if len(table_data) <= 1:
                    continue

                col_widths = self._get_column_widths(config['table_columns'])
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(self.table_styles.get_grades_table_style())
                elements.append(table)

                # Semester GPA
                if config.get('show_session_gpa', True) and sem_stats['total_units'] > 0:
                    sem_gpa = sem_stats['total_grade_points'] / sem_stats['total_units']
                    elements.append(Spacer(1, 0.04 * inch))
                    elements.append(Paragraph(
                        f"<b>{sem_label} GPA: {sem_gpa:.2f}</b>",
                        self.styles['SessionGPA']
                    ))

                elements.append(Spacer(1, self.dimensions.subsection_spacing))

                session_grade_points += sem_stats['total_grade_points']
                session_units += sem_stats['total_units']

            # Session GPA across all semesters (if any)
            if config.get('show_session_gpa', True) and session_units > 0:
                session_gpa = session_grade_points / session_units
                elements.append(Paragraph(
                    f"<b>Session GPA (All Semesters): {session_gpa:.2f}</b>",
                    self.styles['SessionGPA']
                ))
                elements.append(Spacer(1, self.dimensions.subsection_spacing))

            total_grade_points += session_grade_points
            total_units += session_units

        # Cumulative GPA (counts all attempts across all sessions/semesters)
        if config.get('show_cumulative_gpa', True) and total_units > 0:
            cgpa = total_grade_points / total_units
            elements.append(Paragraph(
                f"Cumulative Grade Point Average (CGPA): {cgpa:.2f}",
                self.styles['CumulativeGPA']
            ))

        return elements
    
    def _build_records_unified(self, enrollments, config: Dict) -> List:
        """Build academic records in a single unified table"""
        elements = []
        
        # Build unified table
        table_data, total_stats = self._build_grade_table_data(enrollments, config)
        
        if len(table_data) > 1:
            col_widths = self._get_column_widths(config['table_columns'])
            
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(self.table_styles.get_grades_table_style())
            elements.append(table)
            
            # Overall GPA
            if config.get('show_cumulative_gpa', True) and total_stats['total_units'] > 0:
                cgpa = total_stats['total_grade_points'] / total_stats['total_units']
                elements.append(Spacer(1, self.dimensions.subsection_spacing))
                elements.append(Paragraph(
                    f"Cumulative Grade Point Average (CGPA): {cgpa:.2f}",
                    self.styles['CumulativeGPA']
                ))
        
        return elements
    
    def _build_grade_table_data(self, enrollments, config: Dict) -> Tuple[List, Dict]:
        """Build table data for grade records.

        NOTE: Transcript display includes all attempts, but GPA calculations can be
        configured via AcademicPolicySettings.repeat_policy.
        """
        from grading.repeat_policy import select_enrollments_for_gpa

        columns = config['table_columns']
        table_data = [columns]  # Header row

        policy = AcademicPolicySettings.get_solo().repeat_policy
        counted_ids = select_enrollments_for_gpa(enrollments, policy)

        total_grade_points = 0
        total_units = 0
        
        for enrollment in enrollments:
            try:
                grade = Grade.objects.get(enrollment=enrollment)
                course = enrollment.course
                
                row = []
                
                # Build row based on configured columns
                for column in columns:
                    if column == 'Course Code':
                        row.append(course.code)
                    elif column == 'Course Title':
                        row.append(course.title)
                    elif column == 'Units':
                        row.append(str(course.units))
                    elif column == 'Grade':
                        if AcademicPolicySettings.get_solo().require_approved_for_transcripts and grade.status != Grade.STATUS_APPROVED:
                            row.append('PENDING')
                        else:
                            row.append(grade.grade)
                    elif column == 'Grade Point':
                        try:
                            # Only approved grades count if policy requires it
                            if AcademicPolicySettings.get_solo().require_approved_for_transcripts and grade.status != Grade.STATUS_APPROVED:
                                raise GradingSettings.DoesNotExist()

                            grading_setting = GradingSettings.objects.get(grade_name=grade.grade)
                            grade_point = grading_setting.grade_point
                            row.append(str(grade_point))
                            
                            # Calculate totals (policy-controlled)
                            if enrollment.id in counted_ids:
                                total_grade_points += course.units * grade_point
                                total_units += course.units
                        except GradingSettings.DoesNotExist:
                            row.append('N/A')
                    elif column == 'Session':
                        row.append(enrollment.session.name)
                
                table_data.append(row)
                
                # If not showing grade points in table, still calculate for GPA
                if 'Grade Point' not in columns and enrollment.id in counted_ids:
                    try:
                        grading_setting = GradingSettings.objects.get(grade_name=grade.grade)
                        grade_point = grading_setting.grade_point
                        total_grade_points += course.units * grade_point
                        total_units += course.units
                    except GradingSettings.DoesNotExist:
                        pass
                        
            except Grade.DoesNotExist:
                # Handle enrollment without grade (still display it)
                row = []
                for column in columns:
                    if column == 'Course Code':
                        row.append(enrollment.course.code)
                    elif column == 'Course Title':
                        row.append(enrollment.course.title)
                    elif column == 'Units':
                        row.append(str(enrollment.course.units))
                    elif column in ['Grade', 'Grade Point']:
                        row.append('N/A')
                    elif column == 'Session':
                        row.append(enrollment.session.name)

                table_data.append(row)

                # Attempted units count toward GPA denominator only if this attempt is counted
                # and only in this no-grade branch.
                if enrollment.id in counted_ids:
                    total_units += enrollment.course.units
        
        stats = {
            'total_grade_points': total_grade_points,
            'total_units': total_units
        }
        
        return table_data, stats
    
    def _get_column_widths(self, columns: List[str]) -> List[float]:
        """Get appropriate column widths based on columns - optimized for full page width"""
        # Calculate available width for table (full content width)
        available_width = self.dimensions.content_width
        
        # Define minimum column widths and flexibility
        width_map = {
            'Course Code': self.dimensions.course_code_width,
            'Course Title': self.dimensions.course_title_width,
            'Units': self.dimensions.units_width,
            'Grade': self.dimensions.grade_width,
            'Grade Point': getattr(self.dimensions, 'grade_point_width', self.dimensions.grade_width),
            'Session': 1.0 * inch,
        }
        
        # Get base widths
        base_widths = [width_map.get(col, 1.0 * inch) for col in columns]
        total_base_width = sum(base_widths)
        
        # Always stretch to use full available width
        if total_base_width < available_width:
            extra_width = available_width - total_base_width
            # Distribute extra width primarily to Course Title
            for i, col in enumerate(columns):
                if col == 'Course Title':
                    base_widths[i] += extra_width
                    break
        elif total_base_width > available_width:
            # Scale down proportionally if too wide
            scale_factor = available_width / total_base_width
            base_widths = [w * scale_factor for w in base_widths]
        
        return base_widths
    
    def _build_footer(self, college_settings: CollegeSettings, config: Dict, security_data: Optional[Dict] = None) -> List:
        """Build the footer section"""
        elements = []
        
        # Add certification text if configured
        if config.get('show_certification', False):
            cert_text = config.get(
                'certification_text',
                "This is to certify that the above is a true and complete record of the academic achievement of the above-named student."
            )
            elements.append(Spacer(1, self.dimensions.subsection_spacing))
            elements.append(Paragraph(cert_text, self.styles['CertificationText']))
        
        # Add security information in content area if needed
        if security_data and config.get('show_security_info', False):
            elements.append(Spacer(1, self.dimensions.subsection_spacing))
            elements.append(Paragraph(
                f"Document Hash: {security_data.get('document_hash', '')[:16]}...",
                self.styles['Footer']
            ))
        
        # Note: Signatures and timestamp are now handled in fixed footer
        
        return elements
    
    def _build_signature_section(self, college_settings: CollegeSettings) -> List:
        """Build signature section for official transcripts"""
        elements = []
        
        elements.append(Spacer(1, 0.1 * inch))
        
        # Create signature table
        signature_data = []
        
        # Principal signature
        if college_settings and college_settings.principal_signature:
            try:
                if os.path.exists(college_settings.principal_signature.path):
                    sig_image = Image(
                        college_settings.principal_signature.path,
                        width=self.dimensions.signature_width,
                        height=self.dimensions.signature_height
                    )
                    signature_data.append([sig_image, ""])
                else:
                    signature_data.append(["_" * 30, "_" * 30])
            except:
                signature_data.append(["_" * 30, "_" * 30])
        else:
            signature_data.append(["_" * 30, "_" * 30])
        
        signature_data.append([
            Paragraph("<b>Registrar</b>", self.styles['StudentInfoValue']),
            Paragraph("<b>Principal</b>", self.styles['StudentInfoValue'])
        ])
        
        sig_table = Table(signature_data, colWidths=[3 * inch, 3 * inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('TOPPADDING', (0, 1), (-1, 1), 6),
        ]))
        
        elements.append(sig_table)
        
        return elements


# Convenience functions for common use cases
def generate_standard_transcript(student_id: str, output_file: str) -> bool:
    """Generate a standard academic transcript"""
    generator = TranscriptGenerator('STANDARD_LAYOUT')
    return generator.generate_transcript(student_id, output_file)


def generate_detailed_transcript(student_id: str, output_file: str) -> bool:
    """Generate a detailed transcript with grade points"""
    generator = TranscriptGenerator('DETAILED_LAYOUT')
    return generator.generate_transcript(student_id, output_file)


def generate_official_transcript(student_id: str, output_file: str) -> bool:
    """Generate an official certified transcript"""
    generator = TranscriptGenerator('OFFICIAL_LAYOUT')
    return generator.generate_transcript(student_id, output_file)


def generate_simple_transcript(student_id: str, output_file: str) -> bool:
    """Generate a simple transcript with minimal information"""
    generator = TranscriptGenerator('SIMPLE_LAYOUT')
    return generator.generate_transcript(student_id, output_file)