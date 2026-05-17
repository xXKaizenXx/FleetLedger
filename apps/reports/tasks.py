"""Celery tasks for asynchronous encrypted report delivery."""

from __future__ import annotations

import logging
from calendar import month_name

from django.conf import settings
from django.core.mail import EmailMessage

from apps.accounts.models import User
from apps.core.context import set_bypass_tenant_filter, set_current_tenant_id
from apps.reports.services.encryption import encrypt_pdf
from apps.reports.services.pdf_report import generate_monthly_statement_pdf
from apps.tenants.models import Organization
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_monthly_report_task(
    self,
    tenant_id: int,
    user_id: int,
    year: int,
    month: int,
):
    set_bypass_tenant_filter(True)
    set_current_tenant_id(tenant_id)

    try:
        organization = Organization.objects.get(pk=tenant_id)
        user = User.objects.get(pk=user_id)
        pdf_bytes = generate_monthly_statement_pdf(organization, year, month)
        encrypted = encrypt_pdf(pdf_bytes, settings.REPORT_ENCRYPTION_PASSWORD)

        period = f"{month_name[month]} {year}"
        email = EmailMessage(
            subject=f"FleetLedger Statement — {organization.name} — {period}",
            body=(
                f"Your encrypted end-of-month financial statement for {period} is attached.\n\n"
                f"Open the PDF with the report password configured for your organization."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        filename = f"fleetledger-{organization.slug}-{year}-{month:02d}.pdf"
        email.attach(filename, encrypted, "application/pdf")
        email.send(fail_silently=False)

        logger.info("Report emailed to %s for tenant %s", user.email, tenant_id)
        return {"status": "sent", "recipient": user.email, "period": period}
    except Exception as exc:
        logger.exception("Report generation failed for tenant %s", tenant_id)
        raise self.retry(exc=exc) from exc
