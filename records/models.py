from django.db import models

# Create your models here.

class Patient(models.Model):
    GENDER_CHOICES = (("Male", "Male"), ("Female", "Female"))

    # basic identifying info (do NOT store PII you don’t need)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    # light-contact or internal code (avoid sensitive PII in real deployments)
    patient_code = models.CharField(max_length=32, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # auto-updates on save

    class Meta:
        indexes = [models.Index(fields=["patient_code"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient_code} - {self.last_name}, {self.first_name}"

class DiaHealthRecord(models.Model):
    """
    One row of the DiaHealth dataset for a given patient.
    Binary fields are 0/1 per the dataset.
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="records")

    # Demographic
    gender = models.CharField(max_length=6, choices=Patient.GENDER_CHOICES)
    age = models.FloatField()

    # Vital signs
    pulse_rate = models.FloatField()
    systolic_bp = models.FloatField()
    diastolic_bp = models.FloatField()

    # Biochemical
    glucose = models.FloatField()  # fasting mmol/L (dataset units)

    # Anthropometric
    height = models.FloatField()   # meters
    weight = models.FloatField()   # kg
    bmi = models.FloatField()

    # Family / clinical history (0/1)
    family_diabetes = models.IntegerField()
    hypertensive = models.IntegerField()
    family_hypertension = models.IntegerField()
    cvd = models.IntegerField()
    stroke = models.IntegerField()

    # Outcome
    diabetic = models.IntegerField()  # 0=non-diabetic, 1=diabetic (ground truth label)

    # housekeeping
    source = models.CharField(max_length=64, default="DiaHealth 2024")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["diabetic", "age", "bmi"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"DiaHealthRecord(patient={self.patient.patient_code}, diabetic={self.diabetic})"
