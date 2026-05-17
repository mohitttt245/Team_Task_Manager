from django.conf import settings
from django.contrib.auth import login, logout
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.serializers import LoginSerializer, SignupSerializer, UserSerializer, build_auth_payload
from dashboard.serializers import ActivityLogSerializer
from dashboard.services import get_admin_dashboard_data, get_member_dashboard_data
from projects.models import Project
from projects.serializers import ProjectSerializer
from tasks.models import Task
from tasks.serializers import TaskSerializer, TaskStatusUpdateSerializer

from .permissions import IsAdminOrAssignedMember, IsAdminRole


class SignupAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        payload = build_auth_payload(user)
        response = Response(payload, status=status.HTTP_201_CREATED)
        set_auth_cookies(response, payload)
        return response


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        payload = build_auth_payload(user)
        response = Response(payload, status=status.HTTP_200_OK)
        set_auth_cookies(response, payload)
        return response


class LogoutAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh") or request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        logout(request)
        response = Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class ProjectListAPIView(generics.ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = Project.objects.select_related("created_by").prefetch_related("team_members")
        if self.request.user.role == User.ROLE_MEMBER:
            queryset = queryset.filter(team_members=self.request.user)
        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(team_members__username__icontains=search)
            ).distinct()
        return queryset


class ProjectCreateAPIView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminRole]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectUpdateAPIView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminRole]
    http_method_names = ["put", "patch"]


class ProjectDeleteAPIView(generics.DestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminRole]


class TaskListAPIView(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.select_related("project", "assigned_to", "created_by")
        if self.request.user.role == User.ROLE_MEMBER:
            queryset = queryset.filter(assigned_to=self.request.user)

        search = self.request.GET.get("search", "").strip()
        status_filter = self.request.GET.get("status", "").strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(project__name__icontains=search)
            )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class TaskCreateAPIView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAdminRole]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskUpdateAPIView(generics.UpdateAPIView):
    queryset = Task.objects.select_related("assigned_to", "project")
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAssignedMember]
    http_method_names = ["put", "patch"]

    def get_serializer_class(self):
        if self.request.user.role == User.ROLE_MEMBER:
            return TaskStatusUpdateSerializer
        return TaskSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        if request.user.role == User.ROLE_MEMBER and set(request.data.keys()) - {"status"}:
            return Response(
                {"detail": "Members can only update task status."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)


class TaskDeleteAPIView(generics.DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAdminRole]


class DashboardAPIView(APIView):
    def get(self, request):
        if request.user.role == User.ROLE_ADMIN:
            data = get_admin_dashboard_payload()
        else:
            data = get_member_dashboard_payload(request.user)
        return Response(data, status=status.HTTP_200_OK)


def set_auth_cookies(response, payload):
    response.set_cookie(
        "access_token",
        payload["access"],
        httponly=True,
        samesite="Lax",
        secure=not settings.DEBUG,
    )
    response.set_cookie(
        "refresh_token",
        payload["refresh"],
        httponly=True,
        samesite="Lax",
        secure=not settings.DEBUG,
    )


def get_admin_dashboard_payload():
    data = get_admin_dashboard_data()
    return {
        "role": User.ROLE_ADMIN,
        "stats": {
            "total_projects": data["total_projects"],
            "total_tasks": data["total_tasks"],
            "completed_tasks": data["completed_tasks"],
            "pending_tasks": data["pending_tasks"],
            "overdue_tasks": data["overdue_tasks"],
        },
        "status_breakdown": data["status_breakdown"],
        "priority_breakdown": data["priority_breakdown"],
        "recent_activities": ActivityLogSerializer(data["recent_activities"], many=True).data,
        "overdue_tasks": TaskSerializer(data["overdue_task_list"], many=True).data,
    }


def get_member_dashboard_payload(user):
    data = get_member_dashboard_data(user)
    return {
        "role": User.ROLE_MEMBER,
        "stats": {
            "my_tasks": data["my_tasks"],
            "completed_tasks": data["completed_tasks"],
            "pending_tasks": data["pending_tasks"],
            "overdue_tasks": data["overdue_tasks"],
        },
        "status_breakdown": data["status_breakdown"],
        "recent_activities": ActivityLogSerializer(data["recent_activities"], many=True).data,
        "upcoming_deadlines": TaskSerializer(data["upcoming_deadlines"], many=True).data,
        "today_focus": TaskSerializer(data["today_focus"], many=True).data,
    }
