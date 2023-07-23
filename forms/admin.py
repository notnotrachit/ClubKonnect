from django.contrib import admin
from .models import Forms, Field, Choices
# Register your models here.

admin.site.register(Forms)
admin.site.register(Field)
admin.site.register(Choices)
