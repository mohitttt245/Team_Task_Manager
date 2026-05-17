from django import forms

from accounts.models import User
from core.forms import BootstrapFormMixin

from .models import Project


class ProjectForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "team_members")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "team_members": forms.SelectMultiple(attrs={"size": 8}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["team_members"].queryset = User.objects.filter(role=User.ROLE_MEMBER)


class ProjectTeamForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ("team_members",)
        widgets = {"team_members": forms.SelectMultiple(attrs={"size": 8})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["team_members"].queryset = User.objects.filter(role=User.ROLE_MEMBER)
