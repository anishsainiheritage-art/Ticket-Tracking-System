from django.shortcuts import render, redirect
from .models import Ticket, FilterNameOption, DepartmentOption, IssueTypeOption
from .forms import TicketForm


def ticket_create(request):

    if request.method == 'POST':

        form = TicketForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()
            return redirect('ticket_list')

    else:
        form = TicketForm()

    departments = DepartmentOption.objects.all()
    issue_types = IssueTypeOption.objects.all()

    return render(
        request,
        'tickets/ticket_form.html',
        {
            'form': form,
            'departments': departments,
            'issue_types': issue_types,
        }
    )


from django.db.models import Q

def ticket_list(request):

    tickets = Ticket.objects.all().order_by('-id')

    # Advanced Search & Filter Logic
    ticket_no = request.GET.get('ticket_no')
    full_name = request.GET.get('full_name')
    mobile_number = request.GET.get('mobile_number')
    department = request.GET.get('department')
    issue_type = request.GET.get('issue_type')
    priority = request.GET.get('priority')
    status = request.GET.get('status')
    created_date = request.GET.get('created_date')
    search_query = request.GET.get('q')

    if ticket_no:
        tickets = tickets.filter(ticket_no__icontains=ticket_no)
    if full_name:
        tickets = tickets.filter(full_name__icontains=full_name)
    if mobile_number:
        tickets = tickets.filter(mobile_number__icontains=mobile_number)
    if department:
        tickets = tickets.filter(department=department)
    if issue_type:
        tickets = tickets.filter(issue_type=issue_type)
    if priority:
        tickets = tickets.filter(priority=priority)
    if status:
        tickets = tickets.filter(status=status)
    if created_date:
        tickets = tickets.filter(created_at__date=created_date)
    if search_query:
        tickets = tickets.filter(
            Q(ticket_no__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    total_tickets = tickets.count()
    open_tickets = tickets.filter(status='Open').count()
    assigned_tickets = tickets.filter(status='Assigned').count()
    inprogress_tickets = tickets.filter(status='In Progress').count()
    resolved_tickets = tickets.filter(status='Resolved').count()
    closed_tickets = tickets.filter(status='Closed').count()

    name_options = FilterNameOption.objects.all()
    departments = DepartmentOption.objects.all()
    issue_types = IssueTypeOption.objects.all()

    return render(
        request,
        'tickets/ticket_list.html',
        {
            'tickets': tickets,
            'name_options': name_options,
            'departments': departments,
            'issue_types': issue_types,
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'assigned_tickets': assigned_tickets,
            'inprogress_tickets': inprogress_tickets,
            'resolved_tickets': resolved_tickets,
            'closed_tickets': closed_tickets,
        }
    )


def ticket_edit(request, pk):

    ticket = Ticket.objects.get(id=pk)

    if request.method == 'POST':

        form = TicketForm(
            request.POST,
            request.FILES,
            instance=ticket
        )

        if form.is_valid():
            form.save()
            return redirect('ticket_list')

    else:
        form = TicketForm(instance=ticket)

    departments = DepartmentOption.objects.all()
    issue_types = IssueTypeOption.objects.all()

    return render(
        request,
        'tickets/ticket_form.html',
        {
            'form': form,
            'departments': departments,
            'issue_types': issue_types,
        }
    )


def ticket_status(request, pk):

    ticket = Ticket.objects.get(id=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            ticket.status = new_status
            ticket.save()
    else:
        # Fallback for GET requests
        if ticket.status == 'Open':
            ticket.status = 'Assigned'
        elif ticket.status == 'Assigned':
            ticket.status = 'In Progress'
        elif ticket.status == 'In Progress':
            ticket.status = 'Resolved'
        ticket.save()

    return redirect('ticket_list')

from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.contrib import messages

def ticket_delete(request, pk):
    if request.method == 'POST':
        passcode = request.POST.get('passcode')
        if passcode == 'it@heritage':
            ticket = Ticket.objects.get(id=pk)
            ticket.delete()
            messages.success(request, "Ticket deleted successfully.")
            return redirect('ticket_list')
        else:
            messages.error(request, "Incorrect passcode for deletion.")
            return redirect('ticket_list')
    return HttpResponseBadRequest("Invalid request method.")