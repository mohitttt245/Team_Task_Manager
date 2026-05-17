from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import User
from projects.models import Project
from tasks.models import Task


class TeamTaskManagerAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
            role=User.ROLE_ADMIN,
        )
        self.member_user = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="StrongPass123",
            role=User.ROLE_MEMBER,
        )
        self.other_member = User.objects.create_user(
            username="member2",
            email="member2@example.com",
            password="StrongPass123",
            role=User.ROLE_MEMBER,
        )
        self.project = Project.objects.create(
            name="Client Portal",
            description="Portal redesign",
            created_by=self.admin_user,
        )
        self.project.team_members.set([self.member_user, self.other_member])
        self.task = Task.objects.create(
            title="Write release notes",
            description="Prepare launch release notes",
            project=self.project,
            assigned_to=self.member_user,
            created_by=self.admin_user,
            status=Task.STATUS_TODO,
            priority=Task.PRIORITY_HIGH,
            due_date=date.today() + timedelta(days=2),
        )

    def test_member_cannot_create_project(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.post(
            reverse("api-project-create"),
            {
                "name": "Unauthorized Project",
                "description": "Should fail",
                "team_member_ids": [self.member_user.pk],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_project(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            reverse("api-project-create"),
            {
                "name": "Growth Sprint",
                "description": "Sprint planning",
                "team_member_ids": [self.member_user.pk],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.filter(name="Growth Sprint").count(), 1)

    def test_member_sees_only_assigned_tasks(self):
        Task.objects.create(
            title="Hidden Task",
            description="Assigned elsewhere",
            project=self.project,
            assigned_to=self.other_member,
            created_by=self.admin_user,
            status=Task.STATUS_TODO,
            priority=Task.PRIORITY_LOW,
            due_date=date.today() + timedelta(days=5),
        )
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(reverse("api-tasks"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Write release notes")

    def test_member_can_only_update_task_status(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.put(
            reverse("api-task-update", kwargs={"pk": self.task.pk}),
            {"title": "Changed title", "status": Task.STATUS_DONE},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(
            reverse("api-task-update", kwargs={"pk": self.task.pk}),
            {"status": Task.STATUS_DONE},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.STATUS_DONE)

    def test_dashboard_returns_role_specific_payload(self):
        self.client.force_authenticate(user=self.admin_user)
        admin_response = self.client.get(reverse("api-dashboard"))
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data["role"], User.ROLE_ADMIN)
        self.assertIn("total_projects", admin_response.data["stats"])

        self.client.force_authenticate(user=self.member_user)
        member_response = self.client.get(reverse("api-dashboard"))
        self.assertEqual(member_response.status_code, status.HTTP_200_OK)
        self.assertEqual(member_response.data["role"], User.ROLE_MEMBER)
        self.assertIn("my_tasks", member_response.data["stats"])
