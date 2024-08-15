import re
from rest_framework import serializers
from .models import Project


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"

    def validate_employees(self, data):
        pattern = r'^[a-zA-Z0-9_.+-]+@intendcareer\.com$'
        emails = [x.strip() for x in data.split(",")]

        def isEmailValid(email):
            pattern = r'^[a-zA-Z0-9_.+-]+@intendcareer\.com$'
            if re.match(pattern, email):
                return True
            return False

        invalid_emails = [email for email in emails if not isEmailValid(email)]

        if invalid_emails:
            raise serializers.ValidationError(
                f"The following email(s) are invalid: {', '.join(invalid_emails)}"
            )

        return data
