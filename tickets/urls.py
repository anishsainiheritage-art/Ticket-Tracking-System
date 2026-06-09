from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.ticket_list,
        name='ticket_list'
    ),

    path(
        'create/',
        views.ticket_create,
        name='ticket_create'
    ),
    path(
    'edit/<int:pk>/',
    views.ticket_edit,
    name='ticket_edit'
),
path(
    'status/<int:pk>/',
    views.ticket_status,
    name='ticket_status'
),
    path(
        'delete/<int:pk>/',
        views.ticket_delete,
        name='ticket_delete'
    ),
]