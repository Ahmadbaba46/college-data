# Academic Transcript Template System

## Overview

The Academic Transcript Template System provides a flexible, reusable framework for generating professional PDF transcripts with consistent styling and multiple layout options. The system is based on detailed analysis of the existing JS001_final_transcript.pdf and implements exact measurements and styling specifications.

## Style Guide Specifications

### Page Layout
- **Page Size**: 8.5" × 11" (US Letter)
- **Margins**: Top: 1.5", Bottom: 1.0", Left/Right: 1.0"
- **Content Width**: 6.5" (page width minus margins)

### Typography Hierarchy
- **College Name**: 28pt Helvetica-Bold, Navy Blue (#1f4788), Center-aligned
- **Document Title**: 22pt Helvetica-Bold, Navy Blue, Center-aligned
- **Section Headers**: 18pt Helvetica-Bold, Navy Blue, Left-aligned
- **Body Text**: 12pt Helvetica, Black, Left-aligned
- **Address Text**: 11pt Helvetica, Gray (#555555), Center-aligned

### Color Palette
- **Primary Navy**: #1f4788 (Headers, table headers)
- **Text Gray**: #555555 (Secondary text, addresses)
- **Table Alternating**: #f0f0f0 (Alternate row background)
- **White**: #ffffff (Table header text, backgrounds)

### Spacing & Measurements
- **Header Spacing**: 0.3"
- **Section Spacing**: 0.25" 
- **Subsection Spacing**: 0.15"
- **Table Row Height**: 24pt
- **Table Cell Padding**: 8pt
- **Logo Size**: 1.0" × 1.0"

## Available Template Layouts

### 1. Standard Layout (`STANDARD_LAYOUT`)
**Best for**: Regular academic transcripts

**Features**:
- College logo and branding
- Student information table
- Courses grouped by session
- Session GPA calculations
- Cumulative GPA
- Clean, professional appearance

**Table Columns**: Course Code | Course Title | Units | Grade

### 2. Detailed Layout (`DETAILED_LAYOUT`)
**Best for**: Comprehensive academic records

**Features**:
- All standard features plus:
- Student photo display
- Grade points column
- Enhanced academic metrics

**Table Columns**: Course Code | Course Title | Units | Grade | Grade Point

### 3. Official Layout (`OFFICIAL_LAYOUT`)
**Best for**: Certified transcripts for external use

**Features**:
- All detailed features plus:
- Certification text
- Signature sections (Registrar, Principal)
- Official seals and stamps
- Watermark support
- Enhanced security features

**Additional Elements**:
- Certification statement
- Official signatures
- Generation timestamp
- Security features

### 4. Simple Layout (`SIMPLE_LAYOUT`)
**Best for**: Internal use, quick reference

**Features**:
- Minimal branding
- Essential student information only
- Cumulative GPA only
- No logos or signatures
- Compact format

## Usage Examples

### Command Line Interface

```bash
# Generate standard transcript
python manage.py generate_transcript JS001 output.pdf

# Generate detailed transcript with grade points
python manage.py generate_transcript JS001 output.pdf --layout detailed

# Generate official certified transcript
python manage.py generate_transcript JS001 output.pdf --layout official

# Generate simple transcript
python manage.py generate_transcript JS001 output.pdf --layout simple

# Custom options
python manage.py generate_transcript JS001 output.pdf --show-student-photo --show-grade-points

# Minimal transcript without logos or session GPAs
python manage.py generate_transcript JS001 output.pdf --no-logo --no-session-gpa --simple-table
```

### Programmatic Usage

```python
from reporting.transcript_generator import (
    generate_standard_transcript,
    generate_detailed_transcript,
    generate_official_transcript,
    TranscriptGenerator
)

# Quick generation with predefined layouts
generate_standard_transcript('JS001', 'standard_transcript.pdf')
generate_detailed_transcript('JS001', 'detailed_transcript.pdf')
generate_official_transcript('JS001', 'official_transcript.pdf')

# Custom configuration
generator = TranscriptGenerator('STANDARD_LAYOUT')
custom_config = {
    'show_student_photo': True,
    'show_grade_points': True,
    'table_columns': ['Course Code', 'Course Title', 'Units', 'Grade', 'Grade Point'],
    'certification_text': 'Custom certification message'
}
generator.generate_transcript('JS001', 'custom_transcript.pdf', custom_config)
```

## Customization Options

### Layout Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `show_logo` | bool | Display college logo | True |
| `show_student_photo` | bool | Display student photo | False |
| `show_grade_points` | bool | Include grade points column | True |
| `show_session_gpa` | bool | Calculate session GPAs | True |
| `show_cumulative_gpa` | bool | Display cumulative GPA | True |
| `show_certification` | bool | Include certification text | False |
| `show_signatures` | bool | Include signature section | False |
| `group_by_session` | bool | Group courses by session | True |
| `table_columns` | list | Define table column structure | varies |

### Column Options

Available table columns:
- `Course Code`: Course identifier
- `Course Title`: Full course name
- `Units`: Credit units/hours
- `Grade`: Letter grade earned
- `Grade Point`: Numerical grade point
- `Session`: Academic session/semester

### Creating Custom Layouts

```python
# Define custom layout configuration
CUSTOM_LAYOUT = {
    'show_logo': True,
    'show_student_photo': True,
    'show_grade_points': True,
    'show_session_gpa': True,
    'show_cumulative_gpa': True,
    'show_certification': False,
    'show_signatures': False,
    'group_by_session': True,
    'table_columns': ['Course Code', 'Course Title', 'Units', 'Grade'],
    'certification_text': 'Custom certification message'
}

# Add to TranscriptLayoutConfig class
TranscriptLayoutConfig.CUSTOM_LAYOUT = CUSTOM_LAYOUT
```

## File Structure

```
reporting/
├── transcript_style_guide.py      # Style specifications and configurations
├── transcript_generator.py        # Main generator class and functions
├── management/commands/
│   └── generate_transcript.py     # Updated Django command
└── TRANSCRIPT_TEMPLATES.md        # This documentation
```

## Integration with Django Models

The system integrates with the following models:

- **Students**: `Student`, `Session`, `Level`
- **Grading**: `Enrollment`, `Grade`, `GradingSettings`
- **Configuration**: `CollegeSettings`
- **Courses**: `Course`

## Error Handling

The system includes comprehensive error handling for:
- Missing student records
- Invalid file paths
- Missing images (logos, photos, signatures)
- Database connection issues
- PDF generation errors

## Performance Considerations

- **Database Optimization**: Uses efficient queries with proper ordering
- **Image Handling**: Graceful fallback for missing images
- **Memory Management**: Efficient PDF generation for large transcripts
- **File I/O**: Safe file handling with proper error checking

## Security Features

For official transcripts:
- Watermark support
- Secure PDF generation
- Timestamp verification
- Digital signature preparation
- Tamper-evident features

## Maintenance and Updates

### Adding New Layouts
1. Define layout configuration in `TranscriptLayoutConfig`
2. Add to command choices in `generate_transcript.py`
3. Create convenience function in `transcript_generator.py`
4. Update documentation

### Modifying Styles
1. Update specifications in `transcript_style_guide.py`
2. Modify `TranscriptStyleFactory` for new styles
3. Test with existing templates
4. Update measurements in `TranscriptDimensions`

### Extending Functionality
1. Add new parameters to layout configurations
2. Implement in `TranscriptGenerator` class
3. Update command line arguments
4. Add tests and documentation

## Best Practices

1. **Consistency**: Always use the style guide specifications
2. **Testing**: Test with various student data scenarios
3. **Validation**: Validate all inputs before processing
4. **Documentation**: Update docs when adding features
5. **Performance**: Profile PDF generation for large datasets
6. **Accessibility**: Ensure PDFs meet accessibility standards

## Migration from Legacy System

The new system is backward compatible with the existing command:

```bash
# Legacy usage (still works)
python manage.py generate_transcript JS001 output.pdf

# New enhanced usage
python manage.py generate_transcript JS001 output.pdf --layout detailed
```

No changes required to existing scripts or integrations.