from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from .models import Project, Scrum, Task
from .serializers import (
    LoginSerializer,
    ProjectSerializer,
    ScrumSerializer,
    ScrumSerializerPOST,
    TaskSerializer,
    TaskSerializerPOST,
)
from .permissions import IsProjectManager, IsProjectManagerForUnsafeMethods


def send_email(subject, html_file, recipient_list, context):
    html_message = render_to_string(html_file, context)
    send_mail(
        subject=subject,
        message="",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient_list,
        html_message=html_message,
    )


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
            )
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": str(token)}, status=status.HTTP_200_OK)
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectView(APIView):
    permission_classes = [IsAuthenticated, IsProjectManager]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new project, send email to all employees"""
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            employees = serializer.validated_data["employees"]
            employee_list = [emp.strip() for emp in employees.split(",")]

            send_email(
                subject=f"New Project Assigned: {serializer.validated_data['title']}",
                html_file="project_created.html",
                recipient_list=employee_list,
                context={
                    "project_title": serializer.validated_data["title"],
                    "project_description": serializer.validated_data["description"],
                    "employees": employee_list,
                },
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Update project, send email to all employees"""
        project = Project.objects.get(id=request.data["id"])
        serializer = ProjectSerializer(project, data=request.data)

        if serializer.is_valid():
            serializer.save()
            employee_list = [
                emp.strip() for emp in serializer.validated_data["employees"].split(",")
            ]
            send_email(
                subject=f"Project Updated: {serializer.validated_data['title']}",
                html_file="project_created.html",
                recipient_list=employee_list,
                context={
                    "project_title": serializer.validated_data["title"],
                    "project_description": serializer.validated_data["description"],
                    "employees": employee_list,
                },
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Update project, send email to all employees"""
        project = Project.objects.get(id=request.data["id"])
        serializer = ProjectSerializer(project, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            employee_list = [
                emp.strip() for emp in serializer.validated_data["employees"].split(",")
            ]
            send_email(
                subject=f"Project Updated: {serializer.validated_data['title']}",
                html_file="project_created.html",
                recipient_list=employee_list,
                context={
                    "project_title": serializer.validated_data["title"],
                    "project_description": serializer.validated_data["description"],
                    "employees": employee_list,
                },
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Delete project, send email to all employees"""
        project = Project.objects.get(id=request.data["id"])
        employee_list = [emp.strip() for emp in project.employees.split(",")]
        name = project.title
        project.delete()

        send_email(
            subject=f"Project {name} deleted",
            html_file="project_deleted.html",
            recipient_list=employee_list,
            context={
                "project_title": name,
            },
        )

        return Response({"message": f"{name} deleted successfully"})


class ScrumView(APIView):
    permission_classes = [IsAuthenticated, IsProjectManagerForUnsafeMethods]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """Get all scrums"""
        scrums = Scrum.objects.all()
        serializer = ScrumSerializer(scrums, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new scrum, send email to all employees"""
        serializer = ScrumSerializerPOST(data=request.data)
        if serializer.is_valid():
            serializer.save()

            project_id = serializer.data["project"]
            project = Project.objects.get(id=project_id)
            employees = project.employees

            send_email(
                subject=f"New Scrum Created: {serializer.validated_data['title']}",
                html_file="scrum.html",
                recipient_list=[emp.strip() for emp in employees.split(",")],
                context={
                    "scrum_title": serializer.validated_data["title"],
                    "scrum_description": serializer.validated_data["description"],
                    "start_date": serializer.validated_data["start_date"],
                    "end_date": serializer.validated_data["end_date"],
                    "created_by": serializer.validated_data["created_by"],
                },
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Update scrum, send email to all employees"""
        scrum = Scrum.objects.get(id=request.data["id"])
        serializer = ScrumSerializerPOST(scrum, data=request.data)

        if serializer.is_valid():
            serializer.save()

            project_id = serializer.data["project"]
            project = Project.objects.get(id=project_id)
            employees = project.employees
            send_email(
                subject=f"Scrum Updated: {serializer.validated_data['title']}",
                html_file="scrum.html",
                recipient_list=[emp.strip() for emp in employees.split(",")],
                context={
                    "scrum_title": serializer.validated_data["title"],
                    "scrum_description": serializer.validated_data["description"],
                    "start_date": serializer.validated_data["start_date"],
                    "end_date": serializer.validated_data["end_date"],
                    "created_by": serializer.validated_data["created_by"],
                },
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Update scrum, send email to all employees"""
        scrum = Scrum.objects.get(id=request.data["id"])
        serializer = ScrumSerializerPOST(scrum, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            project_id = serializer.data["project"]
            project = Project.objects.get(id=project_id)
            employees = project.employees
            send_email(
                subject=f"Scrum Updated: {serializer.validated_data['title']}",
                html_file="scrum.html",
                recipient_list=[emp.strip() for emp in employees.split(",")],
                context={
                    "scrum_title": serializer.validated_data["title"],
                    "scrum_description": serializer.validated_data["description"],
                    "start_date": serializer.validated_data["start_date"],
                    "end_date": serializer.validated_data["end_date"],
                    "created_by": serializer.validated_data["created_by"],
                },
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Delete scrum, send email to all employees"""
        scrum = Scrum.objects.get(id=request.data["id"])
        scrum_name = scrum.title

        project_id = scrum.project.id
        project = Project.objects.get(id=project_id)
        employees = project.employees

        send_email(
            subject=f"Scrum Deleted: {scrum_name}",
            html_file="scrum_deleted.html",
            recipient_list=[emp.strip() for emp in employees.split(",")],
        )

        scrum.delete()

        return Response(
            {"message": f"{scrum_name} deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class TaskView(APIView):
    permission_classes = [IsAuthenticated, IsProjectManagerForUnsafeMethods]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """Get all tasks"""
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new task, send email to the person assigned"""
        serializer = TaskSerializerPOST(data=request.data)
        if serializer.is_valid():
            serializer.save()

            user_id = serializer.data["assigned_to"]
            user_email = User.objects.get(id=user_id).email

            send_email(
                subject=f"New Task Assigned: {serializer.validated_data['title']}",
                html_file="task.html",
                recipient_list=[user_email],
                context={
                    "task_title": serializer.validated_data["title"],
                    "task_description": serializer.validated_data["description"],
                    "assigned_by": serializer.validated_data["assigned_by"],
                    "end_date": serializer.validated_data["end_date"],
                    "status": serializer.validated_data["status"],
                },
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Update task, send email to the person assigned"""
        task = Task.objects.get(id=request.data["id"])
        serializer = TaskSerializerPOST(task, data=request.data)

        if serializer.is_valid():
            serializer.save()

            user_id = serializer.data["assigned_to"]
            user_email = User.objects.get(id=user_id).email

            send_email(
                subject=f"Task Updated: {serializer.validated_data['title']}",
                html_file="task.html",
                recipient_list=[user_email],
                context={
                    "task_title": serializer.validated_data["title"],
                    "task_description": serializer.validated_data["description"],
                    "assigned_by": serializer.validated_data["assigned_by"],
                    "end_date": serializer.validated_data["end_date"],
                    "status": serializer.validated_data["status"],
                },
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Update task, send email to the person assigned"""
        task = Task.objects.get(id=request.data["id"])
        serializer = TaskSerializerPOST(task, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            user_id = serializer.data["assigned_to"]
            user_email = User.objects.get(id=user_id).email

            send_email(
                subject=f"Task Updated: {serializer.validated_data['title']}",
                html_file="task.html",
                recipient_list=[user_email],
                context={
                    "task_title": serializer.validated_data["title"],
                    "task_description": serializer.validated_data["description"],
                    "assigned_by": serializer.validated_data["assigned_by"],
                    "end_date": serializer.validated_data["end_date"],
                    "status": serializer.validated_data["status"],
                },
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Delete task, send email to the person assigned"""
        task = Task.objects.get(id=request.data["id"])
        user_email = task.assigned_to.email
        task_name = task.title
        task.delete()

        send_email(
            subject=f"Task Deleted: {task_name}",
            html_file="task_deleted.html",
            recipient_list=[user_email],
            context={
                "task_title": task_name,
            },
        )

        return Response(
            {"message": f"{task_name} deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
