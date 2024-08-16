from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.contrib.auth import authenticate

from .models import Project, Scrum, Task
from .serializers import LoginSerializer, ProjectSerializer, ScrumSerializer, ScrumSerializerPOST, TaskSerializer, TaskSerializerPOST
from .permissions import IsProjectManager, IsProjectManagerForUnsafeMethods


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': str(token)}, status=status.HTTP_200_OK)
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        project = Project.object.get(id=request.data["id"])
        serializer = ProjectSerializer(project, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        project = Project.objects.get(id=request.data["id"])
        serializer = ProjectSerializer(project, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        project = Project.objects.get(id=request.data["id"])
        name = project.name
        project.delete()

        return Response({"message": f"{name} deleted successfully"})


class ScrumView(APIView):
    permission_classes = [IsAuthenticated, IsProjectManagerForUnsafeMethods]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        scrums = Scrum.objects.all()
        serializer = ScrumSerializer(scrums, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ScrumSerializerPOST(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        scrum = Scrum.objects.get(id=request.data['id'])
        serializer = ScrumSerializerPOST(scrum, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        scrum = Scrum.objects.get(id=request.data['id'])
        serializer = ScrumSerializerPOST(scrum, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        scrum = Scrum.objects.get(id=request.data['id'])
        scrum_name = scrum.title

        return Response({"message": f"{scrum_name} deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class TaskView(APIView):
    permission_classes = [IsAuthenticated, IsProjectManagerForUnsafeMethods]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TaskSerializerPOST(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        task = Task.objects.get(id=request.data['id'])
        serializer = TaskSerializerPOST(task, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        task = Task.objects.get(id=request.data['id'])
        serializer = TaskSerializerPOST(task, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        task = Task.objects.get(id=request.data['id'])
        task_name = task.title
        task.delete()

        return Response({"message": f"{task_name} deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
