from typing import List
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from common import models, schemas
from common.database import get_session


app = FastAPI(
    title="Equipment Service",
    version="1.0.0",
    description="Gestión de inventario y ciclo de vida de equipos de TI.",
)


@app.post("/equipment", response_model=schemas.EquipmentOut, status_code=201)
def create_equipment(
    payload: schemas.EquipmentCreate, db: Session = Depends(get_session)
):
    exists = (
        db.query(models.Equipment)
        .filter(models.Equipment.asset_tag == payload.asset_tag)
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="Asset tag ya registrado")

    equipment = models.Equipment(**payload.dict())
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


@app.get("/equipment", response_model=List[schemas.EquipmentOut])
def list_equipment(
    db: Session = Depends(get_session),
    status: str | None = None,
    location: str | None = None,
    limit: int = Query(50, le=200),
):
    query = db.query(models.Equipment)
    if status:
        query = query.filter(models.Equipment.status == status)
    if location:
        query = query.filter(models.Equipment.location == location)
    return query.limit(limit).all()


@app.get("/equipment/{equipment_id}", response_model=schemas.EquipmentOut)
def get_equipment(equipment_id: UUID, db: Session = Depends(get_session)):
    equipment = db.get(models.Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return equipment


@app.put("/equipment/{equipment_id}", response_model=schemas.EquipmentOut)
def update_equipment(
    equipment_id: UUID,
    payload: schemas.EquipmentUpdate,
    db: Session = Depends(get_session),
):
    equipment = db.get(models.Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(equipment, key, value)
    db.commit()
    db.refresh(equipment)
    return equipment


@app.post(
    "/equipment/{equipment_id}/movements",
    response_model=schemas.EquipmentMovementOut,
    status_code=201,
)
def add_movement(
    equipment_id: UUID,
    payload: schemas.EquipmentMovementBase,
    db: Session = Depends(get_session),
):
    equipment = db.get(models.Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    movement = models.EquipmentMovement(**payload.dict())
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


@app.get(
    "/equipment/{equipment_id}/history",
    response_model=List[schemas.EquipmentMovementOut],
)
def get_history(equipment_id: UUID, db: Session = Depends(get_session)):
    equipment = db.get(models.Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return equipment.movements


@app.get("/metrics/inventory")
def inventory_metrics(db: Session = Depends(get_session)):
    total = db.query(models.Equipment).count()
    by_status = (
        db.query(models.Equipment.status, func.count(models.Equipment.id))
        .group_by(models.Equipment.status)
        .all()
    )
    by_location = (
        db.query(models.Equipment.location, func.count(models.Equipment.id))
        .group_by(models.Equipment.location)
        .all()
    )
    return {
        "total": total,
        "by_status": {status or "Sin definir": count for status, count in by_status},
        "by_location": {
            location or "Sin definir": count for location, count in by_location
        },
    }

