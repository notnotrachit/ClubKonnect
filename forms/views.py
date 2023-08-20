from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import json
from .models import Forms, Field, Choices, entries, deleted_entries
from Recruitments.decorators import superuser_required, staff_req
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from allauth.socialaccount.models import SocialApp, SocialAppManager, SocialAccount
import os
import csv


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
                is_required=field['is_required'],
                github_required=field['github_required'],
                linkedin_required=field['linkedin_required'],
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

@login_required
def form_view(request, form_id):
    form = Forms.objects.get(id=form_id)
    if entries.objects.filter(form=form, user=request.user).count() > 0:
        return redirect('home')
    if request.user.is_superuser == False and form.accepting_responses == False:
        return render(request, 'not_accepting_response.html')
    if request.method == "GET":
        form = Forms.objects.get(id=form_id)
        user = request.user
        if form.accepting_responses == False:
            return render(request, 'form_view.html', {'form': form})
        user_github = SocialAccount.objects.filter(user=user, provider='github')
        user_linkedin = SocialAccount.objects.filter(user=user, provider='linkedin_oauth2')
        github_connected = False
        linkedin_connected = False
        if len(user_github) > 0:
            github_connected = True
        if len(user_linkedin) > 0:
            linkedin_connected = True
        user_linkedin = SocialAccount.objects.filter(user=user, provider='linkedin_oauth2')
        return render(request, 'form_view.html', {'form': form, 'user_github': github_connected, 'user_linkedin': linkedin_connected})
    elif request.method == "POST":
        data = {}
        for key in request.POST.keys():
            if key != 'csrfmiddlewaretoken':
                if len(request.POST.getlist(key)) == 1:
                    data[key] = request.POST[key]
                else:
                    data[key] = request.POST.getlist(key)
        form = Forms.objects.get(id=form_id)
        required_fields = ""
        for field in form.fields.all():
            if field.is_required and ((field.field not in data) or (data[field.field] == '') ):
                required_fields = required_fields + field.field + ', '
        if len(required_fields) > 0:
            return JsonResponse({'success': False, 'error': 'The following fields are required: ' + required_fields[:-2]})
        
        if form.github_required:
                github_app = SocialApp.objects.filter(provider='github')
                if len(github_app) > 0:
                    github_account = SocialAccount.objects.filter(user=request.user, provider='github')
                    if len(github_account) == 0:
                        return JsonResponse({'success': False, 'error': 'Github is required', 'social_connection_error': True})
        if form.linkedin_required:
                linkedin_app = SocialApp.objects.filter(provider='linkedin_oauth2')
                if len(linkedin_app) > 0:
                    linkedin_account = SocialAccount.objects.filter(user=request.user, provider='linkedin_oauth2')
                    if len(linkedin_account) == 0:
                        return JsonResponse({'success': False, 'error': 'Linkedin is required', 'social_connection_error': True})
        entries.objects.create(
            form=form,
            user=request.user,
            data=data
        )
        html_message = render_to_string('email/form_submit.html', {'form': form, 'data': data})
        plain_message = strip_tags(html_message)

        send_mail("Thank You for applying", plain_message, f"Recruitments <{os.getenv('EMAIL_HOST_USER')}>", [request.user.email], fail_silently=False, html_message=html_message)
        return JsonResponse({'success': True})

@staff_req
def all_forms(request):
    if request.user.is_superuser:
        forms = Forms.objects.all()
    else:
        forms = Forms.objects.filter(group_allowed__in=request.user.groups.all())
    for i in forms:
        entry_count = entries.objects.filter(form=i).count()
        i.entry_count = entry_count
    return render(request, 'all_forms.html', {'forms': forms})

@staff_req
def create_form(request):
    if request.user.is_superuser:
        pass
    else:
        return redirect('home')
    if request.method == 'POST':
        data = request.POST.dict()
        print(data)
        if 'is_published' in data and data['is_published'] == 'on':
            data['is_published'] = True
        else:
            data['is_published'] = False
        if 'accepting_responses' in data and data['accepting_responses'] == 'on':
            data['accepting_responses'] = True
        else:
            data['accepting_responses'] = False
        if 'github_required' in data and data['github_required'] == 'on':
            data['github_required'] = True
        else:
            data['github_required'] = False
        if 'linkedin_required' in data and data['linkedin_required'] == 'on':
            data['linkedin_required'] = True
        else:
            data['linkedin_required'] = False
        new_form = Forms.objects.create(
            name=data['name'],
            description=data['description'],
            is_published=data['is_published'],
            accepting_responses=data['accepting_responses'],
            github_required=data['github_required'],
            linkedin_required=data['linkedin_required'],
        )
        return redirect('edit_form_fields', form_id=new_form.id)
    else:
        github_social_app = SocialApp.objects.filter(provider='github')
        linkedin_social_app = SocialApp.objects.filter(provider='linkedin_oauth2')
        if len(github_social_app) > 0:
            github = True
        else:
            github = False
        if len(linkedin_social_app) > 0:
            linkedin = True
        else:
            linkedin = False
        return render(request, 'create_form.html', {'github': github, 'linkedin': linkedin})
    

@staff_req
def form_detail(request, form_id):
    form = Forms.objects.get(id=form_id)
    if form.group_allowed.filter(id__in=request.user.groups.all()).count() > 0 or request.user.is_superuser:
        pass
    else:
        return redirect('home')
    github_app = SocialApp.objects.filter(provider='github')
    linkedin_app = SocialApp.objects.filter(provider='linkedin_oauth2')
    if len(github_app) > 0:
        github = True
    else:
        github = False
    if len(linkedin_app) > 0:
        linkedin = True
    else:
        linkedin = False
    if request.method == 'POST':
        data = request.body
        data = json.loads(data)
        form.is_published = data['is_published']
        form.accepting_responses = data['accepting_responses']
        if github:
            form.github_required = data['github_required']
        if linkedin:
            form.linkedin_required = data['linkedin_required']
        form.name = data['name']
        form.description = data['description']
        form.save()
        return JsonResponse({'success': True})
    else:
        form = Forms.objects.get(id=form_id)
        return render(request, 'form_details.html', {'form': form, 'github': github, 'linkedin': linkedin})

@staff_req
def edit_form_fields(request, form_id):
    form = Forms.objects.get(id=form_id)
    if form.group_allowed.filter(id__in=request.user.groups.all()).count() > 0 or request.user.is_superuser:
        pass
    else:
        return redirect('home')
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
                is_required=field['is_required'],
                placeholder=field['placeholder'],
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
    if request.user.is_authenticated:
        for i in all_forms:
            entry = entries.objects.filter(form=i, user=request.user)
            if len(entry) > 0:
                i.applied = True
                i.entry = entry[0]
            else:
                i.applied = False
    return render(request, 'home.html', {'all_forms': all_forms})

@staff_req
def all_entries(request):
    if request.user.is_superuser:
        pass
    else:
        return redirect('home')
    entries_all = entries.objects.all()
    return render(request, 'all_entries.html', {'entries': entries_all})

@staff_req
def entry_detail(request, entry_id):
    entry = entries.objects.get(id=entry_id)
    form = entry.form
    if form.group_allowed.filter(id__in=request.user.groups.all()).count() > 0 or request.user.is_superuser:
        pass
    else:
        return redirect('home')
    user = entry.user
    user_github = SocialAccount.objects.filter(user=user, provider='github')
    user_linkedin = SocialAccount.objects.filter(user=user, provider='linkedin_oauth2')
    if user_github:
        user_github = user_github[0]
    if user_linkedin:
        user_linkedin = user_linkedin[0]
    return render(request, 'entry_detail.html', {'entry': entry, 'user_github': user_github, 'user_linkedin': user_linkedin})

@staff_req
def save_notes(request, entry_id):
    if request.method == 'POST':
        entry = entries.objects.get(id=entry_id)
        form = entry.form
        if form.group_allowed.filter(id__in=request.user.groups.all()).count() > 0 or request.user.is_superuser:
            pass
        else:
            return redirect('home')
        new_notes= json.loads(request.body)
        entry.notes = new_notes["notes"]
        entry.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})
    
@staff_req
def form_entries(request, form_id):
    form = Forms.objects.get(id=form_id)
    status_filter = request.GET.get('status', None)
    if request.user.is_superuser:
        entries_all = entries.objects.filter(form=form)
        all_statuses = entries_all.values_list('status', flat=True).distinct()
        if status_filter:
            entries_all = entries_all.filter(status=status_filter)
        return render(request, 'form_entries.html', {'entries': entries_all, 'form': form, 'all_statuses': all_statuses, 'status_filter': status_filter})
    else:
        if form.group_allowed.filter(id__in=request.user.groups.all()).count() > 0:
            entries_all = entries.objects.filter(form=form)
            all_statuses = entries_all.values_list('status', flat=True).distinct()
            if status_filter:
                entries_all = entries_all.filter(status=status_filter)
            
            return render(request, 'form_entries.html', {'entries': entries_all, 'form': form, 'all_statuses': all_statuses, 'status_filter': status_filter})
        else:
            return redirect('home')


@staff_req
def form_entries_export(request, form_id):
    form = Forms.objects.get(id=form_id)
    if form.group_allowed.filter(id__in=request.user.groups.all()).count() > 0 or request.user.is_superuser:
        pass
    else:
        return redirect('home')
    entries_all = entries.objects.filter(form=form)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{form.name}.csv"'
    writer = csv.writer(response)
    header = ['User_Acc_Name', 'Email']
    if form.github_required:
        header.append('Github')
    for field in form.fields.all():
        header.append(field.field)
    header.append('Status')
    header.append('Notes')
    writer.writerow(header)
    for entry in entries_all:
        row = []
        row.append(entry.user.first_name + ' ' + entry.user.last_name)
        row.append(entry.user.email)
        if form.github_required:
            row.append(entry.user.socialaccount_set.filter(provider='github')[0].extra_data['login'])
        for field in form.fields.all():
            if field.field in entry.data:
                if field.field_type == 'checkbox':
                    if type(entry.data[field.field]) == list:
                        row.append(', '.join(entry.data[field.field]))
                    else:
                        row.append(entry.data[field.field])
                else:
                    row.append(entry.data[field.field])
            else:
                row.append('')
        row.append(entry.status)
        row.append(entry.notes)
        writer.writerow(row)
    return response


@staff_req
def change_form_status(request, entry_id):
    if request.method == 'POST':
        entry = entries.objects.get(id=entry_id)
        form = entry.form
        if form.group_allowed.filter(id__in=request.user.groups.all()).count() > 0 or request.user.is_superuser:
            pass
        else:
            return redirect('home')
        new_status = json.loads(request.body)['status']
        entry.status = new_status
        entry.save()
        html_message = render_to_string('email/Status_update.html', {'user': entry.user, 'new_status': new_status, 'form': entry.form})
        plain_message = strip_tags(html_message)
        send_mail(
            'Status Update',
            plain_message,
            f"Recruitments <{os.getenv('EMAIL_HOST_USER')}>",
            [entry.user.email], 
            html_message=html_message,
        )
        return JsonResponse({'success': True, 'new_status': new_status})
    else:
        return JsonResponse({'success': False})

@login_required
def user_social(request):
    user = request.user
    socials = SocialAccount.objects.filter(user=user)
    github_connection = SocialAccount.objects.filter(user=user, provider='github')
    linkedin_connection = SocialAccount.objects.filter(user=user, provider='linkedin_oauth2')
    if len(github_connection) == 0:
        github_connection = False
    else:
        github_connection = True
    if len(linkedin_connection) == 0:
        linkedin_connection = False
    else:
        linkedin_connection = True
    return JsonResponse({'success': True, 'github_connection': github_connection, 'linkedin_connection': linkedin_connection})


@staff_req
def delete_entry(request, entry_id):
    entry = entries.objects.get(id=entry_id)
    form = entry.form
    if form.group_allowed.filter(id__in=request.user.groups.all()).count() > 0 or request.user.is_superuser:
        pass
    else:
        return redirect('home')
    deleted_entries.objects.create(
        form=form,
        user=entry.user,
        data=entry.data,
        notes=entry.notes,
        status=entry.status
    )
    entry.delete()
    return redirect(form_entries, form_id=form.id)