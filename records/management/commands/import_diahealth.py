from django.core.management.base import BaseCommand
from records.models import Patient, DiaHealthRecord
import pandas as pd
from pathlib import Path


def to_int01(val, default=0):
    """Coerce value to {0,1} with safe fallbacks."""
    if pd.isna(val):
        return int(default)
    try:
        v = str(val).strip().lower()
        if v in {"1", "yes", "y", "true", "t"}:
            return 1
        if v in {"0", "no", "n", "false", "f"}:
            return 0
        # numeric-ish strings
        return 1 if float(v) >= 0.5 else 0
    except Exception:
        return int(default)


class Command(BaseCommand):
    help = "Import DiaHealth CSV into DB (creates Patients + DiaHealthRecord rows)."

    def add_arguments(self, parser):
        parser.add_argument("--csv", type=str,
                            default="Diabetes_Final_Data_V2.csv")

    def handle(self, *args, **opts):
        csv_path = Path(opts["csv"])
        df = pd.read_csv(csv_path)

        # Show columns for quick sanity check
        self.stdout.write(f"Available columns: {list(df.columns)}")

        # Exact dataset columns (adjust names here if needed)
        # Map cardiovascular_disease -> cvd during import
        required = [
            "age", "gender", "pulse_rate", "systolic_bp", "diastolic_bp", "glucose",
            "height", "weight", "bmi", "family_diabetes", "hypertensive",
            "family_hypertension", "cardiovascular_disease", "stroke", "diabetic"
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            self.stderr.write(f"Missing columns: {missing}")
            return

        for i, row in df.iterrows():
            # Minimal patient row (avoid storing extra PII)
            code = f"P{100000+i}"
            p, _ = Patient.objects.get_or_create(
                patient_code=code,
                defaults=dict(
                    first_name="Anon",
                    last_name=f"#{i}",
                    gender=str(row["gender"]).strip().title(
                    ) if pd.notna(row["gender"]) else "Male",
                    age=int(row["age"]) if pd.notna(row["age"]) else 40,
                ),
            )

            DiaHealthRecord.objects.create(
                patient=p,
                # Demographic
                gender=p.gender,
                age=float(row["age"]),

                # Vital signs
                pulse_rate=float(row["pulse_rate"]),
                systolic_bp=float(row["systolic_bp"]),
                diastolic_bp=float(row["diastolic_bp"]),

                # Biochemical
                glucose=float(row["glucose"]),

                # Anthropometric
                height=float(row["height"]),
                weight=float(row["weight"]),
                bmi=float(row["bmi"]),

                # Family/clinical history (coerce to 0/1 safely)
                family_diabetes=to_int01(row["family_diabetes"]),
                hypertensive=to_int01(row["hypertensive"]),
                family_hypertension=to_int01(row["family_hypertension"]),
                # <-- mapped here
                cvd=to_int01(row["cardiovascular_disease"]),
                stroke=to_int01(row["stroke"]),

                # Outcome
                diabetic=to_int01(row["diabetic"]),
            )

        self.stdout.write(self.style.SUCCESS("Import complete."))
