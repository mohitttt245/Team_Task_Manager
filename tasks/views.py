from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, View

from accounts.mixins import AdminRequiredMixin, LoginRequiredMixin

from .forms import TaskForm, TaskStatusForm
from .models import Task


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        queryset = Task.objects.select_related("project", "assigned_to", "created_by")
        user = self.request.user
        if user.is_member_role:
            queryset = queryset.filter(assigned_to=user)

        search = self.request.GET.get("search", "").strip()
        status = self.request.GET.get("status", "").strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(project__name__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_form = TaskForm()
        context["task_form"] = task_form
        context["project_options"] = task_form.fields["project"].queryset
        context["member_options"] = task_form.fields["assigned_to"].queryset
        context["status_choices"] = Task.STATUS_CHOICES
        context["priority_choices"] = Task.PRIORITY_CHOICES
        context["search"] = self.request.GET.get("search", "")
        context["selected_status"] = self.request.GET.get("status", "")
        return context


class TaskCreateView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, "Task created successfully.")
        else:
            messages.error(request, "Unable to create the task. Please review the form.")
        return redirect("tasks:list")


class TaskUpdateView(AdminRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
        else:
            messages.error(request, "Unable to update the task.")
        return redirect("tasks:list")


class TaskDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        messages.warning(request, "Task deleted successfully.")
        return redirect("tasks:list")


class TaskStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        if request.user.is_member_role and task.assigned_to_id != request.user.pk:
            messages.error(request, "You can only update your own tasks.")
            return redirect("tasks:list")

        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task status updated successfully.")
        else:
            messages.error(request, "Unable to update task status.")
        return redirect("tasks:list")
