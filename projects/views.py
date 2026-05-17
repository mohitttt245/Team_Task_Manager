from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, View

from accounts.mixins import AdminRequiredMixin

from .forms import ProjectForm, ProjectTeamForm
from .models import Project


class ProjectListView(AdminRequiredMixin, ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 8

    def get_queryset(self):
        queryset = Project.objects.select_related("created_by").prefetch_related("team_members", "tasks")
        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(team_members__username__icontains=search)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_form = ProjectForm()
        context["project_form"] = project_form
        context["member_options"] = project_form.fields["team_members"].queryset
        context["search"] = self.request.GET.get("search", "")
        return context


class ProjectCreateView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m()
            messages.success(request, "Project created successfully.")
        else:
            messages.error(request, "Unable to create the project. Please review the form.")
        return redirect("projects:list")


class ProjectUpdateView(AdminRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully.")
        else:
            messages.error(request, "Unable to update the project.")
        return redirect("projects:list")


class ProjectDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        project.delete()
        messages.warning(request, "Project deleted successfully.")
        return redirect("projects:list")


class TeamManagementView(AdminRequiredMixin, TemplateView):
    template_name = "projects/team_management.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = Project.objects.prefetch_related("team_members").all()
        search = self.request.GET.get("search", "").strip()
        if search:
            projects = projects.filter(
                Q(name__icontains=search)
                | Q(team_members__username__icontains=search)
                | Q(team_members__email__icontains=search)
            ).distinct()

        paginator = Paginator(projects, 6)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        project_forms = [
            {
                "project": project,
                "form": ProjectTeamForm(instance=project, prefix=f"project-{project.pk}"),
            }
            for project in page_obj
        ]

        context["page_obj"] = page_obj
        context["project_forms"] = project_forms
        context["search"] = search
        return context


class TeamManagementUpdateView(AdminRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        form = ProjectTeamForm(request.POST, instance=project, prefix=f"project-{project.pk}")
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated team members for {project.name}.")
        else:
            messages.error(request, "Unable to update team members.")
        return redirect("projects:team")
