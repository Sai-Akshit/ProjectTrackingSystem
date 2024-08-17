import re
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Scrum, Task


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"

    def validate_employees(self, data):
        pattern = r"^[a-zA-Z0-9_.+-]+@intendcareer\.com$"
        emails = [x.strip() for x in data.split(",")]

        def isEmailValid(email):
            pattern = r"^[a-zA-Z0-9_.+-]+@intendcareer\.com$"
            if re.match(pattern, email):
                return True
            return False

        invalid_emails = [email for email in emails if not isEmailValid(email)]

        if invalid_emails:
            raise serializers.ValidationError(
                f"The following email(s) are invalid: {', '.join(invalid_emails)}"
            )

        return data


class ProjectSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "title"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class ScrumSerializer(serializers.ModelSerializer):
    project = ProjectSerializer1()
    created_by = UserSerializer()

    class Meta:
        model = Scrum
        fields = "__all__"


class ScrumSerializerPOST(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Scrum
        exclude = ["created", "modified"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["created", "modified"]


class TaskSerializerPOST(serializers.ModelSerializer):
    scrum = serializers.PrimaryKeyRelatedField(queryset=Scrum.objects.all())
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    assigned_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Task
        exclude = ["created", "modified"]
