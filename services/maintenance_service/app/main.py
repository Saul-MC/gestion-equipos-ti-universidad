import logging
import os
from datetime import date, timedelta
from typing import List
from uuid import UUID

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from common import models, schemas
from common.database import SessionLocal, get_session, session_scope


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("maintenance-service")

REMINDER_DAYS = int(os.getenv("REMINDER_DAYS", "7"))
OBSOLETE_YEARS = int(os.getenv("OBSOLETE_YEARS", "5"))

scheduler = BackgroundScheduler(timezone="UTC")


def remind_maintenance():
    with session_scope() as session:
        upcoming_date = date.today() + timedelta(days=REMINDER_DAYS)
        tasks = (
            session.query(models.MaintenanceTask)
            .filter(
                models.MaintenanceTask.scheduled_for <= upcoming_date,
                models.MaintenanceTask.status == "scheduled",
            )
            .all()
        )
        for task in tasks:
            logger.info(
                "Recordatorio: tarea %s para equipo %s programada el %s",
                task.id,
                task.equipment_id,
                task.scheduled_for,
            )


def mark_obsolete_equipment():
    with session_scope() as session:
        cutoff_year = date.today().year - OBSOLETE_YEARS
        equipment = (
            session.query(models.Equipment)
            .filter(models.Equipment.purchase_date != None)  # noqa: E711
            .all()
        )
        for item in equipment:
            if item.purchase_date.year <= cutoff_year and item.status == "operational":
                item.status = "obsolete"
                session.add(item)
                logger.warning(
                    "Equipo %s marcado como obsoleto (compra %s)",
                    item.asset_tag,
                    item.purchase_date,
                )


def start_scheduler():
    if scheduler.running:
        return
    scheduler.add_job(remind_maintenance, "interval", hours=12, id="reminders")
    scheduler.add_job(mark_obsolete_equipment, "cron", hour=3, id="obsolescence")
    scheduler.start()


app = FastAPI(
    title="Maintenance Service",
    version="1.0.0",
    description="Registra mantenimientos preventivos/correctivos y agentes inteligentes.",
)


@app.on_event("startup")
def on_startup():
    start_scheduler()


@app.post("/tasks", response_model=schemas.MaintenanceTaskOut, status_code=201)
def create_task(
    payload: schemas.MaintenanceTaskCreate, db: Session = Depends(get_session)
):
    equipment = db.get(models.Equipment, payload.equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    task = models.MaintenanceTask(**payload.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks/upcoming", response_model=List[schemas.MaintenanceTaskOut])
def upcoming_tasks(db: Session = Depends(get_session)):
    limit_date = date.today() + timedelta(days=REMINDER_DAYS)
    tasks = (
        db.query(models.MaintenanceTask)
        .filter(models.MaintenanceTask.scheduled_for <= limit_date)
        .order_by(models.MaintenanceTask.scheduled_for)
        .all()
    )
    return tasks


@app.get("/tasks", response_model=List[schemas.MaintenanceTaskOut])
def list_tasks(db: Session = Depends(get_session)):
    return (
        db.query(models.MaintenanceTask)
        .order_by(models.MaintenanceTask.scheduled_for.desc())
        .all()
    )


@app.patch("/tasks/{task_id}", response_model=schemas.MaintenanceTaskOut)
def update_task(
    task_id: UUID, payload: schemas.MaintenanceTaskUpdate, db: Session = Depends(get_session)
):
    task = db.get(models.MaintenanceTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@app.post("/logs", response_model=schemas.MaintenanceLogOut, status_code=201)
def create_log(
    payload: schemas.MaintenanceLogBase, db: Session = Depends(get_session)
):
    task = db.get(models.MaintenanceTask, payload.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    task.status = "completed"
    log = models.MaintenanceLog(**payload.dict())
    db.add(log)
    db.add(task)
    db.commit()
    db.refresh(log)
    return log


@app.get("/logs", response_model=List[schemas.MaintenanceLogOut])
def list_logs(db: Session = Depends(get_session)):
    return db.query(models.MaintenanceLog).order_by(models.MaintenanceLog.created_at.desc()).all()

