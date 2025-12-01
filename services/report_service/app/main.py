import io
from datetime import datetime
from typing import Dict

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from common import models
from common.database import get_session


app = FastAPI(
    title="Report Service",
    version="1.0.0",
    description="Análisis descriptivo, métricas y exportación en PDF/Excel.",
)


def _aggregate_metrics(db: Session) -> Dict:
    equipment = db.query(models.Equipment).all()
    maintenance_costs = (
        db.query(models.MaintenanceLog)
        .with_entities(models.MaintenanceLog.completed_on, models.MaintenanceLog.cost)
        .all()
    )

    by_status: Dict[str, int] = {}
    by_location: Dict[str, int] = {}
    aging: Dict[str, int] = {"0-2": 0, "3-5": 0, "6+": 0}

    for eq in equipment:
        by_status[eq.status or "Sin estado"] = by_status.get(eq.status or "Sin estado", 0) + 1
        by_location[eq.location or "Sin ubicación"] = by_location.get(eq.location or "Sin ubicación", 0) + 1

        if not eq.purchase_date:
            continue
        age = datetime.now().year - eq.purchase_date.year
        if age <= 2:
            aging["0-2"] += 1
        elif age <= 5:
            aging["3-5"] += 1
        else:
            aging["6+"] += 1

    cost_series: Dict[str, float] = {}
    for log in maintenance_costs:
        if not log.completed_on or not log.cost:
            continue
        key = f"{log.completed_on.year}-{log.completed_on.month:02d}"
        cost_series[key] = cost_series.get(key, 0) + float(log.cost)

    return {
        "equipment_by_status": by_status,
        "equipment_by_location": by_location,
        "maintenance_costs": cost_series,
        "aging_profile": aging,
    }


@app.get("/reports/dashboard")
def dashboard(db: Session = Depends(get_session)):
    return _aggregate_metrics(db)


@app.get("/reports/export")
def export_report(
    format: str = Query("excel", pattern="^(excel|pdf)$"),
    db: Session = Depends(get_session),
):
    metrics = _aggregate_metrics(db)
    if format == "excel":
        return _export_excel(metrics)
    if format == "pdf":
        return _export_pdf(metrics)
    raise HTTPException(status_code=400, detail="Formato no soportado")


def _export_excel(metrics: Dict):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for key, data in metrics.items():
            df = pd.DataFrame(list(data.items()), columns=["category", "value"])
            df.to_excel(writer, sheet_name=key[:31], index=False)
    buffer.seek(0)
    filename = f"report_{datetime.utcnow().isoformat()}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _export_pdf(metrics: Dict):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 45
    primary = (0.12, 0.36, 0.6)
    accent = (0.0, 0.62, 0.53)
    text_color = (0.12, 0.12, 0.16)

    status_labels = {
        "operational": "Operacional",
        "maintenance": "En mantenimiento",
        "obsolete": "Obsoleto",
        "Sin estado": "Sin estado",
    }

    def as_status_label(value: str) -> str:
        if not value:
            return "Sin estado"
        return status_labels.get(value.lower(), value.title())

    def as_currency(amount: float) -> str:
        return f"$ {amount:,.2f}"

    def format_period(period: str) -> str:
        try:
            dt = datetime.strptime(f"{period}-01", "%Y-%m-%d")
            return dt.strftime("%b %Y")
        except ValueError:
            return period

    def draw_header():
        pdf.setFillColorRGB(*primary)
        pdf.rect(0, height - 90, width, 90, stroke=0, fill=1)
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(margin, height - 50, "Reporte de Activos y Mantenimiento")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(margin, height - 68, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        pdf.drawRightString(width - margin, height - 68, "Vista general")

    def ensure_space(needed_rows: int = 3) -> None:
        nonlocal current_height
        if current_height - needed_rows * 16 < margin + 20:
            pdf.showPage()
            draw_header()
            current_height = height - 120

    def draw_section(title: str, rows) -> None:
        nonlocal current_height
        ensure_space(len(rows) + 2)
        pdf.setFillColorRGB(*primary)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(margin, current_height, title)
        current_height -= 18
        pdf.setFillColorRGB(*text_color)
        pdf.setFont("Helvetica", 10)
        if not rows:
            pdf.drawString(margin, current_height, "Sin datos disponibles")
            current_height -= 16
            return
        for left, right in rows:
            ensure_space(1)
            pdf.drawString(margin, current_height, f"• {left}")
            pdf.drawRightString(width - margin, current_height, right)
            current_height -= 14
        current_height -= 8

    def draw_cards(cards):
        nonlocal current_height
        card_width = (width - 2 * margin - 12) / 2
        card_height = 50
        x_positions = [margin, margin + card_width + 12]
        y_pos = current_height
        for idx, (label, value) in enumerate(cards):
            if idx % 2 == 0 and idx > 0:
                y_pos -= card_height + 12
            ensure_space(4)
            x = x_positions[idx % 2]
            pdf.setFillColor(colors.whitesmoke)
            pdf.roundRect(x, y_pos - card_height, card_width, card_height, 8, stroke=0, fill=1)
            pdf.setFillColorRGB(*accent)
            pdf.setFont("Helvetica", 9)
            pdf.drawString(x + 12, y_pos - 16, label)
            pdf.setFillColorRGB(*text_color)
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(x + 12, y_pos - 34, value)
        current_height = y_pos - card_height - 12

    equipment_by_status = metrics.get("equipment_by_status", {})
    equipment_by_location = metrics.get("equipment_by_location", {})
    maintenance_costs = metrics.get("maintenance_costs", {})
    aging_profile = metrics.get("aging_profile", {})

    total_equipos = sum(equipment_by_status.values())
    obsoletos = equipment_by_status.get("obsolete", 0)
    operativos = equipment_by_status.get("operational", 0)
    ubicaciones = len(equipment_by_location)
    meses_costos = len(maintenance_costs)
    costo_promedio = (
        sum(maintenance_costs.values()) / meses_costos if meses_costos else 0
    )

    draw_header()
    current_height = height - 120

    draw_cards(
        [
            ("Equipos totales", str(total_equipos)),
            ("Operacionales", str(operativos)),
            ("Obsoletos", str(obsoletos)),
            ("Ubicaciones activas", str(ubicaciones)),
        ]
    )

    draw_section(
        "Equipos por estado",
        [
            (as_status_label(name or "Sin estado"), str(value))
            for name, value in sorted(
                equipment_by_status.items(), key=lambda item: item[1], reverse=True
            )
        ],
    )

    draw_section(
        "Equipos por ubicación",
        [
            ((location or "Sin ubicación"), str(value))
            for location, value in sorted(
                equipment_by_location.items(), key=lambda item: item[1], reverse=True
            )
        ],
    )

    draw_section(
        "Costos de mantenimiento por mes",
        [
            (format_period(period), as_currency(amount))
            for period, amount in sorted(
                maintenance_costs.items(), key=lambda item: item[0], reverse=True
            )
        ],
    )

    draw_section(
        "Perfil de antigüedad (años)",
        [
            (f"{label} años", str(value))
            for label, value in sorted(aging_profile.items())
        ],
    )

    if meses_costos:
        draw_section(
            "Resumen financiero",
            [
                ("Meses con registro", str(meses_costos)),
                ("Costo promedio mensual", as_currency(costo_promedio)),
                ("Costo total registrado", as_currency(sum(maintenance_costs.values()))),
            ],
        )

    pdf.save()
    buffer.seek(0)
    filename = f"report_{datetime.utcnow().isoformat()}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )






