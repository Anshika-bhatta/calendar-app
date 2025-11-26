from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Event categories"

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_future_event(self):
        return self.start_date > timezone.now()
    
    def to_google_calendar_url(self):
        """Generate Google Calendar URL for this event"""
        start_str = self.start_date.strftime('%Y%m%dT%H%M%SZ')
        end_str = self.end_date.strftime('%Y%m%dT%H%M%SZ')
        details = f"{self.description} - Location: {self.location}" if self.location else self.description
        
        params = {
            'action': 'TEMPLATE',
            'text': self.title,
            'dates': f"{start_str}/{end_str}",
            'details': details,
            'location': self.location,
        }
        
        # Remove empty values
        params = {k: v for k, v in params.items() if v}
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        return f"https://calendar.google.com/calendar/render?{param_string}"