from rest_framework import serializers
from .models import DiaHealthRecord
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id",
            "patient_code",
            "first_name",
            "last_name",
            "gender",
            "age",
            "created_at",
            "updated_at",
        ]

class DiaHealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaHealthRecord
        fields = [
            "id",
            "patient",
            "gender",
            "age",
            "pulse_rate",
            "systolic_bp",
            "diastolic_bp",
            "glucose",
            "height",
            "weight",
            "bmi",
            "family_diabetes",
            "hypertensive",
            "family_hypertension",
            "cvd",
            "stroke",
            "diabetic",
            "created_at",
        ]
        depth = 1   # expands patient info (patient_code, etc.)
