from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


def user_profile_photo_path(instance, filename):
    return f"users/{instance.user_id}/photos/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField(max_length=150, blank=True)
    photo = models.ImageField(upload_to=user_profile_photo_path, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Profile for {self.user}"
