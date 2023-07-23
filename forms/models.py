from django.db import models

class Choices(models.Model):
    choice = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.choice


class Field(models.Model):
    field = models.CharField(max_length=200)
    field_type = models.CharField(
        choices=(
            ('text', 'Text'),
            ('number', 'Number'),
            ('email', 'Email'),
            ('select', 'Select'),
            ('radio', 'Radio'),
            ('checkbox', 'Checkbox'),
            ('url', 'URL'),
            ('textarea', 'Textarea'),
    ),
    default='text',
    max_length=200
    )
    choices = models.ManyToManyField(Choices)
    description = models.TextField()
    placeholder = models.CharField(max_length=200)
    is_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.field

# Create your models here.
class Forms(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    fields = models.ManyToManyField(Field, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    accepting_responses = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
