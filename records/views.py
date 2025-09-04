from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import DiaHealthRecord
from .serializers import DiaHealthRecordSerializer
from rest_framework import viewsets
from .models import Patient
from .serializers import PatientSerializer

@extend_schema(
    tags=["DiaHealth"],
    description="List all DiaHealth records in the database."
)

@extend_schema(
    tags=["Patient"],
    description="CRUD API for managing Patient records."
)

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by("-created_at")
    serializer_class = PatientSerializer

class DiaHealthRecordListView(generics.ListAPIView):
    queryset = DiaHealthRecord.objects.all().order_by("-created_at")
    serializer_class = DiaHealthRecordSerializer

@extend_schema(
    tags=["DiaHealth"],
    description="Retrieve a single DiaHealth record by ID."
)
class DiaHealthRecordDetailView(generics.RetrieveAPIView):
    queryset = DiaHealthRecord.objects.all()
    serializer_class = DiaHealthRecordSerializer
