from rest_framework import serializers
from sheets.models import Sheet, Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name"]


class SheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sheet
        # Internal verifier notes and performance ratings stay off the employee's hours page.
        exclude = [
            "manager_level_1_comment",
            "manager_level_2_comment",
            "performance_form_aspect_m1",
            "performance_form_aspect_m2",
        ]
