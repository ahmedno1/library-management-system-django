from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("books/<int:book_id>/review/", views.add_review, name="add_review_alias"),
    path("book/<int:book_id>/review/", views.add_review, name="add_review"),
]
