"""
PDF Report Generation Service for CareerPath Ghana.
Generates styled tertiary academic eligibility reports using ReportLab.
"""

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_eligibility_report_pdf(data: dict) -> bytes:
    """
    Builds a professional 1-2 page academic eligibility report PDF.
    
    Expected keys in `data`:
        - student_name: str (optional)
        - aggregate: int
        - label: str (e.g. 'Outstanding', 'Excellent')
        - is_awaiting: bool
        - core_grades: dict (e.g. {'English Language': 2, ...})
        - electives: list of dicts [{'name': 'Physics', 'grade': 2}, ...]
        - eligible_programs: list of dicts [{'program_name': ..., 'university_short': ..., 'cutoff': ..., 'user_aggregate': ...}]
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=TA_LEFT
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#475569'),
        alignment=TA_LEFT
    )

    section_heading = ParagraphStyle(
        'SecHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    table_header = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("CareerPath Ghana", title_style))
    story.append(Paragraph("Tertiary Academic Eligibility & Admissions Report", subtitle_style))
    story.append(Spacer(1, 4))
    
    report_date = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    story.append(Paragraph(f"Generated on {report_date} | Official Student Assessment", body_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceAfter=15))

    # 2. Student Summary Card
    is_awaiting = data.get('is_awaiting', False)
    aggregate = data.get('aggregate')
    label = data.get('label', 'Assessment Result')
    student_name = data.get('student_name', 'Student Candidate')

    if is_awaiting:
        agg_display = "Awaiting Results"
        status_text = "Subject Track Evaluation Active"
    else:
        agg_display = f"Aggregate {aggregate}" if aggregate is not None else "N/A"
        status_text = f"Performance Rating: {label}"

    summary_data = [
        [
            Paragraph(f"<b>Candidate:</b> {student_name}", body_style),
            Paragraph(f"<b>WASSCE Status:</b> {agg_display}", body_style),
            Paragraph(f"<b>Rating:</b> {label}", body_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[200, 160, 170])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 16))

    # 3. WASSCE Grades Table
    core_grades = data.get('core_grades', {})
    electives = data.get('electives', [])

    story.append(Paragraph("Verified WASSCE / SSSCE Subject Profile", section_heading))
    
    grade_rows = [[Paragraph("Subject", table_header), Paragraph("Category", table_header), Paragraph("Grade Value", table_header)]]
    
    for subj, grd in core_grades.items():
        grd_val = f"Grade {grd}" if not is_awaiting else "Pending"
        grade_rows.append([
            Paragraph(str(subj), body_style),
            Paragraph("Core Subject", body_style),
            Paragraph(grd_val, body_style)
        ])
    
    for el in electives:
        sub_name = el.get('name') or el.get('subject') or 'Elective'
        grd = el.get('grade')
        grd_val = f"Grade {grd}" if (grd and not is_awaiting) else "Pending"
        grade_rows.append([
            Paragraph(str(sub_name), body_style),
            Paragraph("Elective Subject", body_style),
            Paragraph(grd_val, body_style)
        ])

    grade_table = Table(grade_rows, colWidths=[260, 140, 130])
    grade_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(grade_table)
    story.append(Spacer(1, 18))

    # 4. Qualified Programs Table
    eligible_progs = data.get('eligible_programs', [])
    story.append(Paragraph(f"Qualified & Borderline University Degree Programs ({len(eligible_progs)} Available)", section_heading))

    if not eligible_progs:
        story.append(Paragraph("No qualified degree programs matched this subject combination. Try running the What-If Simulator to explore pathways.", body_style))
    else:
        prog_rows = [
            [
                Paragraph("Degree Program", table_header),
                Paragraph("University", table_header),
                Paragraph("Cut-Off", table_header),
                Paragraph("Your Aggregate", table_header),
                Paragraph("Status", table_header)
            ]
        ]

        for p in eligible_progs[:40]:  # Up to top 40 programs
            p_name = p.get('program_name') or p.get('name', '')
            uni = p.get('university_short') or p.get('university_name', '')
            cutoff = str(p.get('cutoff', 'N/A'))
            user_agg = str(p.get('user_aggregate', 'N/A'))
            is_elig = p.get('is_eligible', True)
            is_bord = p.get('is_borderline', False)
            status = "Direct Qualified" if is_elig else ("Borderline" if is_bord else "Near Miss")

            prog_rows.append([
                Paragraph(p_name, body_style),
                Paragraph(uni, body_style),
                Paragraph(cutoff, body_style),
                Paragraph(user_agg, body_style),
                Paragraph(status, body_style)
            ])

        prog_table = Table(prog_rows, colWidths=[200, 75, 75, 80, 100])
        prog_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#059669')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        story.append(prog_table)

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=8))
    story.append(Paragraph("CareerPath Ghana Admissions Advisory | https://careerpath.onrender.com | Powered by Ministry & University Cut-Off Standards", subtitle_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

