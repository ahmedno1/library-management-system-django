from django.contrib import admin

from .models import Author, Book, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "slug")
    search_fields = ("name", "slug")
    readonly_fields = ("slug",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "created_at")
    search_fields = ("full_name",)
    list_filter = ("created_at",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "total_copies", "available_copies", "created_at")
    search_fields = ("title", "author__full_name", "category__name", "language")
    list_filter = ("category", "author", "language", "publication_year", "created_at")
    list_select_related = ("author", "category")
    readonly_fields = ("created_at",)
