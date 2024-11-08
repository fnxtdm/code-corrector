# myapp/views.py

from django.http import HttpResponse
from django.template import loader

def interactive_screenshot_view(request):
    # Load the HTML template
    template = loader.get_template('index.html')
    context = {
        'title': 'Best 1'
    }
    return HttpResponse(template.render(context, request))