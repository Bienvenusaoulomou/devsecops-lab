from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
import pickle
import subprocess


app = FastAPI(
    title="DevSecOps Security Demo API",
    description="Application de démonstration pour le pipeline DevSecOps",
    version="1.0.0",
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Cache-Control"] = "no-store"

        return response


app.add_middleware(SecurityHeadersMiddleware)


class Patient(BaseModel):
    name: str
    age: int
    email: str


patients = {
    1: {
        "id": 1,
        "name": "Alice Martin",
        "age": 34,
        "email": "alice@example.com",
    },
    2: {
        "id": 2,
        "name": "Bob Dupont",
        "age": 45,
        "email": "bob@example.com",
    },
}


@app.get("/")
def root():
    return {
        "application": "DevSecOps Security Demo API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/patients")
def get_patients():
    return list(patients.values())


@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):
    patient = patients.get(patient_id)

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


@app.post("/patients", status_code=201)
def create_patient(patient: Patient):
    patient_id = max(patients.keys(), default=0) + 1

    new_patient = {
        "id": patient_id,
        **patient.model_dump(),
    }

    patients[patient_id] = new_patient

    return new_patient


# ============================================================
# TEST NEGATIF SONARQUBE - 6 QUALITY GATE CONDITIONS
# ============================================================


# 1. COVERAGE
# Cette fonction ne sera volontairement pas couverte par pytest.
@app.get("/negative/coverage")
def negative_coverage():
    value = 10
    result = value * 2
    return {"result": result}


# 2. DUPLICATION
# Blocs volontairement similaires pour augmenter la duplication.
@app.get("/negative/duplicate-a")
def negative_duplicate_a():
    data = {
        "name": "duplicate-test",
        "status": "active",
        "type": "test",
        "category": "negative",
        "description": "duplicated block for SonarQube",
        "value": 100,
        "enabled": True,
        "source": "sonarqube",
        "environment": "test",
    }
    return data


@app.get("/negative/duplicate-b")
def negative_duplicate_b():
    data = {
        "name": "duplicate-test",
        "status": "active",
        "type": "test",
        "category": "negative",
        "description": "duplicated block for SonarQube",
        "value": 100,
        "enabled": True,
        "source": "sonarqube",
        "environment": "test",
    }
    return data


# 3. MAINTAINABILITY / CODE SMELL
# Fonction volontairement complexe et difficile à maintenir.
@app.get("/negative/maintainability")
def negative_maintainability(value: int = 0):
    result = 0

    if value > 0:
        if value > 10:
            if value > 20:
                if value > 30:
                    if value > 40:
                        if value > 50:
                            if value > 60:
                                if value > 70:
                                    result = 8
                                else:
                                    result = 7
                            else:
                                result = 6
                        else:
                            result = 5
                    else:
                        result = 4
                else:
                    result = 3
            else:
                result = 2
        else:
            result = 1

    return {"result": result}


# 4. RELIABILITY / BUG
# Division volontairement impossible.
@app.get("/negative/bug")
def negative_bug():
    divisor = 0
    result = 100 / divisor
    return {"result": result}


# 5. SECURITY / VULNERABILITY
# Désérialisation non sûre de données contrôlées par l'utilisateur.
@app.get("/negative/vulnerability")
def negative_vulnerability(data: str):
    decoded_data = data.encode()
    result = pickle.loads(decoded_data)
    return {"result": str(result)}


# 6. SECURITY HOTSPOT
# Exécution d'une commande construite à partir d'une entrée utilisateur.
@app.get("/negative/security-hotspot")
def negative_security_hotspot(command: str):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )

    return {
        "stdout": result.stdout,
        "returncode": result.returncode,
    }