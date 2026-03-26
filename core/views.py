import uuid
import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .utils.pdf_extractor import extract_text_from_file, extract_text_from_string
from .utils.ai_scorer import analyze_resume
from .utils.pdf_generator import generate_resume_pdf


def index(request):
    """Main web dashboard."""
    return render(request, 'index.html')


@csrf_exempt
@require_http_methods(["POST"])
def score_resume(request):
    """
    POST /api/score/
    Accepts JD (file or text) + Resume (file or text).
    Returns ATS analysis JSON.
    """
    try:
        # Extract JD text
        jd_text = ""
        if 'jd_file' in request.FILES:
            jd_file = request.FILES['jd_file']
            jd_text = extract_text_from_file(jd_file, jd_file.name)
        elif request.POST.get('jd_text'):
            jd_text = extract_text_from_string(request.POST.get('jd_text'))

        # Extract Resume text
        resume_text = ""
        if 'resume_file' in request.FILES:
            resume_file = request.FILES['resume_file']
            resume_text = extract_text_from_file(resume_file, resume_file.name)
        elif request.POST.get('resume_text'):
            resume_text = extract_text_from_string(request.POST.get('resume_text'))

        if not jd_text:
            return JsonResponse({'error': 'Job Description is required.'}, status=400)
        if not resume_text:
            return JsonResponse({'error': 'Resume is required.'}, status=400)

        # Run AI analysis
        result = analyze_resume(jd_text, resume_text)

        # Store in session for PDF download
        session_id = str(uuid.uuid4())
        request.session[session_id] = {
            'optimized_resume': result.get('optimized_resume'),
            'jd_text': jd_text[:500],
        }
        result['session_id'] = session_id
        result['status'] = 'success'

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'error': str(e), 'status': 'error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_pdf(request):
    """
    POST /api/generate-pdf/
    Body: { session_id, template: 'modern'|'corporate', resume_data (optional override) }
    Returns PDF file as download.
    """
    try:
        body = json.loads(request.body)
        template = body.get('template', 'modern')
        resume_data = body.get('resume_data')

        # If resume_data not provided, try session
        if not resume_data:
            session_id = body.get('session_id', '')
            session_data = request.session.get(session_id, {})
            resume_data = session_data.get('optimized_resume')

        if not resume_data:
            return JsonResponse({'error': 'No resume data found. Please run analysis first.'}, status=400)

        # Generate PDF
        pdf_bytes = generate_resume_pdf(resume_data, template=template)

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f"optimized_resume_{template}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_pdf_direct(request):
    """
    POST /api/generate-pdf-direct/
    Used by the bot — accepts resume_data JSON directly.
    """
    try:
        body = json.loads(request.body)
        template = body.get('template', 'modern')
        resume_data = body.get('resume_data', {})

        if not resume_data:
            return JsonResponse({'error': 'resume_data is required'}, status=400)

        pdf_bytes = generate_resume_pdf(resume_data, template=template)

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="optimized_resume.pdf"'
        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
