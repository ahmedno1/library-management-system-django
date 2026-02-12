from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    # stars submitted via hidden input controlled by the star UI (0.5 increments)
    stars = forms.DecimalField(
        max_digits=3,
        decimal_places=1,
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(),
        label="Rating",
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Share your thoughts (optional)",
            }
        ),
        label="Comment",
    )

    class Meta:
        model = Review
        fields = ["stars", "comment"]
