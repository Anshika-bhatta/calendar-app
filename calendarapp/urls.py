from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar_view'),
    path('add/', views.add_event, name='add_event'),
    path('edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('events/json/', views.calendar_events_json, name='calendar_events_json'),
    path('export/ical/<int:event_id>/', views.export_event_ical, name='export_event_ical'),
]