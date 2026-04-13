from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

tax_bp = Blueprint('tax', __name__)


@tax_bp.route('/calculate', methods=['POST'])
@jwt_required()
def calculate_tax():
    data = request.get_json()

    # Income details
    gross_salary     = float(data.get('gross_salary', 0))
    other_income     = float(data.get('other_income', 0))
    total_income     = gross_salary + other_income

    # Deductions
    sec_80c          = min(float(data.get('sec_80c', 0)), 150000)       # PPF, ELSS, LIC etc. max 1.5L
    sec_80d          = min(float(data.get('sec_80d', 0)), 25000)        # Health insurance max 25k
    sec_80d_parents  = min(float(data.get('sec_80d_parents', 0)), 50000) # Parents health insurance
    hra_exemption    = float(data.get('hra_exemption', 0))
    std_deduction    = 50000                                             # Standard deduction FY2024-25
    home_loan_int    = min(float(data.get('home_loan_int', 0)), 200000) # Section 24b max 2L
    nps_80ccd        = min(float(data.get('nps_80ccd', 0)), 50000)      # NPS additional 80CCD(1B)

    total_deductions = sec_80c + sec_80d + sec_80d_parents + hra_exemption + std_deduction + home_loan_int + nps_80ccd
    taxable_income   = max(total_income - total_deductions, 0)

    # ── OLD REGIME TAX SLABS (FY 2024-25) ──────────────────────────
    def old_regime_tax(income):
        tax = 0
        if income <= 250000:    tax = 0
        elif income <= 500000:  tax = (income - 250000) * 0.05
        elif income <= 1000000: tax = 12500 + (income - 500000) * 0.20
        else:                   tax = 112500 + (income - 1000000) * 0.30
        # Rebate u/s 87A — if taxable income <= 5L, tax = 0
        if income <= 500000:    tax = 0
        cess = tax * 0.04
        return round(tax + cess)

    # ── NEW REGIME TAX SLABS (FY 2024-25) ──────────────────────────
    def new_regime_tax(income):
        tax = 0
        slabs = [
            (300000, 0.00),
            (300000, 0.05),
            (300000, 0.10),
            (300000, 0.15),
            (300000, 0.20),
            (float('inf'), 0.30),
        ]
        remaining = income
        for limit, rate in slabs:
            if remaining <= 0: break
            taxable_in_slab = min(remaining, limit)
            tax += taxable_in_slab * rate
            remaining -= taxable_in_slab
        # Rebate u/s 87A — if income <= 7L, tax = 0
        if income <= 700000: tax = 0
        cess = tax * 0.04
        return round(tax + cess)

    old_tax = old_regime_tax(taxable_income)
    new_tax = new_regime_tax(total_income)   # New regime uses gross (fewer deductions allowed)

    better_regime = 'new' if new_tax < old_tax else 'old'
    tax_saved     = abs(old_tax - new_tax)

    # 80C breakdown suggestions
    remaining_80c = 150000 - sec_80c
    suggestions   = []
    if remaining_80c > 0:
        suggestions.append(f"You can still invest Rs.{remaining_80c:,.0f} more under 80C (PPF, ELSS, LIC)")
    if sec_80d == 0:
        suggestions.append("Buy health insurance to claim up to Rs.25,000 under Section 80D")
    if nps_80ccd == 0:
        suggestions.append("Invest in NPS to get additional Rs.50,000 deduction under 80CCD(1B)")
    if home_loan_int == 0:
        suggestions.append("Home loan interest up to Rs.2,00,000 is deductible under Section 24b")

    return jsonify({
        'gross_salary':     gross_salary,
        'total_income':     total_income,
        'total_deductions': total_deductions,
        'taxable_income':   taxable_income,
        'std_deduction':    std_deduction,
        'old_regime': {
            'tax':          old_tax,
            'monthly_tax':  round(old_tax / 12),
            'effective_rate': round((old_tax / total_income * 100), 2) if total_income else 0,
        },
        'new_regime': {
            'tax':          new_tax,
            'monthly_tax':  round(new_tax / 12),
            'effective_rate': round((new_tax / total_income * 100), 2) if total_income else 0,
        },
        'better_regime':  better_regime,
        'tax_saved':      tax_saved,
        'suggestions':    suggestions,
        'deduction_breakdown': {
            '80C':          sec_80c,
            '80D':          sec_80d,
            '80D_parents':  sec_80d_parents,
            'HRA':          hra_exemption,
            'std_deduction': std_deduction,
            'home_loan':    home_loan_int,
            'NPS_80CCD':    nps_80ccd,
        }
    }), 200
