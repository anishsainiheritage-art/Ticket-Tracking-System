"""
models.py — Ticket Model for ERP Help Desk & Ticket Management System.

Security Notes:
  - ticket_no is auto-generated server-side; never derived from user input.
  - attachment uses upload_to with a callable that generates a UUID-based filename
    to prevent directory traversal and filename collision.
  - All string fields are sanitised at the form layer (TicketForm).
"""

import uuid
import os
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# Upload helper — generates a UUID filename to prevent path traversal & leaks
# TODO(security): In production, store files outside the web root and serve
#                 via an authenticated view, not directly via MEDIA_URL.
# ---------------------------------------------------------------------------
def ticket_attachment_path(instance, filename):
    """
    Return a safe upload path with a UUID-based filename.
    Original extension is preserved but the filename is randomised.
    Example: media/tickets/2026/06/04/<uuid>.pdf
    """
    ext = os.path.splitext(filename)[1].lower()          # e.g. '.pdf'
    safe_name = f"{uuid.uuid4().hex}{ext}"               # randomised filename
    today = timezone.now()
    return os.path.join(
        'tickets',
        str(today.year),
        str(today.month).zfill(2),
        str(today.day).zfill(2),
        safe_name,
    )


# ---------------------------------------------------------------------------
# Choice constants
# ---------------------------------------------------------------------------
class StatusChoices(models.TextChoices):
    OPEN        = 'Open',        'Open'
    ASSIGNED    = 'Assigned',    'Assigned'
    IN_PROGRESS = 'In Progress', 'In Progress'
    CLOSED      = 'Closed',      'Closed'


class PriorityChoices(models.TextChoices):
    LOW      = 'Low',      'Low'
    MEDIUM   = 'Medium',   'Medium'
    HIGH     = 'High',     'High'
    CRITICAL = 'Critical', 'Critical'


class DepartmentChoices(models.TextChoices):
    PURCHASE    = 'Purchase',    'Purchase'
    INVENTORY   = 'Inventory',   'Inventory'
    PRODUCTION  = 'Production',  'Production'
    PPC         = 'PPC',         'PPC'
    ACCOUNTS    = 'Accounts',    'Accounts'
    HR          = 'HR',          'HR'
    IT          = 'IT',          'IT'
    SALES       = 'Sales',       'Sales'
    OTHER       = 'Other',       'Other'


class IssueTypeChoices(models.TextChoices):
    ERP_ISSUE        = 'ERP Issue',        'ERP Issue'
    BOM_ISSUE        = 'BOM Issue',        'BOM Issue'
    PURCHASE_ISSUE   = 'Purchase Issue',   'Purchase Issue'
    INVENTORY_ISSUE  = 'Inventory Issue',  'Inventory Issue'
    PRODUCTION_ISSUE = 'Production Issue', 'Production Issue'
    NETWORK_ISSUE    = 'Network Issue',    'Network Issue'
    HARDWARE_ISSUE   = 'Hardware Issue',   'Hardware Issue'
    SOFTWARE_ISSUE   = 'Software Issue',   'Software Issue'
    OTHER            = 'Other',            'Other'


# ---------------------------------------------------------------------------
# Ticket Model
# ---------------------------------------------------------------------------
class Ticket(models.Model):
    """
    Core ticket model.  ticket_no is generated automatically in save().
    """

    # ── Identity ─────────────────────────────────────────────────────────────
    ticket_no = models.CharField(
        max_length=30,
        unique=True,
        blank=True,          # populated in save() before DB insert
        editable=False,
        db_index=True,
        verbose_name='Ticket Number',
    )

    # ── Requester details ────────────────────────────────────────────────────
    full_name = models.CharField(
        max_length=150,
        verbose_name='Full Name',
    )
    mobile_number = models.CharField(
        max_length=15,
        verbose_name='Mobile Number',
        blank=True,
        null=True,
    )
    # email = models.EmailField(
    #     blank=True,
    #     null=True,
    #     verbose_name='Email Address',
    # )

    # ── Classification ───────────────────────────────────────────────────────
    department = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name='Department',
    )
    issue_type = models.CharField(
        max_length=60,
        db_index=True,
        verbose_name='Issue Type',
    )
    priority = models.CharField(
        max_length=20,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM,
        db_index=True,
        verbose_name='Priority',
    )

    # ── Content ──────────────────────────────────────────────────────────────
    description = models.TextField(
        verbose_name='Detailed Description',
    )
    attachment = models.FileField(
        upload_to=ticket_attachment_path,
        blank=True,
        null=True,
        verbose_name='Attachment',
    )

    # ── Workflow ─────────────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.OPEN,
        db_index=True,
        verbose_name='Status',
    )

    # ── Timestamps ───────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True,     verbose_name='Updated At')

    # ── Meta ─────────────────────────────────────────────────────────────────
    class Meta:
        db_table   = 'tickets'
        ordering   = ['-created_at']
        verbose_name        = 'Ticket'
        verbose_name_plural = 'Tickets'

    # ── Ticket-number generation ─────────────────────────────────────────────
    def _generate_ticket_no(self):
        """
        Generate a sequential ticket number in the format TKT-YYYYMMDD-NNN.
        The sequence resets each calendar day.
        """
        today_str = timezone.now().strftime('%Y%m%d')       # e.g. '20260604'
        prefix    = f'TKT-{today_str}-'

        # Count tickets already created today to compute the next sequence
        last_ticket = (
            Ticket.objects
            .filter(ticket_no__startswith=prefix)
            .order_by('-ticket_no')
            .first()
        )

        if last_ticket:
            try:
                last_seq = int(last_ticket.ticket_no.split('-')[-1])
            except (ValueError, IndexError):
                last_seq = 0
            next_seq = last_seq + 1
        else:
            next_seq = 1

        return f'{prefix}{str(next_seq).zfill(3)}'          # e.g. TKT-20260604-007

    # ── Overrides ────────────────────────────────────────────────────────────
    def save(self, *args, **kwargs):
        if not self.ticket_no:
            self.ticket_no = self._generate_ticket_no()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.ticket_no} — {self.full_name}'

# ---------------------------------------------------------------------------
# Dynamic Dropdown Option Models
# ---------------------------------------------------------------------------
class FilterNameOption(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Filter Name Option')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Filter Name Option'
        verbose_name_plural = 'Filter Name Options'
        ordering = ['name']

class DepartmentOption(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Department Name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Department Option'
        verbose_name_plural = 'Department Options'
        ordering = ['name']

class IssueTypeOption(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Issue Type Name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Issue Type Option'
        verbose_name_plural = 'Issue Type Options'
        ordering = ['name']
