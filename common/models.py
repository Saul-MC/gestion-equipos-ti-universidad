import uuid
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    contact_email = Column(String(150))
    phone = Column(String(40))
    category = Column(String(80))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contracts = relationship("SupplierContract", back_populates="supplier")
    equipment = relationship("Equipment", back_populates="supplier")


class SupplierContract(Base):
    __tablename__ = "supplier_contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    contract_number = Column(String(80), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    amount = Column(Numeric(14, 2))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="contracts")


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_tag = Column(String(80), unique=True, nullable=False)
    name = Column(String(150))
    type = Column(String(80))
    model = Column(String(120))
    serial_number = Column(String(120))
    purchase_date = Column(Date)
    cost = Column(Numeric(14, 2))
    location = Column(String(120))
    status = Column(String(40), default="operational")
    useful_life_years = Column(Integer, default=5)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="equipment")
    movements = relationship("EquipmentMovement", back_populates="equipment")
    maintenance_tasks = relationship("MaintenanceTask", back_populates="equipment")


class EquipmentMovement(Base):
    __tablename__ = "equipment_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"))
    from_location = Column(String(120))
    to_location = Column(String(120))
    assigned_to = Column(String(120))
    notes = Column(Text)
    moved_at = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="movements")


class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"))
    scheduled_for = Column(Date, nullable=False)
    type = Column(String(40))
    priority = Column(String(20))
    status = Column(String(30), default="scheduled")
    assigned_team = Column(String(120))
    reminder_token = Column(String(120))
    created_at = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="maintenance_tasks")
    logs = relationship("MaintenanceLog", back_populates="task")


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("maintenance_tasks.id"))
    completed_on = Column(Date)
    action_taken = Column(Text)
    cost = Column(Numeric(14, 2))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("MaintenanceTask", back_populates="logs")

