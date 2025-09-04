from django.shortcuts import render

# Create your views here.
import pandas as pd
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from .serializers import (
    PatientFeaturesSerializer,
    PredictResponseSerializer,
)
from .model_store import gb_model, lr_model, explainer, FEATURES, LOW_T, HIGH_T

def band_from_prob(p):
    if p < LOW_T: return "Low"
    if p < HIGH_T: return "Medium"
    return "High"

@extend_schema(
    tags=["Prediction"],
    request=PatientFeaturesSerializer,
    responses={
        200: OpenApiResponse(
            response=PredictResponseSerializer,
            description="Risk score + risk band from Gradient Boosting, with SHAP-based explanation from Logistic Regression."
        ),
        400: OpenApiResponse(description="Validation error"),
    },
    examples=[
        OpenApiExample(
            'Valid request',
            value={
                "age": 54,
                "gender": "Male",
                "pulse_rate": 78,
                "systolic_bp": 132,
                "diastolic_bp": 86,
                "glucose": 7.8,
                "height": 1.72,
                "weight": 84.0,
                "bmi": 28.4,
                "family_diabetes": 1,
                "hypertensive": 1,
                "family_hypertension": 1,
                "cvd": 1,
                "stroke": 0
            },
            request_only=True
        ),
        OpenApiExample(
            'Successful response',
            value={
                "risk_score": 0.7312,
                "risk_band": "High",
                "explanation": [
                    {"feature":"glucose","value":"7.8","shap_abs":0.41,"direction":"↑risk"},
                    {"feature":"bmi","value":"28.4","shap_abs":0.19,"direction":"↑risk"},
                    {"feature":"family_diabetes","value":"1","shap_abs":0.12,"direction":"↑risk"},
                    {"feature":"systolic_bp","value":"132","shap_abs":0.07,"direction":"↑risk"},
                    {"feature":"gender","value":"Male","shap_abs":0.04,"direction":"↑risk"}
                ],
                "model_versions": {"gradient_boosting":"v1.0","logistic_regression":"v1.0"}
            },
            response_only=True
        )
    ],
)
class PredictView(APIView):
    """
    POST /api/predict
    Returns risk_score (GBM), risk_band, and SHAP-based explanation (LR).
    """
    def post(self, request):
        from .serializers import PatientFeaturesSerializer
        ser = PatientFeaturesSerializer(data=request.data)
        if not ser.is_valid():
            return Response({"errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = ser.validated_data
        # unify cvd
        if 'cvd' not in data:
            data['cvd'] = int(data.get('cardiovascular_disease', 0))

        # Build 1-row DataFrame in training feature order
        row = pd.DataFrame([[data.get(f, 0) for f in FEATURES]], columns=FEATURES)

        # 1) Risk (GBM)
        prob = float(gb_model.predict_proba(row)[0, 1])
        band = band_from_prob(prob)

        # 2) SHAP explanation (LR)
        X_trans = lr_model.named_steps["preprocess"].transform(row)
        sv = explainer(X_trans)
        vals = np.abs(getattr(sv, "values", sv)[0])
        order = np.argsort(vals)[::-1][:5]

        explanation = []
        for i in order:
            sign = getattr(sv, "values", sv)[0, i]
            explanation.append({
                "feature": FEATURES[i] if i < len(FEATURES) else f"f{i}",
                "value": str(row.iloc[0, i]) if i < len(FEATURES) else None,
                "shap_abs": float(vals[i]),
                "direction": "↑risk" if sign > 0 else "↓risk",
            })

        return Response({
            "risk_score": round(prob, 4),
            "risk_band": band,
            "explanation": explanation,
            "model_versions": {"gradient_boosting": "v1.0", "logistic_regression": "v1.0"}
        }, status=200)
