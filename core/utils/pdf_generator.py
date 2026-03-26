"""
PDF Generator using ReportLab.
Generates professional resume PDFs in two templates:
  1. Modern Clean (1-page) - Navy/White design
  2. Corporate Professional (2-page) - Classic black/gray
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ──────────────────────────────── COLOR PALETTES ────────────────────────────── #

NAVY = colors.HexColor('#1a2980')
NAVY_LIGHT = colors.HexColor('#26d0ce')
ACCENT = colors.HexColor('#00b4d8')
DARK = colors.HexColor('#1a1a2e')
GRAY = colors.HexColor('#555555')
LIGHT_GRAY = colors.HexColor('#f0f0f0')
WHITE = colors.white
BLACK = colors.black
GREEN_ACCENT = colors.HexColor('#00c896')

CORP_DARK = colors.HexColor('#1c1c1c')
CORP_GRAY = colors.HexColor('#4a4a4a')
CORP_LINE = colors.HexColor('#cccccc')


# ──────────────────────────────── PAGE DIMENSIONS ───────────────────────────── #

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 1.5 * cm
RIGHT_MARGIN = 1.5 * cm
TOP_MARGIN = 1.5 * cm
BOTTOM_MARGIN = 1.5 * cm


def _safe_str(val, default=""):
    """Convert any value to a safe, non-None string."""
    if val is None:
        return default
    return str(val).strip()


def _safe_list(val):
    """Ensure value is a list."""
    if isinstance(val, list):
        return val
    if val:
        return [str(val)]
    return []


# ═══════════════════════════════════════════════════════════════════════════════
#  TEMPLATE 1: MODERN CLEAN (1-PAGE, NAVY GRADIENT HEADER)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_modern_pdf(resume_data):
    """
    Generate a modern, ATS-friendly 1-page resume PDF.
    Navy header bar, clean sections, strong typographic hierarchy.
    Returns PDF as bytes.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title=f"Resume - {_safe_str(resume_data.get('name', 'Candidate'))}",
    )

    styles = _modern_styles()
    story = []

    # ── HEADER ──────────────────────────────────────────────────────────────── #
    name = _safe_str(resume_data.get('name', 'Your Name'))
    contact = _safe_str(resume_data.get('contact', 'email@example.com'))

    header_data = [
        [Paragraph(f'<font color="white"><b>{name}</b></font>', styles['header_name'])],
        [Paragraph(f'<font color="#90e0ef">{contact}</font>', styles['header_contact'])],
    ]
    header_table = Table(header_data, colWidths=[PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # ── SUMMARY ─────────────────────────────────────────────────────────────── #
    summary = _safe_str(resume_data.get('summary', ''))
    if summary:
        story.append(_section_header('PROFESSIONAL SUMMARY', styles))
        story.append(Paragraph(summary, styles['body']))
        story.append(Spacer(1, 6))

    # ── SKILLS ──────────────────────────────────────────────────────────────── #
    skills = resume_data.get('skills', {})
    if skills:
        story.append(_section_header('TECHNICAL SKILLS', styles))
        skills_lines = []
        skill_map = {
            'languages': '💻 Languages',
            'frameworks': '🔧 Frameworks',
            'tools': '🛠 Tools',
            'databases': '🗄 Databases',
        }
        if isinstance(skills, dict):
            for key, label in skill_map.items():
                vals = skills.get(key, [])
                if vals:
                    val_str = ', '.join(_safe_list(vals))
                    skills_lines.append(f'<b>{label}:</b>  {val_str}')
            # Any extra keys
            for key, val in skills.items():
                if key not in skill_map and val:
                    skills_lines.append(f'<b>{key.title()}:</b>  {", ".join(_safe_list(val))}')
        elif isinstance(skills, list):
            skills_lines.append(', '.join(skills))
        elif isinstance(skills, str):
            skills_lines.append(skills)

        for line in skills_lines:
            story.append(Paragraph(line, styles['body']))
        story.append(Spacer(1, 6))

    # ── EXPERIENCE ──────────────────────────────────────────────────────────── #
    experience = _safe_list(resume_data.get('experience', []))
    if experience:
        story.append(_section_header('PROFESSIONAL EXPERIENCE', styles))
        for exp in experience:
            if not isinstance(exp, dict):
                story.append(Paragraph(_safe_str(exp), styles['body']))
                story.append(Spacer(1, 4))
                continue
            title = _safe_str(exp.get('title', ''))
            company = _safe_str(exp.get('company', ''))
            duration = _safe_str(exp.get('duration', ''))

            if title or company:
                exp_header = Table(
                    [[
                        Paragraph(f'<b>{title}</b> — {company}', styles['job_title']),
                        Paragraph(duration, styles['date']),
                    ]],
                    colWidths=[
                        (PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN) * 0.72,
                        (PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN) * 0.28,
                    ]
                )
                exp_header.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(exp_header)

            bullets = _safe_list(exp.get('bullets', []))
            for bullet in bullets:
                story.append(Paragraph(f'• {_safe_str(bullet)}', styles['bullet']))
            story.append(Spacer(1, 4))

    # ── PROJECTS ────────────────────────────────────────────────────────────── #
    projects = _safe_list(resume_data.get('projects', []))
    if projects:
        story.append(_section_header('PROJECTS', styles))
        for proj in projects:
            if not isinstance(proj, dict):
                story.append(Paragraph(_safe_str(proj), styles['body']))
                story.append(Spacer(1, 4))
                continue
            name_p = _safe_str(proj.get('name', ''))
            tech = _safe_str(proj.get('tech', ''))
            if name_p:
                story.append(Paragraph(
                    f'<b>{name_p}</b>' + (f'  <font color="#555555" size="9">| {tech}</font>' if tech else ''),
                    styles['job_title']
                ))
            bullets = _safe_list(proj.get('bullets', []))
            for bullet in bullets:
                story.append(Paragraph(f'• {_safe_str(bullet)}', styles['bullet']))
            story.append(Spacer(1, 4))

    # ── EDUCATION ───────────────────────────────────────────────────────────── #
    education = resume_data.get('education', '')
    if education:
        story.append(_section_header('EDUCATION', styles))
        if isinstance(education, list):
            for edu in education:
                story.append(Paragraph(f'• {_safe_str(edu)}', styles['body']))
        else:
            story.append(Paragraph(_safe_str(education), styles['body']))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def _section_header(title, styles):
    """Returns a navy section header line."""
    return KeepTogether([
        Paragraph(title, styles['section_header']),
        HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceAfter=4),
    ])


def _modern_styles():
    styles = getSampleStyleSheet()
    return {
        'header_name': ParagraphStyle(
            'HeaderName', fontSize=22, fontName='Helvetica-Bold',
            alignment=TA_CENTER, textColor=WHITE, spaceAfter=2,
        ),
        'header_contact': ParagraphStyle(
            'HeaderContact', fontSize=9, fontName='Helvetica',
            alignment=TA_CENTER, textColor=WHITE,
        ),
        'section_header': ParagraphStyle(
            'SectionHeader', fontSize=11, fontName='Helvetica-Bold',
            textColor=NAVY, spaceBefore=8, spaceAfter=2,
            letterSpacing=1,
        ),
        'job_title': ParagraphStyle(
            'JobTitle', fontSize=10, fontName='Helvetica-Bold',
            textColor=DARK, spaceBefore=2,
        ),
        'date': ParagraphStyle(
            'Date', fontSize=9, fontName='Helvetica',
            textColor=GRAY, alignment=TA_RIGHT,
        ),
        'body': ParagraphStyle(
            'Body', fontSize=9.5, fontName='Helvetica',
            textColor=DARK, leading=14, spaceAfter=2,
        ),
        'bullet': ParagraphStyle(
            'Bullet', fontSize=9, fontName='Helvetica',
            textColor=DARK, leading=13, leftIndent=12, spaceAfter=1,
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  TEMPLATE 2: CORPORATE PROFESSIONAL (2-PAGE, CLASSIC BLACK/GRAY)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_corporate_pdf(resume_data):
    """
    Generate a classic 2-page corporate resume PDF.
    Clean black-and-white, ATS-friendly, professional.
    Returns PDF as bytes.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Resume - {_safe_str(resume_data.get('name', 'Candidate'))}",
    )

    styles = _corporate_styles()
    story = []

    # ── HEADER ──────────────────────────────────────────────────────────────── #
    name = _safe_str(resume_data.get('name', 'Your Name'))
    contact = _safe_str(resume_data.get('contact', ''))

    story.append(Paragraph(name.upper(), styles['corp_name']))
    if contact:
        story.append(Paragraph(contact, styles['corp_contact']))
    story.append(HRFlowable(width="100%", thickness=2, color=CORP_DARK, spaceBefore=6, spaceAfter=8))

    # ── SUMMARY ─────────────────────────────────────────────────────────────── #
    summary = _safe_str(resume_data.get('summary', ''))
    if summary:
        story.append(Paragraph('PROFESSIONAL SUMMARY', styles['corp_section']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=CORP_LINE, spaceAfter=4))
        story.append(Paragraph(summary, styles['corp_body']))
        story.append(Spacer(1, 8))

    # ── SKILLS ──────────────────────────────────────────────────────────────── #
    skills = resume_data.get('skills', {})
    if skills:
        story.append(Paragraph('CORE COMPETENCIES', styles['corp_section']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=CORP_LINE, spaceAfter=4))
        if isinstance(skills, dict):
            for key, val in skills.items():
                vals = _safe_list(val)
                if vals:
                    story.append(Paragraph(
                        f'<b>{key.title()}:</b> {", ".join(vals)}',
                        styles['corp_body']
                    ))
        elif isinstance(skills, list):
            story.append(Paragraph(', '.join(skills), styles['corp_body']))
        elif isinstance(skills, str):
            story.append(Paragraph(skills, styles['corp_body']))
        story.append(Spacer(1, 8))

    # ── EXPERIENCE ──────────────────────────────────────────────────────────── #
    experience = _safe_list(resume_data.get('experience', []))
    if experience:
        story.append(Paragraph('PROFESSIONAL EXPERIENCE', styles['corp_section']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=CORP_LINE, spaceAfter=4))
        for exp in experience:
            if not isinstance(exp, dict):
                story.append(Paragraph(_safe_str(exp), styles['corp_body']))
                story.append(Spacer(1, 4))
                continue
            title = _safe_str(exp.get('title', ''))
            company = _safe_str(exp.get('company', ''))
            duration = _safe_str(exp.get('duration', ''))
            full_width = PAGE_WIDTH - 4 * cm

            row = Table(
                [[
                    Paragraph(f'<b>{title}</b>  |  {company}', styles['corp_job']),
                    Paragraph(duration, styles['corp_date']),
                ]],
                colWidths=[full_width * 0.70, full_width * 0.30]
            )
            row.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(row)

            for bullet in _safe_list(exp.get('bullets', [])):
                story.append(Paragraph(f'▪ {_safe_str(bullet)}', styles['corp_bullet']))
            story.append(Spacer(1, 6))

    # ── PROJECTS ────────────────────────────────────────────────────────────── #
    projects = _safe_list(resume_data.get('projects', []))
    if projects:
        story.append(Paragraph('PROJECTS', styles['corp_section']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=CORP_LINE, spaceAfter=4))
        for proj in projects:
            if not isinstance(proj, dict):
                story.append(Paragraph(_safe_str(proj), styles['corp_body']))
                story.append(Spacer(1, 4))
                continue
            name_p = _safe_str(proj.get('name', ''))
            tech = _safe_str(proj.get('tech', ''))
            story.append(Paragraph(
                f'<b>{name_p}</b>' + (f' — <i>{tech}</i>' if tech else ''),
                styles['corp_job']
            ))
            for bullet in _safe_list(proj.get('bullets', [])):
                story.append(Paragraph(f'▪ {_safe_str(bullet)}', styles['corp_bullet']))
            story.append(Spacer(1, 4))

    # ── EDUCATION ───────────────────────────────────────────────────────────── #
    education = resume_data.get('education', '')
    if education:
        story.append(Paragraph('EDUCATION', styles['corp_section']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=CORP_LINE, spaceAfter=4))
        if isinstance(education, list):
            for edu in education:
                story.append(Paragraph(_safe_str(edu), styles['corp_body']))
        else:
            story.append(Paragraph(_safe_str(education), styles['corp_body']))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def _corporate_styles():
    styles = getSampleStyleSheet()
    return {
        'corp_name': ParagraphStyle(
            'CorpName', fontSize=20, fontName='Helvetica-Bold',
            alignment=TA_CENTER, textColor=CORP_DARK, spaceAfter=4,
        ),
        'corp_contact': ParagraphStyle(
            'CorpContact', fontSize=9, fontName='Helvetica',
            alignment=TA_CENTER, textColor=CORP_GRAY, spaceAfter=2,
        ),
        'corp_section': ParagraphStyle(
            'CorpSection', fontSize=10, fontName='Helvetica-Bold',
            textColor=CORP_DARK, spaceBefore=10, spaceAfter=2,
            letterSpacing=1.5,
        ),
        'corp_job': ParagraphStyle(
            'CorpJob', fontSize=10, fontName='Helvetica-Bold',
            textColor=CORP_DARK, spaceBefore=2, spaceAfter=1,
        ),
        'corp_date': ParagraphStyle(
            'CorpDate', fontSize=9, fontName='Helvetica',
            textColor=CORP_GRAY, alignment=TA_RIGHT,
        ),
        'corp_body': ParagraphStyle(
            'CorpBody', fontSize=9.5, fontName='Helvetica',
            textColor=CORP_GRAY, leading=14, spaceAfter=2,
        ),
        'corp_bullet': ParagraphStyle(
            'CorpBullet', fontSize=9, fontName='Helvetica',
            textColor=CORP_DARK, leading=13, leftIndent=14, spaceAfter=1,
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def generate_resume_pdf(resume_data, template='modern'):
    """
    Generate a resume PDF.
    
    Args:
        resume_data: dict with keys: name, contact, summary, skills, experience, projects, education
        template: 'modern' (1-page navy) or 'corporate' (2-page black/gray)
    
    Returns:
        bytes: PDF file content
    """
    if template == 'corporate':
        return generate_corporate_pdf(resume_data)
    else:
        return generate_modern_pdf(resume_data)
