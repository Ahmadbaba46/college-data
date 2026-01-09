"""
Academic Transcript Style Guide and Template Configuration
=========================================================

This module defines the comprehensive style guide and reusable template
configuration for generating academic transcripts with consistent branding
and professional appearance.

Based on analysis of JS001_final_transcript.pdf
"""

from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


@dataclass
class TranscriptDimensions:
    """Exact measurements and spacing for transcript layout"""
    
    # Page Setup
    page_size = letter  # 8.5" × 11"
    page_width = 8.5 * inch
    page_height = 11 * inch
    
    # Margins - Minimal for maximum space utilization
    top_margin = 0.4 * inch
    bottom_margin = 0.3 * inch
    left_margin = 0.3 * inch
    right_margin = 0.3 * inch
    content_width = page_width - left_margin - right_margin
    
    # Vertical Spacing - Minimal for single page layout
    header_spacing = 0.08 * inch
    section_spacing = 0.06 * inch
    subsection_spacing = 0.04 * inch
    line_spacing = 0.03 * inch
    
    # Logo and Images
    logo_width = 1.0 * inch
    logo_height = 1.0 * inch
    signature_width = 1.5 * inch
    signature_height = 0.75 * inch
    
    # Table Specifications
    table_row_height = 24  # points
    table_header_padding = 12  # points
    table_cell_padding = 8  # points
    
    # Column Widths (maximized for full page width utilization - 7.9" total)
    course_code_width = 1.1 * inch
    course_title_width = 5.2 * inch  # Takes up most space
    units_width = 0.6 * inch
    grade_width = 0.5 * inch
    grade_point_width = 0.5 * inch


@dataclass
class TranscriptColors:
    """Color palette for transcript design"""
    
    # Primary Colors
    primary_navy = colors.HexColor('#1f4788')  # Headers, table headers
    primary_dark = colors.HexColor('#002060')  # Alternative dark blue
    
    # Secondary Colors
    text_black = colors.black
    text_gray = colors.HexColor('#555555')  # Address, secondary text
    text_light_gray = colors.HexColor('#777777')
    
    # Background Colors
    bg_white = colors.white
    bg_light_gray = colors.HexColor('#f8f9fa')
    bg_table_alt = colors.HexColor('#f0f0f0')  # Alternating table rows
    
    # Accent Colors
    border_light = colors.HexColor('#e0e0e0')
    border_medium = colors.HexColor('#cccccc')


@dataclass
class TranscriptTypography:
    """Typography specifications for all text elements"""
    
    # Font Families
    primary_font = 'Helvetica'
    primary_font_bold = 'Helvetica-Bold'
    secondary_font = 'Times-Roman'  # For formal elements if needed
    
    # Font Sizes (in points) - Compact for single page layout
    college_name_size = 20
    document_title_size = 16
    section_header_size = 12
    subsection_header_size = 11
    body_text_size = 10
    small_text_size = 8
    address_text_size = 9
    
    # Line Heights (leading) - Tighter spacing for compact layout
    header_leading = 28  # 24pt + 4pt spacing
    title_leading = 22   # 18pt + 4pt spacing
    body_leading = 14    # 11pt + 3pt spacing
    tight_leading = 12   # 11pt + 1pt spacing


class TranscriptStyleFactory:
    """Factory class to create consistent ReportLab styles"""
    
    @staticmethod
    def create_styles() -> Dict[str, ParagraphStyle]:
        """Generate all paragraph styles for transcript"""
        
        colors_config = TranscriptColors()
        typo = TranscriptTypography()
        
        styles = {}
        
        # College Header Styles
        styles['CollegeName'] = ParagraphStyle(
            name='CollegeName',
            fontName=typo.primary_font_bold,
            fontSize=typo.college_name_size,
            leading=typo.header_leading,
            alignment=1,  # Center
            textColor=colors_config.primary_navy,
            spaceBefore=0,
            spaceAfter=3,
        )
        
        styles['CollegeAddress'] = ParagraphStyle(
            name='CollegeAddress',
            fontName=typo.primary_font,
            fontSize=typo.address_text_size,
            leading=typo.tight_leading,
            alignment=1,  # Center
            textColor=colors_config.text_gray,
            spaceBefore=0,
            spaceAfter=4,
        )
        
        # Document Title
        styles['DocumentTitle'] = ParagraphStyle(
            name='DocumentTitle',
            fontName=typo.primary_font_bold,
            fontSize=typo.document_title_size,
            leading=typo.title_leading,
            alignment=1,  # Center
            textColor=colors_config.primary_navy,
            spaceBefore=8,
            spaceAfter=10,
        )
        
        # Student Information
        styles['StudentInfoLabel'] = ParagraphStyle(
            name='StudentInfoLabel',
            fontName=typo.primary_font_bold,
            fontSize=typo.body_text_size,
            leading=typo.body_leading,
            alignment=0,  # Left
            textColor=colors_config.text_black,
            spaceBefore=2,
            spaceAfter=2,
        )
        
        styles['StudentInfoValue'] = ParagraphStyle(
            name='StudentInfoValue',
            fontName=typo.primary_font,
            fontSize=typo.body_text_size,
            leading=typo.body_leading,
            alignment=0,  # Left
            textColor=colors_config.text_black,
            spaceBefore=2,
            spaceAfter=2,
        )
        
        # Section Headers
        styles['SessionHeader'] = ParagraphStyle(
            name='SessionHeader',
            fontName=typo.primary_font_bold,
            fontSize=typo.section_header_size,
            leading=16,
            alignment=0,  # Left
            textColor=colors_config.primary_navy,
            spaceBefore=8,
            spaceAfter=4,
            borderWidth=0,
            borderColor=colors_config.primary_navy,
            borderPadding=0,
        )

        styles['SubSectionHeader'] = ParagraphStyle(
            name='SubSectionHeader',
            fontName=typo.primary_font_bold,
            fontSize=typo.body_text_size,
            leading=typo.body_leading,
            alignment=0,  # Left
            textColor=colors_config.text_black,
            spaceBefore=6,
            spaceAfter=3,
        )
        
        # GPA Text Styles
        styles['SessionGPA'] = ParagraphStyle(
            name='SessionGPA',
            fontName=typo.primary_font_bold,
            fontSize=typo.body_text_size,
            leading=typo.body_leading,
            alignment=2,  # Right
            textColor=colors_config.primary_navy,
            spaceBefore=8,
            spaceAfter=4,
        )
        
        styles['CumulativeGPA'] = ParagraphStyle(
            name='CumulativeGPA',
            fontName=typo.primary_font_bold,
            fontSize=typo.section_header_size,
            leading=16,
            alignment=0,  # Left
            textColor=colors_config.primary_navy,
            spaceBefore=8,
            spaceAfter=6,
        )
        
        # Footer Styles
        styles['Footer'] = ParagraphStyle(
            name='Footer',
            fontName=typo.primary_font,
            fontSize=typo.small_text_size,
            leading=12,
            alignment=1,  # Center
            textColor=colors_config.text_gray,
            spaceBefore=36,
            spaceAfter=0,
        )
        
        # Certification Text
        styles['CertificationText'] = ParagraphStyle(
            name='CertificationText',
            fontName=typo.primary_font,
            fontSize=typo.body_text_size,
            leading=typo.body_leading,
            alignment=0,  # Left
            textColor=colors_config.text_black,
            spaceBefore=24,
            spaceAfter=12,
        )
        
        return styles


class TranscriptTableStyles:
    """Pre-configured table styles for different transcript sections"""
    
    @staticmethod
    def get_student_info_table_style():
        """Style for student information table"""
        from reportlab.platypus import TableStyle
        
        return TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ])
    
    @staticmethod
    def get_grades_table_style():
        """Style for grades/courses table"""
        from reportlab.platypus import TableStyle
        
        colors_config = TranscriptColors()
        dims = TranscriptDimensions()
        
        return TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors_config.primary_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors_config.bg_white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Header padding
            ('TOPPADDING', (0, 0), (-1, 0), dims.table_header_padding),
            ('BOTTOMPADDING', (0, 0), (-1, 0), dims.table_header_padding),
            ('LEFTPADDING', (0, 0), (-1, 0), dims.table_cell_padding),
            ('RIGHTPADDING', (0, 0), (-1, 0), dims.table_cell_padding),
            
            # Data rows styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),  # Units and Grade columns centered
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            
            # Data row padding
            ('TOPPADDING', (0, 1), (-1, -1), dims.table_cell_padding),
            ('BOTTOMPADDING', (0, 1), (-1, -1), dims.table_cell_padding),
            ('LEFTPADDING', (0, 1), (-1, -1), dims.table_cell_padding),
            ('RIGHTPADDING', (0, 1), (-1, -1), dims.table_cell_padding),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors_config.bg_white, colors_config.bg_table_alt]),
            
            # Borders
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors_config.primary_navy),
            ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors_config.border_light),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors_config.border_medium),
        ])


class TranscriptLayoutConfig:
    """Configuration class for different transcript layouts"""
    
    # Standard Academic Transcript Layout
    STANDARD_LAYOUT = {
        'show_logo': True,
        'show_student_photo': True,
        'show_grade_points': True,
        'show_session_gpa': True,
        'show_cumulative_gpa': True,
        'show_certification': True,
        'show_signatures': True,
        'group_by_session': True,
        'table_columns': ['Course Code', 'Course Title', 'Units', 'Grade'],
    }
    
    # Detailed Academic Transcript (with grade points)
    DETAILED_LAYOUT = {
        'show_logo': True,
        'show_student_photo': True,
        'show_grade_points': True,
        'show_session_gpa': True,
        'show_cumulative_gpa': True,
        'show_certification': True,
        'show_signatures': True,
        'group_by_session': True,
        'table_columns': ['Course Code', 'Course Title', 'Units', 'Grade', 'Grade Point'],
    }
    
    # Simple Transcript (minimal information)
    SIMPLE_LAYOUT = {
        'show_logo': False,
        'show_student_photo': False,
        'show_grade_points': False,
        'show_session_gpa': False,
        'show_cumulative_gpa': True,
        'show_certification': False,
        'show_signatures': False,
        'group_by_session': True,
        'table_columns': ['Course Code', 'Course Title', 'Units', 'Grade'],
    }
    
    # Official Certified Transcript
    OFFICIAL_LAYOUT = {
        'show_logo': True,
        'show_student_photo': True,
        'show_grade_points': True,
        'show_session_gpa': True,
        'show_cumulative_gpa': True,
        'show_certification': True,
        'show_signatures': True,
        'show_seal': True,
        'group_by_session': True,
        'table_columns': ['Course Code', 'Course Title', 'Units', 'Grade', 'Grade Point'],
        'add_watermark': True,
        'certification_text': "This is to certify that the above is a true and complete record of the academic achievement of the above-named student.",
    }


# Quick access to common configurations
TRANSCRIPT_STYLES = TranscriptStyleFactory.create_styles()
TRANSCRIPT_DIMENSIONS = TranscriptDimensions()
TRANSCRIPT_COLORS = TranscriptColors()
TRANSCRIPT_TYPOGRAPHY = TranscriptTypography()