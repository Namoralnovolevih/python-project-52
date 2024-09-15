from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from .models import Status


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'timestamp')
    search_fields = ['name']
    list_filter = (('timestamp', DateFieldListFilter),)
