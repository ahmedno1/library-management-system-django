from django.urls import path

from . import views

app_name = "borrowing"

urlpatterns = [
    path("borrow/<int:pk>/", views.borrow_book, name="borrow_book"),
    path("borrow/<int:book_id>/", views.borrow_book, name="borrow_book_alias"),
    path("my-books/", views.my_borrowed_books, name="my_books"),
    path("return/<int:record_id>/", views.return_book, name="return_book"),
]
