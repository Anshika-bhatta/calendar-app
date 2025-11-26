from django.contrib import admin
from .models import Event, EventCategory

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'description']
    list_editable = ['color']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'category', 'created_by', 'is_future_event']
    list_filter = ['start_date', 'created_by', 'category']
    search_fields = ['title', 'description', 'location']