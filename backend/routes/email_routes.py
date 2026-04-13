from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Budget, Goal
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

email_bp = Blueprint('email', __name__)


def send_email(to_email, subject, html_body):
    """Send email via Gmail SMTP."""
    smtp_user = os.getenv('EMAIL_USER', '')
    smtp_pass = os.getenv('EMAIL_PASS', '')

    if not smtp_user or not smtp_pass:
        raise Exception('Email credentials not configured in .env')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'FinTech <{smtp_user}>'
    msg['To']      = to_email
    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())


def build_report_email(user, budget, goals):
    """Build a beautiful HTML email report."""
    income    = budget.income if budget else 0
    expenses  = budget.expenses if budget else []
    total_exp = sum(e.actual for e in expenses)
    savings   = income - total_exp
    rate      = round((savings / income) * 100, 1) if income else 0
    month     = budget.month if budget else datetime.now().strftime('%B')
    year      = budget.year  if budget else datetime.now().year

    status_color = '#3ecf8e' if savings >= 0 else '#f06375'
    rate_color   = '#3ecf8e' if rate >= 20 else '#f5a623' if rate >= 10 else '#f06375'

    expense_rows = ''.join(
        f'''<tr>
              <td style="padding:8px 12px;color:#555;border-bottom:1px solid #f0f0f0">{e.category}</td>
              <td style="padding:8px 12px;text-align:right;font-weight:600;border-bottom:1px solid #f0f0f0">
                {'<span style="color:#f06375">' if e.budget_amt and e.actual > e.budget_amt else '<span>'}
                ₹{e.actual:,.0f}</span>
              </td>
              <td style="padding:8px 12px;text-align:right;color:#999;border-bottom:1px solid #f0f0f0">
                {'₹' + f'{e.budget_amt:,.0f}' if e.budget_amt else '—'}
              </td>
            </tr>'''
        for e in expenses if e.actual > 0
    )

    goal_rows = ''.join(
        f'''<tr>
              <td style="padding:8px 12px;color:#555;border-bottom:1px solid #f0f0f0">{g.name}</td>
              <td style="padding:8px 12px;text-align:right;border-bottom:1px solid #f0f0f0">
                <div style="background:#f0f0f0;border-radius:4px;height:8px;width:100%">
                  <div style="background:#7c6ff7;border-radius:4px;height:8px;width:{min(round((g.saved/g.target)*100),100)}%"></div>
                </div>
                <small style="color:#999">{round((g.saved/g.target)*100,1) if g.target else 0}% · ₹{g.saved:,.0f} of ₹{g.target:,.0f}</small>
              </td>
            </tr>'''
        for g in goals
    )

    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"/></head>
    <body style="margin:0;padding:0;background:#f5f5f5;font-family:Arial,sans-serif">
      <div style="max-width:600px;margin:30px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08)">

        <!-- Header -->
        <div style="background:linear-gradient(135deg,#7c6ff7,#5b8df8);padding:32px;text-align:center">
          <div style="font-size:32px;font-weight:800;color:#fff;letter-spacing:-1px">FinTech ₹</div>
          <div style="color:rgba(255,255,255,0.8);margin-top:6px;font-size:14px">Monthly Financial Report — {month} {year}</div>
        </div>

        <!-- Greeting -->
        <div style="padding:24px 32px 0">
          <h2 style="color:#1a1a2e;margin:0">Hello, {user.name}! 👋</h2>
          <p style="color:#666;margin-top:8px">Here is your financial summary for <strong>{month} {year}</strong>.</p>
        </div>

        <!-- Summary Cards -->
        <div style="padding:20px 32px;display:flex;gap:12px">
          <div style="flex:1;background:#f8f8ff;border-radius:12px;padding:16px;text-align:center;border:1px solid #ece9ff">
            <div style="font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px">Income</div>
            <div style="font-size:22px;font-weight:700;color:#7c6ff7;margin-top:4px">₹{income:,.0f}</div>
          </div>
          <div style="flex:1;background:#fff5f5;border-radius:12px;padding:16px;text-align:center;border:1px solid #ffe0e0">
            <div style="font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px">Expenses</div>
            <div style="font-size:22px;font-weight:700;color:#f06375;margin-top:4px">₹{total_exp:,.0f}</div>
          </div>
          <div style="flex:1;background:#f0fff8;border-radius:12px;padding:16px;text-align:center;border:1px solid #c8f0de">
            <div style="font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px">Savings</div>
            <div style="font-size:22px;font-weight:700;color:{status_color};margin-top:4px">₹{savings:,.0f}</div>
          </div>
        </div>

        <!-- Savings Rate -->
        <div style="margin:0 32px;background:#f8f8ff;border-radius:12px;padding:16px;border:1px solid #ece9ff">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="color:#666;font-size:14px">Savings Rate</span>
            <span style="font-size:18px;font-weight:700;color:{rate_color}">{rate}%</span>
          </div>
          <div style="background:#e8e8f0;border-radius:4px;height:8px;margin-top:8px">
            <div style="background:{rate_color};border-radius:4px;height:8px;width:{min(rate,100)}%"></div>
          </div>
          <div style="font-size:12px;color:#999;margin-top:6px">Target: 20%+</div>
        </div>

        <!-- Expense Table -->
        <div style="padding:24px 32px 0">
          <h3 style="color:#1a1a2e;margin:0 0 12px">Expense Breakdown</h3>
          <table style="width:100%;border-collapse:collapse;font-size:14px">
            <thead>
              <tr style="background:#f8f8f8">
                <th style="padding:10px 12px;text-align:left;color:#999;font-size:12px;text-transform:uppercase">Category</th>
                <th style="padding:10px 12px;text-align:right;color:#999;font-size:12px;text-transform:uppercase">Actual</th>
                <th style="padding:10px 12px;text-align:right;color:#999;font-size:12px;text-transform:uppercase">Budget</th>
              </tr>
            </thead>
            <tbody>{expense_rows or '<tr><td colspan="3" style="padding:16px;text-align:center;color:#999">No expenses recorded</td></tr>'}</tbody>
          </table>
        </div>

        <!-- Goals -->
        {'<div style="padding:24px 32px 0"><h3 style="color:#1a1a2e;margin:0 0 12px">Financial Goals</h3><table style="width:100%;border-collapse:collapse;font-size:14px"><tbody>' + goal_rows + '</tbody></table></div>' if goals else ''}

        <!-- Footer -->
        <div style="padding:24px 32px;text-align:center;color:#999;font-size:12px;border-top:1px solid #f0f0f0;margin-top:24px">
          <p style="margin:0">This report was generated by <strong style="color:#7c6ff7">FinTech</strong></p>
          <p style="margin:4px 0 0">Smart Finance Advisor for India 🇮🇳</p>
        </div>
      </div>
    </body>
    </html>'''


@email_bp.route('/send-report', methods=['POST'])
@jwt_required()
def send_report():
    user_id = int(get_jwt_identity())
    data    = request.get_json()
    month   = data.get('month', datetime.now().strftime('%B'))
    year    = int(data.get('year', datetime.now().year))

    user   = User.query.get_or_404(user_id)
    budget = Budget.query.filter_by(user_id=user_id, month=month, year=year).first()
    goals  = Goal.query.filter_by(user_id=user_id).all()

    try:
        html    = build_report_email(user, budget, goals)
        subject = f'FinTech Report — {month} {year}'
        send_email(user.email, subject, html)
        current_app.logger.info(f'Report email sent to {user.email}')
        return jsonify({'message': f'Report sent to {user.email} successfully!'}), 200
    except Exception as e:
        current_app.logger.error(f'Email send failed: {str(e)}')
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500


@email_bp.route('/test', methods=['POST'])
@jwt_required()
def test_email():
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    try:
        send_email(
            user.email,
            'FinTech — Test Email ✓',
            f'<h2>Hello {user.name}!</h2><p>Your FinTech email notifications are working correctly. 🎉</p>'
        )
        return jsonify({'message': f'Test email sent to {user.email}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
