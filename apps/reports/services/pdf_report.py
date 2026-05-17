"""End-of-month financial statement PDF generation."""

from __future__ import annotations

import io
from calendar import month_name
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.finance.models import FinancialTransaction, LeaseAgreement
from apps.fleet.models import Vehicle
from apps.tenants.models import Organization


def generate_monthly_statement_pdf(
    organization: Organization,
    year: int,
    month: int,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    period = f"{month_name[month]} {year}"
    story.append(Paragraph("<b>FleetLedger — End of Month Statement</b>", styles["Title"]))
    story.append(Paragraph(f"Organization: {organization.name}", styles["Normal"]))
    story.append(Paragraph(f"Period: {period}", styles["Normal"]))
    story.append(Spacer(1, 16))

    vehicles = Vehicle.all_objects.filter(tenant=organization)
    transactions = FinancialTransaction.all_objects.filter(
        tenant=organization,
        occurred_at__year=year,
        occurred_at__month=month,
    )
    leases = LeaseAgreement.all_objects.filter(tenant=organization, is_active=True)

    total_spend = sum((t.amount for t in transactions), Decimal("0"))

    summary_data = [
        ["Metric", "Value"],
        ["Active vehicles", str(vehicles.filter(status="active").count())],
        ["Total vehicles", str(vehicles.count())],
        ["Active leases", str(leases.count())],
        ["Transactions (period)", str(transactions.count())],
        ["Total spend (period)", f"${total_spend:,.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[220, 200])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Transaction Detail</b>", styles["Heading2"]))
    tx_data = [["Date", "Type", "Amount", "Reference"]]
    for tx in transactions[:500]:
        tx_data.append(
            [
                tx.occurred_at.isoformat(),
                tx.get_transaction_type_display(),
                f"${tx.amount:,.2f}",
                tx.reference or "—",
            ]
        )
    if len(tx_data) == 1:
        tx_data.append(["—", "No transactions", "—", "—"])

    tx_table = Table(tx_data, colWidths=[90, 120, 90, 120])
    tx_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.grey)]))
    story.append(tx_table)

    doc.build(story)
    return buffer.getvalue()
