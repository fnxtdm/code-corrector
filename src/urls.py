# src/urls.py

from django.urls import path
from .views import interactive_screenshot_view
from .views import upload_file, list_issue

urlpatterns = [
    # Change to the view
    path('', interactive_screenshot_view),
    path('upload/', upload_file, name='upload_file'),
    path('list_issue/', list_issue, name='list_issue'),
]