import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tickets.models import DepartmentOption, IssueTypeOption

departments = [
    'Purchase', 'Inventory', 'Production', 'PPC', 
    'Accounts', 'HR', 'IT', 'Sales', 'Other'
]

issue_types = [
    'ERP Issue', 'BOM Issue', 'Purchase Issue', 'Inventory Issue',
    'Production Issue', 'Network Issue', 'Hardware Issue', 'Software Issue', 'Other'
]

for dept in departments:
    DepartmentOption.objects.get_or_create(name=dept)
    print(f"Added dept: {dept}")

for issue in issue_types:
    IssueTypeOption.objects.get_or_create(name=issue)
    print(f"Added issue: {issue}")

print("Done populating options.")
