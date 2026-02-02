from django.contrib import admin

from .models import BorrowRecord


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "borrowed_at", "due_at", "returned_at", "is_overdue")
    list_filter = ("borrowed_at", "due_at", "returned_at", "user", "book")
    search_fields = ("user__username", "user__email", "book__title")
    list_select_related = ("user", "book")
    readonly_fields = ("borrowed_at", "due_at", "returned_at")

    def is_overdue(self, obj):
        return obj.is_overdue

    is_overdue.boolean = True
    is_overdue.short_description = "Overdue"
