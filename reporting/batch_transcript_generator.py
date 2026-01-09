"""
Batch Transcript Generator with Watermark Support
===============================================

This module extends the transcript generation system to support:
1. Batch processing of multiple students
2. Watermark and security features
3. Progress tracking and reporting
4. Output organization and management
"""

import os
import datetime
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from django.db.models import Q
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import String, Drawing
from reportlab.graphics.renderPDF import drawToFile
from io import BytesIO
import zipfile

from students.models import Student, Session
from grading.models import Enrollment
from configuration.models import CollegeSettings
from .transcript_generator import TranscriptGenerator
from .transcript_style_guide import TranscriptLayoutConfig


class WatermarkGenerator:
    """Generate watermarks and security features for transcripts"""
    
    @staticmethod
    def create_text_watermark(text: str, opacity: float = 0.1, 
                            font_size: int = 60, rotation: int = 45) -> Drawing:
        """
        Create a text-based watermark
        
        Args:
            text: Watermark text (e.g., "OFFICIAL", "CONFIDENTIAL")
            opacity: Transparency level (0.0 to 1.0)
            font_size: Size of watermark text
            rotation: Rotation angle in degrees
            
        Returns:
            Drawing object for watermark
        """
        # Create drawing canvas
        d = Drawing(8.5 * inch, 11 * inch)
        
        # Calculate center position
        x_center = 4.25 * inch
        y_center = 5.5 * inch
        
        # Create watermark text
        watermark = String(
            x_center, y_center, text,
            fontName='Helvetica-Bold',
            fontSize=font_size,
            fillColor=colors.Color(0.5, 0.5, 0.5, alpha=opacity),
            textAnchor='middle'
        )
        
        # Apply rotation
        watermark.rotate(rotation)
        d.add(watermark)
        
        return d
    
    @staticmethod
    def create_security_pattern() -> Drawing:
        """Create a subtle security pattern background"""
        d = Drawing(8.5 * inch, 11 * inch)
        
        # Create a grid pattern
        grid_spacing = 0.5 * inch
        line_color = colors.Color(0.9, 0.9, 0.9, alpha=0.3)
        
        # Vertical lines
        for x in range(0, int(8.5 * inch), int(grid_spacing)):
            d.add(String(x, 0, '|', fillColor=line_color))
        
        # Horizontal lines  
        for y in range(0, int(11 * inch), int(grid_spacing)):
            d.add(String(0, y, '_', fillColor=line_color))
            
        return d


class BatchTranscriptGenerator:
    """
    Enhanced transcript generator with batch processing and security features
    """
    
    def __init__(self, layout_config: str = 'STANDARD_LAYOUT'):
        """Initialize batch generator with layout configuration"""
        self.generator = TranscriptGenerator(layout_config)
        self.layout_config = layout_config
        self.watermark_gen = WatermarkGenerator()
        
    def generate_batch_transcripts(
        self,
        student_ids: List[str] = None,
        output_dir: str = "transcripts",
        layout: str = "standard",
        custom_config: Optional[Dict] = None,
        add_watermark: bool = False,
        watermark_text: str = "OFFICIAL",
        create_zip: bool = False,
        max_workers: int = 4,
        progress_callback: Optional[callable] = None,
        save_security_data: bool = False,
    ) -> Dict[str, any]:
        """
        Generate transcripts for multiple students in batch
        
        Args:
            student_ids: List of student IDs, if None processes all students
            output_dir: Directory to save transcripts
            layout: Layout template to use
            custom_config: Custom configuration overrides
            add_watermark: Whether to add watermark
            watermark_text: Text for watermark
            create_zip: Create zip archive of all transcripts
            max_workers: Number of parallel workers
            progress_callback: Function to call with progress updates
            
        Returns:
            Dictionary with generation results and statistics
        """
        
        # Setup output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Get student list
        if student_ids is None:
            students = Student.objects.all()
        else:
            students = Student.objects.filter(student_id__in=student_ids)
        
        if not students.exists():
            return {
                'success': False,
                'error': 'No students found matching criteria',
                'total_students': 0,
                'successful': 0,
                'failed': 0
            }
        
        # Initialize tracking
        results = {
            'success': True,
            'total_students': students.count(),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'generated_files': [],
            'start_time': datetime.datetime.now(),
            'zip_file': None
        }
        
        # Generate transcripts with parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks
            future_to_student = {
                executor.submit(
                    self._generate_single_transcript,
                    student,
                    output_path,
                    layout,
                    custom_config,
                    add_watermark,
                    watermark_text,
                    save_security_data
                ): student for student in students
            }
            
            # Process completed tasks
            for future in as_completed(future_to_student):
                student = future_to_student[future]
                
                try:
                    file_path, success, _security_data = future.result()

                    # include sidecar JSON in zip/archive list if present
                    if save_security_data and success:
                        json_path = str(file_path).replace('.pdf', '_security.json')
                        if os.path.exists(json_path):
                            results['generated_files'].append(json_path)
                    
                    if success:
                        results['successful'] += 1
                        results['generated_files'].append(file_path)
                        
                        if progress_callback:
                            progress_callback(
                                results['successful'], 
                                results['total_students'],
                                f"Generated transcript for {student.student_id}"
                            )
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to generate transcript for {student.student_id}")
                        
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Error processing {student.student_id}: {str(e)}")
        
        # Create zip archive if requested
        if create_zip and results['generated_files']:
            zip_path = self._create_zip_archive(output_path, results['generated_files'])
            results['zip_file'] = str(zip_path)
        
        # Calculate completion time
        results['end_time'] = datetime.datetime.now()
        results['duration'] = results['end_time'] - results['start_time']
        
        return results
    
    def _generate_single_transcript(
        self,
        student: Student,
        output_path: Path,
        layout: str,
        custom_config: Optional[Dict],
        add_watermark: bool,
        watermark_text: str,
        save_security_data: bool = False,
    ) -> Tuple[str, bool, Optional[dict]]:
        """Generate transcript for a single student"""
        
        try:
            # Create filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{student.student_id}_{layout}_{timestamp}.pdf"
            file_path = output_path / filename
            
            # Prepare configuration
            config = custom_config.copy() if custom_config else {}
            
            # Add watermark if requested
            if add_watermark:
                config['add_watermark'] = True
                config['watermark_text'] = watermark_text
            
            # Generate transcript (optionally returning security data)
            result = self.generator.generate_transcript(
                student.student_id,
                str(file_path),
                config,
                return_security_data=save_security_data,
            )

            if isinstance(result, dict):
                success = bool(result.get('success'))
                security_data = result.get('security_data')
            else:
                success = bool(result)
                security_data = None

            # Optionally write a sidecar JSON file with security metadata
            if save_security_data and success and security_data:
                json_path = str(file_path).replace('.pdf', '_security.json')
                try:
                    import json
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(
                            {
                                'student_id': student.student_id,
                                'output_file': str(file_path),
                                'security_data': security_data,
                            },
                            f,
                            indent=2,
                            default=str,
                        )
                except Exception:
                    # Best-effort only; transcript generation already succeeded.
                    pass

            return str(file_path), success, security_data
            
        except Exception as e:
            return f"Error: {str(e)}", False, None
    
    def _create_zip_archive(self, output_path: Path, file_paths: List[str]) -> Path:
        """Create zip archive of generated transcripts"""
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"transcripts_batch_{timestamp}.zip"
        zip_path = output_path / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_paths:
                file_path_obj = Path(file_path)
                if file_path_obj.exists():
                    zipf.write(file_path, file_path_obj.name)
        
        return zip_path
    
    def generate_session_batch(
        self,
        session_name: str,
        output_dir: str = "session_transcripts",
        layout: str = "official",
        **kwargs
    ) -> Dict[str, any]:
        """Generate transcripts for all students in a specific session"""
        
        try:
            session = Session.objects.get(name=session_name)
            enrollments = Enrollment.objects.filter(session=session)
            student_ids = list(enrollments.values_list('student__student_id', flat=True).distinct())
            
            return self.generate_batch_transcripts(
                student_ids=student_ids,
                output_dir=f"{output_dir}/{session_name}",
                layout=layout,
                **kwargs
            )
            
        except Session.DoesNotExist:
            return {
                'success': False,
                'error': f'Session "{session_name}" not found',
                'total_students': 0,
                'successful': 0,
                'failed': 0
            }
    
    def generate_level_batch(
        self,
        level_name: str,
        output_dir: str = "level_transcripts", 
        layout: str = "standard",
        **kwargs
    ) -> Dict[str, any]:
        """Generate transcripts for all students at a specific level"""
        
        students = Student.objects.filter(
            Q(entry_level__name=level_name) | Q(current_level__name=level_name)
        )
        
        student_ids = list(students.values_list('student_id', flat=True))
        
        return self.generate_batch_transcripts(
            student_ids=student_ids,
            output_dir=f"{output_dir}/{level_name}",
            layout=layout,
            **kwargs
        )


# NOTE: Batch transcript generation now relies on TranscriptGenerator's built-in
# security features (QR code + DB-backed verification records). Any placeholder
# security blocks that generated fake verification codes have been removed.


# Convenience functions for batch operations
def generate_all_transcripts(output_dir: str = "all_transcripts", layout: str = "standard") -> Dict:
    """Generate transcripts for all students"""
    batch_gen = BatchTranscriptGenerator()
    return batch_gen.generate_batch_transcripts(
        output_dir=output_dir,
        layout=layout,
        create_zip=True
    )


def generate_official_batch(student_ids: List[str], output_dir: str = "official_transcripts") -> Dict:
    """Generate official transcripts with watermarks for specified students"""
    batch_gen = BatchTranscriptGenerator('OFFICIAL_LAYOUT')
    return batch_gen.generate_batch_transcripts(
        student_ids=student_ids,
        output_dir=output_dir,
        layout="official",
        add_watermark=True,
        watermark_text="OFFICIAL",
        create_zip=True
    )


def generate_session_transcripts(session_name: str, layout: str = "detailed") -> Dict:
    """Generate transcripts for all students in a session"""
    batch_gen = BatchTranscriptGenerator()
    return batch_gen.generate_session_batch(
        session_name=session_name,
        layout=layout,
        add_watermark=True,
        watermark_text="CERTIFIED",
        create_zip=True
    )