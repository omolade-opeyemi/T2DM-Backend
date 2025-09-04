from rest_framework import serializers

class PatientFeaturesSerializer(serializers.Serializer):
    age = serializers.FloatField()
    gender = serializers.ChoiceField(choices=["Male","Female"])
    pulse_rate = serializers.FloatField()
    systolic_bp = serializers.FloatField()
    diastolic_bp = serializers.FloatField()
    glucose = serializers.FloatField()
    height = serializers.FloatField()
    weight = serializers.FloatField()
    bmi = serializers.FloatField()
    family_diabetes = serializers.IntegerField()
    hypertensive = serializers.IntegerField()
    family_hypertension = serializers.IntegerField()
    cvd = serializers.IntegerField(required=False)
    cardiovascular_disease = serializers.IntegerField(required=False)
    stroke = serializers.IntegerField()
    diabetic = serializers.IntegerField(required=False)  # optional at inference

    def validate(self, data):
        if 'cvd' not in data:
            data['cvd'] = int(data.get('cardiovascular_disease', 0))
        return data

class ExplanationItemSerializer(serializers.Serializer):
    feature = serializers.CharField()
    value = serializers.CharField(allow_null=True)  # string for swagger simplicity
    shap_abs = serializers.FloatField()
    direction = serializers.ChoiceField(choices=["↑risk", "↓risk"])

class PredictResponseSerializer(serializers.Serializer):
    risk_score = serializers.FloatField()
    risk_band = serializers.ChoiceField(choices=["Low", "Medium", "High"])
    explanation = ExplanationItemSerializer(many=True)
    model_versions = serializers.DictField(child=serializers.CharField())
