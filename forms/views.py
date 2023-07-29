from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from .models import Forms, Field, Choices, entries
from Recruitments.decorators import superuser_required
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os


# Create your views here.
@superuser_required
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
    elif request.method == "POST":
        data = {}
        for key in request.POST.keys():
            if key != 'csrfmiddlewaretoken':
                if len(request.POST.getlist(key)) == 1:
                    data[key] = request.POST[key]
                else:
                    data[key] = request.POST.getlist(key)
        form = Forms.objects.get(id=form_id)
        for field in form.fields.all():
            if field.is_required and field.field not in data:
                return JsonResponse({'success': False, 'error': f'{field.field} is required'})
        entries.objects.create(
            form=form,
            user=request.user,
            data=data
        )
        email_text = """
        """
        # send_mail("Thank You for applying",f"Recruitments <{os.getenv('EMAIL_HOST_USER')}>", [request.user.email], fail_silently=False)

        html_message = render_to_string('email/form_submit.html', {'form': form, 'data': data})
        plain_message = strip_tags(html_message)

        send_mail("Thank You for applying", plain_message, f"Recruitments <{os.getenv('EMAIL_HOST_USER')}>", [request.user.email], fail_silently=False, html_message=html_message)
        return JsonResponse({'success': True})


        # return redirect('home')

@superuser_required
def all_forms(request):
    forms = Forms.objects.all()
    return render(request, 'all_forms.html', {'forms': forms})

@superuser_required
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
    

@superuser_required
def form_detail(request, form_id):
    form = Forms.objects.get(id=form_id)
    return render(request, 'form_details.html', {'form': form})

@superuser_required
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

@superuser_required
def all_entries(request):
    entries_all = entries.objects.all()
    return render(request, 'all_entries.html', {'entries': entries_all})

@superuser_required
def entry_detail(request, entry_id):
    entry = entries.objects.get(id=entry_id)
    return render(request, 'entry_detail.html', {'entry': entry})

@superuser_required
def save_notes(request, entry_id):
    if request.method == 'POST':
        entry = entries.objects.get(id=entry_id)
        new_notes= json.loads(request.body)
        entry.notes = new_notes["notes"]
        entry.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})
    
@superuser_required
def form_entries(request, form_id):
    form = Forms.objects.get(id=form_id)
    entries_all = entries.objects.filter(form=form)
    return render(request, 'form_entries.html', {'entries': entries_all, 'form': form})


@superuser_required
def change_form_status(request, entry_id):
    if request.method == 'POST':
        entry = entries.objects.get(id=entry_id)
        new_status = json.loads(request.body)['status']
        entry.status = new_status
        entry.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})
