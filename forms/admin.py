from django.contrib import admin
from .models import Forms, Field, Choices, entries, deleted_entries
# Register your models here.

admin.site.register(Forms)
admin.site.register(Field)
admin.site.register(Choices)
admin.site.register(entries)
admin.site.register(deleted_entries)
