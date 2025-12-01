import os
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import create_engine, text


EQUIPMENT_SERVICE_URL = os.getenv("EQUIPMENT_SERVICE_URL", "http://equipment_service:8000")
PROVIDER_SERVICE_URL = os.getenv("PROVIDER_SERVICE_URL", "http://provider_service:8000")
MAINTENANCE_SERVICE_URL = os.getenv("MAINTENANCE_SERVICE_URL", "http://maintenance_service:8000")
REPORT_SERVICE_URL = os.getenv("REPORT_SERVICE_URL", "http://report_service:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@postgres:5432/it_assets")

# Conexión a BD para autenticación
db_engine = create_engine(DATABASE_URL)


class LoginRequest(BaseModel):
    username: str
    password: str


async def _request(method: str, url: str, **kwargs) -> httpx.Response:
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.json()) from exc
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc


app = FastAPI(title="API Gateway", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/auth/login")
async def login(credentials: LoginRequest):
    """Autenticación de usuarios consultando la BD."""
    try:
        with db_engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, username, password_hash, full_name, role, email, is_active
                    FROM users
                    WHERE username = :username AND is_active = TRUE
                """),
                {"username": credentials.username}
            )
            user = result.fetchone()
            
            if not user:
                raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
            
            # En producción usar bcrypt para comparar contraseñas
            # Por ahora comparación directa (solo para desarrollo)
            if user.password_hash != credentials.password:
                raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
            
            return {
                "success": True,
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role,
                    "email": user.email,
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de autenticación: {str(e)}")


@app.get("/dashboard")
async def dashboard():
    response = await _request("GET", f"{REPORT_SERVICE_URL}/reports/dashboard")
    maintenance_resp = await _request("GET", f"{MAINTENANCE_SERVICE_URL}/tasks/upcoming")
    return {
        "metrics": response.json(),
        "upcoming_tasks": maintenance_resp.json(),
    }


@app.get("/equipment")
async def list_equipment(status: str | None = None, location: str | None = None):
    params = {}
    if status:
        params["status"] = status
    if location:
        params["location"] = location
    response = await _request("GET", f"{EQUIPMENT_SERVICE_URL}/equipment", params=params)
    return response.json()


@app.post("/equipment")
async def create_equipment(payload: Dict[str, Any]):
    response = await _request("POST", f"{EQUIPMENT_SERVICE_URL}/equipment", json=payload)
    return response.json()


@app.get("/equipment/{equipment_id}")
async def retrieve_equipment(equipment_id: str):
    response = await _request("GET", f"{EQUIPMENT_SERVICE_URL}/equipment/{equipment_id}")
    return response.json()


@app.put("/equipment/{equipment_id}")
async def update_equipment(equipment_id: str, payload: Dict[str, Any]):
    response = await _request("PUT", f"{EQUIPMENT_SERVICE_URL}/equipment/{equipment_id}", json=payload)
    return response.json()


@app.post("/equipment/{equipment_id}/movements")
async def create_movement(equipment_id: str, payload: Dict[str, Any]):
    response = await _request(
        "POST", f"{EQUIPMENT_SERVICE_URL}/equipment/{equipment_id}/movements", json=payload
    )
    return response.json()


@app.get("/equipment/{equipment_id}/history")
async def equipment_history(equipment_id: str):
    response = await _request("GET", f"{EQUIPMENT_SERVICE_URL}/equipment/{equipment_id}/history")
    return response.json()


@app.get("/equipment/metrics")
async def equipment_metrics():
    response = await _request("GET", f"{EQUIPMENT_SERVICE_URL}/metrics/inventory")
    return response.json()


@app.get("/suppliers")
async def list_suppliers():
    response = await _request("GET", f"{PROVIDER_SERVICE_URL}/suppliers")
    return response.json()


@app.post("/suppliers")
async def create_supplier(payload: Dict[str, Any]):
    response = await _request("POST", f"{PROVIDER_SERVICE_URL}/suppliers", json=payload)
    return response.json()


@app.put("/suppliers/{supplier_id}")
async def update_supplier(supplier_id: str, payload: Dict[str, Any]):
    response = await _request(
        "PUT",
        f"{PROVIDER_SERVICE_URL}/suppliers/{supplier_id}",
        json=payload,
    )
    return response.json()


@app.get("/suppliers/{supplier_id}/contracts")
async def list_contracts(supplier_id: str):
    response = await _request(
        "GET",
        f"{PROVIDER_SERVICE_URL}/suppliers/{supplier_id}/contracts",
    )
    return response.json()


@app.post("/suppliers/{supplier_id}/contracts")
async def create_contract(supplier_id: str, payload: Dict[str, Any]):
    response = await _request(
        "POST",
        f"{PROVIDER_SERVICE_URL}/suppliers/{supplier_id}/contracts",
        json=payload,
    )
    return response.json()


@app.get("/maintenance/upcoming")
async def upcoming_tasks():
    response = await _request("GET", f"{MAINTENANCE_SERVICE_URL}/tasks/upcoming")
    return response.json()


@app.post("/maintenance/tasks")
async def create_task(payload: Dict[str, Any]):
    response = await _request("POST", f"{MAINTENANCE_SERVICE_URL}/tasks", json=payload)
    return response.json()


@app.get("/maintenance/tasks")
async def list_tasks():
    response = await _request("GET", f"{MAINTENANCE_SERVICE_URL}/tasks")
    return response.json()


@app.patch("/maintenance/tasks/{task_id}")
async def update_task(task_id: str, payload: Dict[str, Any]):
    response = await _request(
        "PATCH",
        f"{MAINTENANCE_SERVICE_URL}/tasks/{task_id}",
        json=payload,
    )
    return response.json()


@app.get("/maintenance/logs")
async def list_logs():
    response = await _request("GET", f"{MAINTENANCE_SERVICE_URL}/logs")
    return response.json()


@app.post("/maintenance/logs")
async def create_log(payload: Dict[str, Any]):
    response = await _request("POST", f"{MAINTENANCE_SERVICE_URL}/logs", json=payload)
    return response.json()


@app.get("/reports/export")
async def export_report(format: str = "excel"):
    response = await _request("GET", f"{REPORT_SERVICE_URL}/reports/export", params={"format": format})
    return Response(
        content=response.content,
        media_type=response.headers.get("content-type", "application/octet-stream"),
        headers={"Content-Disposition": response.headers.get("content-disposition", "attachment")},
    )

