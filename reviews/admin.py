from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "stars", "created_at")
    search_fields = ("user__username", "user__email", "book__title", "comment")
    list_filter = ("stars", "created_at")
    list_select_related = ("user", "book")
    readonly_fields = ("created_at",)
