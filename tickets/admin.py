from django.contrib import admin
from django.http import HttpResponse
from .models import Ticket, FilterNameOption, DepartmentOption, IssueTypeOption
import openpyxl
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

@admin.action(description='Export selected tickets to Excel')
def export_to_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="admin_tickets.xlsx"'
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Tickets'
    
    columns = ['Ticket No', 'Full Name', 'Department', 'Issue Type', 'Priority', 'Status', 'Created At']
    worksheet.append(columns)
    
    for ticket in queryset:
        created_at_str = ticket.created_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.created_at else ""
        row = [
            ticket.ticket_no,
            ticket.full_name,
            ticket.department,
            ticket.issue_type,
            ticket.priority,
            ticket.status,
            created_at_str
        ]
        worksheet.append(row)
        
    workbook.save(response)
    return response

@admin.action(description='Export selected tickets to PDF')
def export_to_pdf(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="admin_tickets.pdf"'
    
    # We use landscape to fit columns better, but letter is fine if columns are few.
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    data = [['Ticket No', 'Full Name', 'Department', 'Issue Type', 'Status']]
    for ticket in queryset:
        data.append([
            ticket.ticket_no, 
            ticket.full_name, 
            ticket.department, 
            ticket.issue_type, 
            ticket.status
        ])
        
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    doc.build(elements)
    return response

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_no', 'full_name', 'department', 'issue_type', 'priority', 'status', 'created_at')
    search_fields = ('ticket_no', 'full_name')
    list_filter = ('status', 'priority', 'department', 'issue_type')
    readonly_fields = ('ticket_no', 'created_at', 'updated_at')
    actions = [export_to_excel, export_to_pdf]

@admin.register(FilterNameOption)
class FilterNameOptionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(DepartmentOption)
class DepartmentOptionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(IssueTypeOption)
class IssueTypeOptionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
