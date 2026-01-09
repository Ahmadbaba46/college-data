import json

from django.test import TestCase, Client
from django.contrib.auth.models import User, Group

from students.models import Student, Level, Session
from courses.models import Course
from grading.models import Enrollment, Grade, GradingSettings
from reporting.security_features import verify_transcript_code
from reporting.transcript_generator import TranscriptGenerator


class TranscriptTamperEvidenceTest(TestCase):
    def setUp(self):
        self.level = Level.objects.create(name='100 Level')
        self.session = Session.objects.create(name='2023/2024')
        self.student = Student.objects.create(
            first_name='John',
            last_name='Doe',
            student_id='TAMP1',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.session,
        )
        self.course = Course.objects.create(code='CS201', title='Algo', units=3)
        from courses.models import CourseOffering
        offering = CourseOffering.objects.create(course=self.course, session=self.session, semester='FIRST')
        self.enrollment = Enrollment.objects.create(student=self.student, course_offering=offering)
        GradingSettings.objects.create(grade_name='A', min_score=90, max_score=100, grade_point=4.0)
        GradingSettings.objects.create(grade_name='F', min_score=0, max_score=59, grade_point=0.0)
        Grade.objects.create(enrollment=self.enrollment, ca_score=20, exam_score=70)  # 90

    def test_tamper_detection(self):
        gen = TranscriptGenerator('OFFICIAL_LAYOUT')
        result = gen.generate_transcript(
            self.student.student_id,
            'tmp/tmp_tamper.pdf',
            {'add_security_features': True},
            return_security_data=True,
            create_transcript_record=False,
        )
        self.assertTrue(result['success'], msg=result.get('error'))
        code = result['security_data']['verification_code']

        # Simulate tampering by modifying stored canonical payload in DB
        from reporting.models import TranscriptVerificationRecord
        rec = TranscriptVerificationRecord.objects.get(verification_code=code)
        payload = dict(rec.payload_json)
        payload['canonical_payload']['student']['last_name'] = 'HACKED'
        rec.payload_json = payload
        rec.save(update_fields=['payload_json'])

        verify = verify_transcript_code(code)
        self.assertFalse(verify['valid'])
        self.assertIn('possible tampering', verify.get('error', '').lower())


class TranscriptApiRBACTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.level = Level.objects.create(name='100 Level')
        self.session = Session.objects.create(name='2023/2024')
        self.student = Student.objects.create(
            first_name='John',
            last_name='Doe',
            student_id='API1',
            entry_level=self.level,
            current_level=self.level,
            current_session=self.session,
        )

    def test_api_requires_auth(self):
        resp = self.client.post('/transcripts/api/transcripts/', data=json.dumps({'student_id': 'API1'}), content_type='application/json')
        self.assertEqual(resp.status_code, 401)

    def test_api_requires_role(self):
        u = User.objects.create_user(username='nope', password='pass')
        self.client.login(username='nope', password='pass')
        resp = self.client.post('/transcripts/api/transcripts/', data=json.dumps({'student_id': 'API1'}), content_type='application/json')
        self.assertEqual(resp.status_code, 403)

    def test_api_allows_dataentry(self):
        u = User.objects.create_user(username='de', password='pass')
        g, _ = Group.objects.get_or_create(name='DataEntry')
        u.groups.add(g)
        self.client.login(username='de', password='pass')

        resp = self.client.post('/transcripts/api/transcripts/', data=json.dumps({'student_id': 'API1', 'layout': 'simple'}), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertTrue(body['success'])
        self.assertIn('transcript_record_id', body['data'])
