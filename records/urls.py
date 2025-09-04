from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet,DiaHealthRecordListView, DiaHealthRecordDetailView
router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")


urlpatterns = [

    # Patient CRUD
    path("", include(router.urls)),
    # DiaHealthRecord GET endpoints
    path("records/", DiaHealthRecordListView.as_view(), name="diahealth-records"),
    path("records/<int:pk>/", DiaHealthRecordDetailView.as_view(), name="diahealth-record-detail"),
]
