from typing import List
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from common import models, schemas
from common.database import get_session


app = FastAPI(
    title="Provider Service",
    version="1.0.0",
    description="Gestión de proveedores y contratos.",
)


@app.post("/suppliers", response_model=schemas.SupplierOut, status_code=201)
def create_supplier(payload: schemas.SupplierCreate, db: Session = Depends(get_session)):
    supplier = models.Supplier(**payload.dict())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@app.get("/suppliers", response_model=List[schemas.SupplierOut])
def list_suppliers(db: Session = Depends(get_session)):
    return db.query(models.Supplier).order_by(models.Supplier.created_at.desc()).all()


@app.put("/suppliers/{supplier_id}", response_model=schemas.SupplierOut)
def update_supplier(
    supplier_id: UUID,
    payload: schemas.SupplierUpdate,
    db: Session = Depends(get_session),
):
    supplier = db.get(models.Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(supplier, key, value)
    db.commit()
    db.refresh(supplier)
    return supplier


@app.post(
    "/suppliers/{supplier_id}/contracts",
    response_model=schemas.SupplierContractOut,
    status_code=201,
)
def add_contract(
    supplier_id: UUID,
    payload: schemas.SupplierContractBase,
    db: Session = Depends(get_session),
):
    supplier = db.get(models.Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    contract = models.SupplierContract(**payload.dict(), supplier_id=supplier_id)
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@app.get(
    "/suppliers/{supplier_id}/contracts",
    response_model=List[schemas.SupplierContractOut],
)
def list_contracts(supplier_id: UUID, db: Session = Depends(get_session)):
    supplier = db.get(models.Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return supplier.contracts






