from django.contrib import admin

from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'number', 'first_club', 'current_club', 'age')
    list_filter = ('position',)
    search_fields = ('name', 'first_club', 'current_club')
    ordering = ('name',)
