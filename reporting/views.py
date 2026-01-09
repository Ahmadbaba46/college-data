"""
Web Views for Transcript Verification and API Endpoints
======================================================

This module provides:
1. Web-based transcript verification portal
2. REST API endpoints for external systems
3. Transcript generation web interface
4. Security verification services
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
from django.conf import settings
import json
import os
from datetime import datetime
import mimetypes

from students.models import Student, Session
from grading.models import Enrollment
from configuration.models import CollegeSettings
from .security_features import verify_transcript_code, SecureTranscriptFeatures
from .transcript_generator import TranscriptGenerator
from .batch_transcript_generator import BatchTranscriptGenerator


class TranscriptVerificationView(View):
    """Web portal for verifying transcript authenticity"""
    
    def get(self, request):
        """Display verification form or process verification"""
        verification_code = request.GET.get('code')
        
        if verification_code:
            # Process verification
            result = verify_transcript_code(verification_code)
            return render(request, 'reporting/verification_result.html', {
                'verification_code': verification_code,
                'result': result
            })
        
        # Show verification form
        return render(request, 'reporting/verification_form.html')
    
    def post(self, request):
        """Handle form submission for verification"""
        verification_code = request.POST.get('verification_code', '').strip().upper()
        
        if not verification_code:
            return render(request, 'reporting/verification_form.html', {
                'error': 'Please enter a verification code'
            })
        
        result = verify_transcript_code(verification_code)
        return render(request, 'reporting/verification_result.html', {
            'verification_code': verification_code,
            'result': result
        })


@method_decorator(csrf_exempt, name='dispatch')
class TranscriptAPIView(View):
    """REST API endpoints for transcript operations"""
    
    def get(self, request, student_id=None):
        """Get transcript information or list transcripts"""
        
        if student_id:
            # Get specific student transcript info
            try:
                student = Student.objects.get(student_id=student_id)
                enrollments = Enrollment.objects.filter(student=student)
                
                transcript_info = {
                    'student_id': student.student_id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'entry_level': student.entry_level.name if student.entry_level else None,
                    'current_level': student.current_level.name if student.current_level else None,
                    'current_session': student.current_session.name if student.current_session else None,
                    'enrollments_count': enrollments.count(),
                    'available_layouts': ['standard', 'detailed', 'official', 'simple']
                }
                
                return JsonResponse({
                    'success': True,
                    'data': transcript_info
                })
                
            except Student.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Student with ID {student_id} not found'
                }, status=404)
        
        else:
            # List all students available for transcript generation
            students = Student.objects.all()[:50]  # Limit for performance
            
            student_list = [{
                'student_id': s.student_id,
                'student_name': f"{s.first_name} {s.last_name}",
                'entry_level': s.entry_level.name if s.entry_level else None
            } for s in students]
            
            return JsonResponse({
                'success': True,
                'data': student_list,
                'total_count': Student.objects.count()
            })
    
    def post(self, request, student_id=None):
        """Generate transcript via API"""

        # RBAC: require authentication and Admin/DataEntry role
        from users.permissions import user_in_groups
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        if not user_in_groups(request.user, ['Admin', 'DataEntry']):
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

        try:
            # Parse request data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            if not student_id:
                student_id = data.get('student_id')
            
            if not student_id:
                return JsonResponse({
                    'success': False,
                    'error': 'student_id is required'
                }, status=400)
            
            # Validate student exists
            try:
                student = Student.objects.get(student_id=student_id)
            except Student.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Student with ID {student_id} not found'
                }, status=404)
            
            # Extract generation parameters
            layout = data.get('layout', 'standard')
            add_watermark = data.get('add_watermark', False)
            watermark_text = data.get('watermark_text', 'OFFICIAL')
            add_security = data.get('add_security_features', True)
            
            # Generate transcript
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{student_id}_{layout}_{timestamp}.pdf"
            file_path = os.path.join('api_transcripts', filename)
            
            # Create directory if it doesn't exist
            os.makedirs('api_transcripts', exist_ok=True)
            
            # Configure transcript generation
            layout_map = {
                'standard': 'STANDARD_LAYOUT',
                'detailed': 'DETAILED_LAYOUT',
                'official': 'OFFICIAL_LAYOUT',
                'simple': 'SIMPLE_LAYOUT'
            }
            
            generator = TranscriptGenerator(layout_map.get(layout, 'STANDARD_LAYOUT'))
            
            config = {
                'add_watermark': add_watermark,
                'watermark_text': watermark_text,
                'add_security_features': add_security,
                'show_certification': layout in ['official', 'detailed'],
                'show_signatures': layout in ['official', 'detailed']
            }
            
            result = generator.generate_transcript(
                student_id,
                file_path,
                config,
                generated_by=request.user,
                layout_name=layout,
            )

            success = bool(result) if not isinstance(result, dict) else bool(result.get('success'))

            if success:
                # Get file info
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                
                response_data = {
                    'success': True,
                    'data': {
                        'student_id': student_id,
                        'student_name': f"{student.first_name} {student.last_name}",
                        'layout': layout,
                        'filename': filename,
                        'file_path': file_path,
                        'file_size_bytes': file_size,
                        'generated_at': datetime.now().isoformat(),
                        'download_url': f'/api/transcripts/download/{filename}',
                        'security_features': add_security,
                        'transcript_record_id': (result.get('transcript_id') if isinstance(result, dict) else None)
                    }
                }
                
                return JsonResponse(response_data, status=201)
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to generate transcript'
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Internal server error: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class VerificationAPIView(View):
    """API endpoint for transcript verification"""
    
    def get(self, request, verification_code=None):
        """Verify transcript using verification code"""
        
        if not verification_code:
            verification_code = request.GET.get('code')
        
        if not verification_code:
            return JsonResponse({
                'success': False,
                'error': 'Verification code is required'
            }, status=400)
        
        try:
            result = verify_transcript_code(verification_code)
            
            return JsonResponse({
                'success': True,
                'verification_code': verification_code,
                'verification_result': result
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Verification failed: {str(e)}'
            }, status=500)


def download_transcript(request, filename):
    """Download generated transcript file"""

    # RBAC: require authentication and Admin/DataEntry role
    from users.permissions import user_in_groups
    if not request.user.is_authenticated:
        raise Http404("Not found")
    if not user_in_groups(request.user, ['Admin', 'DataEntry']):
        raise Http404("Not found")
    
    file_path = os.path.join('api_transcripts', filename)
    
    if not os.path.exists(file_path):
        raise Http404("Transcript file not found")
    
    # Security check - ensure filename doesn't contain path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise Http404("Invalid filename")
    
    # Open and serve file
    with open(file_path, 'rb') as f:
        content = f.read()
    
    content_type, _ = mimetypes.guess_type(file_path)
    response = HttpResponse(content, content_type=content_type or 'application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def transcript_generate(request):
    """Web UI for generating individual transcripts"""
    from users.permissions import user_in_groups
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.http import FileResponse
    
    # RBAC check
    if not request.user.is_authenticated or not user_in_groups(request.user, ['Admin', 'DataEntry']):
        raise Http404("Not found")
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        layout = request.POST.get('layout', 'standard')
        
        try:
            student = Student.objects.get(student_id=student_id)
            
            # Map layout name to layout config
            layout_map = {
                'standard': 'STANDARD_LAYOUT',
                'detailed': 'DETAILED_LAYOUT',
                'official': 'OFFICIAL_LAYOUT',
                'simple': 'SIMPLE_LAYOUT',
            }
            layout_config = layout_map.get(layout, 'STANDARD_LAYOUT')
            
            # Generate transcript
            generator = TranscriptGenerator(layout_config=layout_config)
            output_dir = 'api_transcripts'
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f'transcript_{layout}_{student_id}_{timestamp}.pdf')
            
            result = generator.generate_transcript(student_id, output_file)
            
            if result.get('success'):
                messages.success(request, f'Transcript generated successfully for {student.full_name}')
                
                # Store in database
                from reporting.models import Transcript
                Transcript.objects.create(
                    student=student,
                    layout=layout,
                    output_file=output_file,
                    generated_by=request.user
                )
                
                # Offer download
                if os.path.exists(output_file):
                    response = FileResponse(
                        open(output_file, 'rb'),
                        as_attachment=True,
                        filename=os.path.basename(output_file)
                    )
                    response['Content-Type'] = 'application/pdf'
                    return response
                else:
                    messages.error(request, 'Transcript file not found after generation.')
                    return redirect('reporting:transcript_generate')
            else:
                messages.error(request, f'Failed to generate transcript: {result.get("error")}')
                
        except Student.DoesNotExist:
            messages.error(request, f'Student with ID {student_id} not found.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('reporting:transcript_generate')
    
    # GET request - show form
    students = Student.objects.all().order_by('student_id')
    
    ctx = {
        'students': students,
    }
    
    return render(request, 'reporting/transcript_generate.html', ctx)


def transcript_batch(request):
    """Web UI for batch transcript generation"""
    from users.permissions import user_in_groups
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.http import FileResponse
    from students.models import Level
    
    # RBAC check
    if not request.user.is_authenticated or not user_in_groups(request.user, ['Admin', 'DataEntry']):
        raise Http404("Not found")
    
    if request.method == 'POST':
        generation_type = request.POST.get('generation_type')
        layout = request.POST.get('layout', 'standard')
        
        try:
            # Map layout name to layout config
            layout_map = {
                'standard': 'STANDARD_LAYOUT',
                'detailed': 'DETAILED_LAYOUT',
                'official': 'OFFICIAL_LAYOUT',
                'simple': 'SIMPLE_LAYOUT',
            }
            layout_config = layout_map.get(layout, 'STANDARD_LAYOUT')
            
            batch_gen = BatchTranscriptGenerator(layout_config=layout_config)
            
            if generation_type == 'all':
                result = batch_gen.generate_batch_transcripts()
                
            elif generation_type == 'session':
                session_id = request.POST.get('session_id')
                session = Session.objects.get(id=session_id)
                student_ids = list(
                    Student.objects.filter(current_session=session)
                    .values_list('student_id', flat=True)
                )
                result = batch_gen.generate_batch_transcripts(student_ids=student_ids)
                
            elif generation_type == 'level':
                level_id = request.POST.get('level_id')
                level = Level.objects.get(id=level_id)
                student_ids = list(
                    Student.objects.filter(current_level=level)
                    .values_list('student_id', flat=True)
                )
                result = batch_gen.generate_batch_transcripts(student_ids=student_ids)
                
            elif generation_type == 'selected':
                student_ids = request.POST.getlist('student_ids')
                result = batch_gen.generate_batch_transcripts(student_ids=student_ids)
            
            else:
                messages.error(request, 'Invalid generation type.')
                return redirect('reporting:transcript_batch')
            
            # Show results
            success_count = result.get('successful', 0)
            error_count = len(result.get('errors', []))
            
            if success_count > 0:
                messages.success(request, f'Successfully generated {success_count} transcript(s).')
            if error_count > 0:
                messages.warning(request, f'{error_count} error(s) occurred.')
            
            # If zip file created, offer download
            if result.get('zip_file'):
                return FileResponse(
                    open(result['zip_file'], 'rb'),
                    as_attachment=True,
                    filename=os.path.basename(result['zip_file'])
                )
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('reporting:transcript_batch')
    
    # GET request
    students = Student.objects.all().order_by('student_id')
    sessions = Session.objects.all().order_by('-name')
    levels = Level.objects.all().order_by('name')
    
    ctx = {
        'students': students,
        'sessions': sessions,
        'levels': levels,
    }
    
    return render(request, 'reporting/transcript_batch.html', ctx)


def transcript_history(request):
    """View transcript generation history"""
    from users.permissions import user_in_groups
    
    # RBAC check
    if not request.user.is_authenticated:
        raise Http404("Not found")
    
    from reporting.models import Transcript
    
    # Filter options
    student_id = request.GET.get('student_id')
    layout_filter = request.GET.get('layout')
    
    records = Transcript.objects.select_related(
        'student', 'generated_by'
    ).order_by('-created_at')
    
    if student_id:
        records = records.filter(student__student_id=student_id)
    if layout_filter:
        records = records.filter(layout=layout_filter)
    
    # Limit to recent 100
    records = records[:100]
    
    ctx = {
        'records': records,
        'selected_student_id': student_id,
        'selected_layout': layout_filter,
    }
    
    return render(request, 'reporting/transcript_history.html', ctx)