# src/views.py
import os

from django import forms
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

class UploadFileForm(forms.Form):
    file = forms.FileField()

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            # Check if the uploaded file is a CSV
            # if not file.name.endswith('.csv'):
            #     return HttpResponse('File is not a CSV type')

            # Define the path to save the file
            temp_dir = './temp/'
            tmp_file_path = os.path.join(temp_dir, file.name)
            # Create the /tmp directory if it does not exist
            os.makedirs(temp_dir, exist_ok=True)

            # Save the file to the /tmp directory
            with open(tmp_file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Read the CSV file
            # Save each row in the database
            # for row in reader:
            #     # Assuming the CSV has name, price, description in that order
            #     try:
            #         Product.objects.create(
            #             name=row[0],
            #             price=row[1],
            #             description=row[2]
            #         )
            #     except Exception as e:
            #         return HttpResponse(f'Error saving record: {e}')

            return HttpResponse('File uploaded and data saved successfully')
    else:
        form = UploadFileForm()

    return render(request, 'upload.html', {'form': form})

def list_issue(request):

    return HttpResponse('[{\"issue\": \"[Absolute Path Traversal] localServices/applications/ar..."}]')

def interactive_screenshot_view(request):
    # Load the HTML template
    template = loader.get_template('index.html')
    context = {
        'title': 'Best 1'
    }
    return HttpResponse(template.render(context, request))