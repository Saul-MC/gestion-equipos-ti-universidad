from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SupplierBase(BaseModel):
    name: str
    contact_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(SupplierBase):
    pass


class SupplierOut(SupplierBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class SupplierContractBase(BaseModel):
    contract_number: str
    start_date: date
    end_date: Optional[date] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None


class SupplierContractCreate(SupplierContractBase):
    supplier_id: UUID


class SupplierContractOut(SupplierContractBase):
    id: UUID

    class Config:
        orm_mode = True


class EquipmentBase(BaseModel):
    asset_tag: str = Field(..., max_length=80)
    name: Optional[str] = None
    type: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    cost: Optional[Decimal] = None
    location: Optional[str] = None
    status: Optional[str] = "operational"
    useful_life_years: Optional[int] = 5
    supplier_id: Optional[UUID] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    useful_life_years: Optional[int] = None


class EquipmentOut(EquipmentBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class EquipmentMovementBase(BaseModel):
    equipment_id: UUID
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class EquipmentMovementOut(EquipmentMovementBase):
    id: UUID
    moved_at: datetime

    class Config:
        orm_mode = True


class MaintenanceTaskBase(BaseModel):
    equipment_id: UUID
    scheduled_for: date
    type: str = Field(..., regex="^(preventive|corrective)$")
    priority: str = Field(..., regex="^(low|medium|high)$")
    assigned_team: Optional[str] = None


class MaintenanceTaskCreate(MaintenanceTaskBase):
    pass


class MaintenanceTaskUpdate(BaseModel):
    scheduled_for: Optional[date] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class MaintenanceTaskOut(MaintenanceTaskBase):
    id: UUID
    status: str

    class Config:
        orm_mode = True


class MaintenanceLogBase(BaseModel):
    task_id: UUID
    completed_on: date
    action_taken: str
    cost: Optional[Decimal] = None
    notes: Optional[str] = None


class MaintenanceLogOut(MaintenanceLogBase):
    id: UUID

    class Config:
        orm_mode = True


class DashboardMetric(BaseModel):
    equipment_by_status: dict
    equipment_by_location: dict
    maintenance_costs: dict
    aging_profile: dict


class ReportExportResponse(BaseModel):
    filename: str
    generated_at: datetime
    format: str


class PaginatedResponse(BaseModel):
    items: List
    total: int






