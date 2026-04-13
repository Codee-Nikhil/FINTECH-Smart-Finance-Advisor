from flask import Blueprint, make_response, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Budget, Goal
from datetime import datetime
import io

pdf_bp = Blueprint('pdf', __name__)


def draw_text(lines, x, y, size=12, bold=False):
    """Helper to generate PDF text stream commands."""
    out = []
    out.append(f"BT")
    out.append(f"/{'F2' if bold else 'F1'} {size} Tf")
    out.append(f"{x} {y} Td")
    for i, line in enumerate(lines):
        safe = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        if i == 0:
            out.append(f"({safe}) Tj")
        else:
            out.append(f"0 -{size+4} Td")
            out.append(f"({safe}) Tj")
    out.append("ET")
    return '\n'.join(out)


@pdf_bp.route('/report', methods=['GET'])
@jwt_required()
def generate_report():
    user_id = int(get_jwt_identity())
    month   = request.args.get('month', datetime.now().strftime('%B'))
    year    = int(request.args.get('year', datetime.now().year))

    user   = User.query.get_or_404(user_id)
    budget = Budget.query.filter_by(user_id=user_id, month=month, year=year).first()
    goals  = Goal.query.filter_by(user_id=user_id).all()

    income    = budget.income if budget else 0
    expenses  = budget.expenses if budget else []
    total_exp = sum(e.actual for e in expenses)
    savings   = income - total_exp
    rate      = round((savings / income) * 100, 1) if income else 0

    # Build PDF manually (no external library needed)
    now = datetime.now().strftime('%d %B %Y')

    # Content stream
    content_lines = []

    # Header
    content_lines.append("BT /F2 24 Tf 50 780 Td (FinTech Financial Report) Tj ET")
    content_lines.append("BT /F1 12 Tf 50 758 Td (Generated on: " + now + ") Tj ET")
    content_lines.append("BT /F1 12 Tf 50 742 Td (Name: " + user.name + "   |   Period: " + month + " " + str(year) + ") Tj ET")

    # Divider line
    content_lines.append("0.8 0.8 0.8 RG 50 730 m 545 730 l S")

    # Summary section
    content_lines.append("BT /F2 14 Tf 50 710 Td (Financial Summary) Tj ET")
    content_lines.append(f"BT /F1 12 Tf 50 690 Td (Monthly Income:       Rs. {income:,.0f}) Tj ET")
    content_lines.append(f"BT /F1 12 Tf 50 672 Td (Total Expenses:       Rs. {total_exp:,.0f}) Tj ET")
    content_lines.append(f"BT /F1 12 Tf 50 654 Td (Monthly Savings:      Rs. {savings:,.0f}) Tj ET")
    content_lines.append(f"BT /F1 12 Tf 50 636 Td (Savings Rate:         {rate}%) Tj ET")

    # Divider
    content_lines.append("0.8 0.8 0.8 RG 50 624 m 545 624 l S")

    # Expense breakdown
    content_lines.append("BT /F2 14 Tf 50 606 Td (Expense Breakdown) Tj ET")
    content_lines.append("BT /F2 11 Tf 50 588 Td (Category) Tj ET")
    content_lines.append("BT /F2 11 Tf 300 588 Td (Actual) Tj ET")
    content_lines.append("BT /F2 11 Tf 400 588 Td (Budget) Tj ET")
    content_lines.append("BT /F2 11 Tf 480 588 Td (Status) Tj ET")

    y = 570
    for e in expenses:
        if e.actual > 0 or e.budget_amt > 0:
            status = 'Over' if e.budget_amt and e.actual > e.budget_amt else ('OK' if e.budget_amt else '-')
            cat = e.category[:28]
            safe_cat = cat.replace('(', '\\(').replace(')', '\\)')
            content_lines.append(f"BT /F1 10 Tf 50 {y} Td ({safe_cat}) Tj ET")
            content_lines.append(f"BT /F1 10 Tf 300 {y} Td (Rs. {e.actual:,.0f}) Tj ET")
            content_lines.append(f"BT /F1 10 Tf 400 {y} Td (Rs. {e.budget_amt:,.0f}) Tj ET")
            content_lines.append(f"BT /F1 10 Tf 480 {y} Td ({status}) Tj ET")
            y -= 16
            if y < 200:
                break

    # Divider
    content_lines.append(f"0.8 0.8 0.8 RG 50 {y-4} m 545 {y-4} l S")
    y -= 22

    # Goals section
    content_lines.append(f"BT /F2 14 Tf 50 {y} Td (Financial Goals) Tj ET")
    y -= 18
    for g in goals:
        pct = round((g.saved / g.target) * 100, 1) if g.target else 0
        safe_name = g.name.replace('(', '\\(').replace(')', '\\)')
        content_lines.append(f"BT /F1 10 Tf 50 {y} Td ({safe_name}: Rs. {g.saved:,.0f} of Rs. {g.target:,.0f}  ({pct}% complete)) Tj ET")
        y -= 16
        if y < 80:
            break

    # Footer
    content_lines.append("0.8 0.8 0.8 RG 50 60 m 545 60 l S")
    content_lines.append("BT /F1 9 Tf 50 45 Td (FinTech Smart Finance Advisor  |  This report is for personal use only.) Tj ET")

    content_stream = '\n'.join(content_lines)
    stream_bytes   = content_stream.encode('latin-1', errors='replace')
    stream_len     = len(stream_bytes)

    # Assemble minimal valid PDF
    pdf_parts = []
    pdf_parts.append(b'%PDF-1.4\n')

    offsets = []

    # Object 1 — catalog
    offsets.append(len(b''.join(pdf_parts)))
    pdf_parts.append(b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n')

    # Object 2 — pages
    offsets.append(len(b''.join(pdf_parts)))
    pdf_parts.append(b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n')

    # Object 3 — page
    offsets.append(len(b''.join(pdf_parts)))
    pdf_parts.append(b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842]\n'
                     b'   /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>\nendobj\n')

    # Object 4 — content stream
    offsets.append(len(b''.join(pdf_parts)))
    stream_header = f'4 0 obj\n<< /Length {stream_len} >>\nstream\n'.encode()
    pdf_parts.append(stream_header)
    pdf_parts.append(stream_bytes)
    pdf_parts.append(b'\nendstream\nendobj\n')

    # Object 5 — font Helvetica
    offsets.append(len(b''.join(pdf_parts)))
    pdf_parts.append(b'5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n')

    # Object 6 — font Helvetica-Bold
    offsets.append(len(b''.join(pdf_parts)))
    pdf_parts.append(b'6 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n')

    # xref
    xref_offset = len(b''.join(pdf_parts))
    xref = ['xref', f'0 {len(offsets)+1}', '0000000000 65535 f ']
    for o in offsets:
        xref.append(f'{o:010d} 00000 n ')
    xref_str = '\n'.join(xref) + '\n'

    pdf_parts.append(xref_str.encode())
    pdf_parts.append(f'trailer\n<< /Size {len(offsets)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n'.encode())

    pdf_bytes = b''.join(pdf_parts)

    filename = f"FinTech_Report_{month}_{year}.pdf"
    response = make_response(pdf_bytes)
    response.headers['Content-Type']        = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
