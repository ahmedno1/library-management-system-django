from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, editable=False)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["slug"])]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self) -> str:
        base_slug = slugify(self.name)
        slug_candidate = base_slug
        counter = 1
        while Category.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
            slug_candidate = f"{base_slug}-{counter}"
            counter += 1
        return slug_candidate


class Author(models.Model):
    full_name = models.CharField(max_length=150)
    photo = models.ImageField(upload_to="authors/photos/", blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.full_name


class Book(models.Model):
    title = models.CharField(max_length=200)
    cover = models.ImageField(upload_to="books/covers/", blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="books")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="books")
    description = models.TextField()
    language = models.CharField(max_length=50)
    publication_year = models.PositiveSmallIntegerField(blank=True, null=True)
    pages = models.PositiveIntegerField(blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title", "author__full_name"]
        indexes = [models.Index(fields=["title"])]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.title

    def clean(self):
        super().clean()
        if self.available_copies is not None and self.total_copies is not None:
            if self.available_copies < 0:
                raise ValidationError({"available_copies": "Available copies cannot be negative."})
            if self.available_copies > self.total_copies:
                raise ValidationError({"available_copies": "Available copies cannot exceed total copies."})

    def save(self, *args, **kwargs):
        # Ensure validation rules run when saving via the ORM.
        self.full_clean()
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.name} - {self.subject}"


class PageVisit(models.Model):
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.method} {self.path} @ {self.created_at:%Y-%m-%d %H:%M}"
