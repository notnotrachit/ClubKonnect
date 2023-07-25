from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from .models import Forms, Field, Choices, entries
# Create your views here.
def new_form(request, form_id=None):
    if request.method == 'POST':
        form = Forms.objects.get(id=form_id)
        if len(form.fields.all()) > 0:
            return redirect('form_view')

        data = json.loads(request.body)
        print(data)
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
        return JsonResponse({'success': True})
    else:
        form = Forms.objects.get(id=form_id)
        if len(form.fields.all()) > 0:
            return redirect('form_view')
        return render(request, 'new_form.html', {'form': form})


def form_view(request, form_id):
    if request.method == "GET":
        form = Forms.objects.get(id=form_id)
        return render(request, 'form_view.html', {'form': form})
    else:
        data = json.loads(request.body)
        form = Forms.objects.get(id=form_id)
        for field in form.fields.all():
            if field.is_required and field.field not in data:
                return JsonResponse({'success': False, 'error': f'{field.field} is required'})
        new_entry = entries.objects.create(
            form=form,
            user=request.user,
            data=data
        )
        return JsonResponse({'success': True})


        # return redirect('home')


def all_forms(request):
    forms = Forms.objects.all()
    return render(request, 'all_forms.html', {'forms': forms})


def create_form(request):
    if request.method == 'POST':
        data = request.POST.dict()

        if 'is_public' in data and data['is_public'] == 'on':
            data['is_public'] = True
        else:
            data['is_public'] = False
        if 'accepting_responses' in data and data['accepting_responses'] == 'on':
            data['accepting_responses'] = True
        else:
            data['accepting_responses'] = False
        new_form = Forms.objects.create(
            name=data['name'],
            description=data['description'],
            is_published=data['is_public'],
            accepting_responses=data['accepting_responses']
        )
        return redirect('new_form', form_id=new_form.id)
    else:
        return render(request, 'create_form.html')
    


def form_detail(request, form_id):
    form = Forms.objects.get(id=form_id)
    return render(request, 'form_details.html', {'form': form})

def edit_form_fields(request, form_id):
    if request.method == 'POST':

        data = json.loads(request.body)
        form = Forms.objects.get(id=form_id)
        fields = form.fields.all()
        for field in fields:
            if field.field_type == 'select' or field.field_type == 'radio' or field.field_type == 'checkbox':
                for i in field.choices.all():
                    i.delete()
            field.delete()

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
        return JsonResponse({'success': True})
    else:
        form = Forms.objects.get(id=form_id)       

        return render(request, 'edit_form_fields.html', {'form': form})
    



def home(request):
    all_forms = Forms.objects.filter(is_published=True)
    print(all_forms)
    return render(request, 'home.html', {'all_forms': all_forms})