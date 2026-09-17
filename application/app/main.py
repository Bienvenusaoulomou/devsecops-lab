from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel


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