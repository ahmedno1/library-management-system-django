from django.urls import path

from . import views

app_name = "library"

urlpatterns = [
    path("", views.home, name="home"),
    path("books/", views.book_list, name="book_list"),
    path("books/<int:pk>/", views.book_detail, name="book_detail_alias"),
    path("book/<int:pk>/", views.book_detail, name="book_detail"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/<slug:slug>/", views.category_detail, name="category_detail"),
    path("authors/", views.author_list, name="author_list"),
    path("authors/<int:pk>/", views.author_detail, name="author_detail"),
    path("contact/", views.contact, name="contact"),
]
