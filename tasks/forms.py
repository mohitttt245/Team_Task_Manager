from django import forms

from accounts.models import User
from core.forms import BootstrapFormMixin
from projects.models import Project

from .models import Task


class TaskForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = ("title", "description", "project", "assigned_to", "status", "priority", "due_date")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = Project.objects.prefetch_related("team_members").all()
        self.fields["assigned_to"].queryset = User.objects.filter(role=User.ROLE_MEMBER)


class TaskStatusForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = ("status",)
