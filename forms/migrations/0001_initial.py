# Generated by Django 4.2.1 on 2023-07-23 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Choices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(max_length=200)),
                ('field_type', models.CharField(choices=[('text', 'Text'), ('number', 'Number'), ('email', 'Email'), ('select', 'Select'), ('radio', 'Radio'), ('checkbox', 'Checkbox'), ('url', 'URL'), ('textarea', 'Textarea')], default='text', max_length=200)),
                ('description', models.TextField()),
                ('placeholder', models.CharField(max_length=200)),
                ('is_required', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('choices', models.ManyToManyField(to='forms.choices')),
            ],
        ),
        migrations.CreateModel(
            name='Forms',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_published', models.BooleanField(default=False)),
                ('accepting_responses', models.BooleanField(default=False)),
                ('fields', models.ManyToManyField(to='forms.field')),
            ],
        ),
    ]