# src/urls.py

from django.urls import path
from .views import interactive_screenshot_view

urlpatterns = [
    # Change to the view
    path('', interactive_screenshot_view),
]