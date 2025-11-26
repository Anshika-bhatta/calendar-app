from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
import json
from datetime import datetime, timedelta
from .models import Event, EventCategory
from .forms import EventForm, CategoryForm

def is_admin(user):
    return user.is_staff or user.is_superuser

def calendar_view(request):
    """Main calendar view with both list and grid options"""
    now = timezone.now()
    future_events = Event.objects.filter(start_date__gte=now)
    past_events = Event.objects.filter(start_date__lt=now)
    categories = EventCategory.objects.all()
    
    view_type = request.GET.get('view', 'grid')
    
    context = {
        'future_events': future_events,
        'past_events': past_events,
        'categories': categories,
        'view_type': view_type,
        'current_month': now.month,
        'current_year': now.year,
    }
    return render(request, 'calendar.html', context)

def calendar_events_json(request):
    """API endpoint for calendar grid view with proper event timing"""
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    
    if start_str and end_str:
        start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        events = Event.objects.filter(start_date__gte=start, end_date__lte=end)
    else:
        events = Event.objects.all()
    
    events_data = []
    for event in events:
        start_date = event.start_date
        end_date = event.end_date
        
        # Handle single-day events properly
        if start_date.date() == end_date.date():
            # Single day event - use exact times
            event_title = f"{event.title} ({start_date.strftime('%H:%M')}-{end_date.strftime('%H:%M')})"
        else:
            # Multi-day event
            event_title = event.title
        
        events_data.append({
            'id': event.id,
            'title': event_title,
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'description': event.description,
            'category': event.category.name if event.category else 'Uncategorized',
            'color': event.category.color if event.category else '#6c757d',
            'location': event.location,
            'url': f'/edit/{event.id}/',
            'google_calendar_url': event.to_google_calendar_url(),
            'display': 'block',
            'allDay': False,
            # Force single-day display
            'extendedProps': {
                'isSingleDay': start_date.date() == end_date.date()
            }
        })
    
    return JsonResponse(events_data, safe=False)

@login_required
def add_event(request):
    """All logged-in users can add events"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            return redirect('calendar_view')
    else:
        form = EventForm()
    
    categories = EventCategory.objects.all()
    return render(request, 'add_event.html', {'form': form, 'categories': categories})

@login_required
def edit_event(request, event_id):
    """Users can edit their own events, admins can edit all events"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check permission: user can edit their own events or is admin
    if not (request.user == event.created_by or request.user.is_staff):
        return redirect('calendar_view')
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('calendar_view')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'edit_event.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_event(request, event_id):
    """Only admins can delete events"""
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('calendar_view')

@login_required
@user_passes_test(is_admin)
def manage_categories(request):
    """Only admins can manage categories"""
    categories = EventCategory.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'categories.html', {'form': form, 'categories': categories})

@login_required
@user_passes_test(is_admin)
def delete_category(request, category_id):
    """Only admins can delete categories"""
    category = get_object_or_404(EventCategory, id=category_id)
    category.delete()
    return redirect('manage_categories')

def export_event_ical(request, event_id):
    """Export single event as iCal format"""
    event = get_object_or_404(Event, id=event_id)
    
    ical_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Company Calendar//EN
BEGIN:VEVENT
UID:{event.id}@companycalendar
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{event.start_date.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{event.end_date.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{event.title}
DESCRIPTION:{event.description}
LOCATION:{event.location}
END:VEVENT
END:VCALENDAR"""
    
    response = HttpResponse(ical_content, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="event_{event.id}.ics"'
    return response