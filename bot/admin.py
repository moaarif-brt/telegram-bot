from django.contrib import admin
from .models import Token

class TokenAdmin(admin.ModelAdmin):
    list_display = ('token_symbol', 'token_name', 'exchange', 'user', 'created_at', 'updated_at')
    search_fields = ('token_symbol', 'token_name', 'exchange', 'user__username')
    list_filter = ('exchange', 'created_at')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'token_symbol', 'token_name', 'exchange')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Token, TokenAdmin)
