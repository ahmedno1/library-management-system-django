"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from accounts import views as accounts_views

urlpatterns = [
    path("", include("library.urls", namespace="library")),
    path("", include("borrowing.urls", namespace="borrowing")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    # public aliases
    path("login/", accounts_views.login_view, name="login"),
    path("register/", accounts_views.register_view, name="register"),
    path("profile/", accounts_views.profile_view, name="profile"),
    path("profile/edit/", accounts_views.profile_edit_view, name="profile_edit"),
    path("", include("reviews.urls", namespace="reviews")),
    path("admin/", admin.site.urls),
]
