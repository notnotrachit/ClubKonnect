from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import Forms, Field, Choices
# Create your views here.
def new_form(request):
    return render(request, 'new_form.html')


def form_submit(request):
    data = json.loads(request.body)
    print(data)
    # Get the 1st forms object
    form = Forms.objects.first()
    
    #  Put the data in the form
    for field in data:
        field_obj = Field.objects.create(
            field=field['name'],
            field_type=field['type'],
            description=field['description'],
            is_required=field['is_required']
        )
        if field['type'] == 'select' or field['type'] == 'radio' or field['type'] == 'checkbox':
            for choice in field['options']:
                choice_obj = Choices.objects.create(
                    choice=choice
                )
                field_obj.choices.add(choice_obj)
        form.fields.add(field_obj)





    return JsonResponse({'status': 'success'})