import os
from datetime import date, datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api_gateway:8000")

st.set_page_config(
    page_title="Gestión de Equipos TI",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="💻"
)

# ==================== AUTENTICACIÓN ====================
def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None

def login_page():
    st.title("🔐 Inicio de Sesión")
    st.markdown("### Sistema de Gestión de Equipos de TI - Universidad Pública")
    
    # Verificar si ya está autenticado (evitar rerun innecesario)
    if st.session_state.get("authenticated", False):
        return
    
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario", key="login_username")
        password = st.text_input("🔑 Contraseña", type="password", placeholder="Ingresa tu contraseña", key="login_password")
        submitted = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
        
        if submitted:
            if username and password:
                try:
                    response = api_json("POST", "/auth/login", json={"username": username, "password": password})
                    if response.get("success"):
                        user_data = response.get("user", {})
                        st.session_state.authenticated = True
                        st.session_state.username = user_data.get("username", username)
                        st.session_state.user_role = user_data.get("role", "user")
                        st.session_state.user_full_name = user_data.get("full_name", username)
                        # Usar st.success y luego rerun fuera del form
                        st.success("✅ Inicio de sesión exitoso!")
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                except requests.HTTPError as exc:
                    if exc.response.status_code == 401:
                        st.error("❌ Usuario o contraseña incorrectos")
                    else:
                        st.error(f"❌ Error de conexión: {exc.response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Por favor completa todos los campos")
    
    # Rerun solo si se autenticó exitosamente (manejado fuera del form)
    if st.session_state.get("authenticated", False):
        # Usar st.rerun() de manera segura fuera del contexto del form
        try:
            st.rerun()
        except Exception:
            # Si falla, el siguiente refresh de página cargará la sesión autenticada
            pass
    
    st.markdown("---")
    st.info("""
    **Usuarios de prueba:**
    - 👨‍💼 Admin: `admin` / `admin123`
    - 🔧 Técnico: `tecnico` / `tecnico123`
    - 👤 Usuario: `usuario` / `usuario123`
    """)

def logout():
    # Limpiar variables de sesión relacionadas con autenticación
    st.session_state.authenticated = False
    st.session_state.username = None
    if "user_role" in st.session_state:
        del st.session_state.user_role
    if "user_full_name" in st.session_state:
        del st.session_state.user_full_name
    # Invalidar todos los cachés
    invalidate_caches(fetch_dashboard, fetch_suppliers, fetch_equipment, fetch_tasks, fetch_logs, fetch_upcoming_tasks)
    # Rerun seguro
    try:
        st.rerun()
    except Exception:
        # Si falla, el siguiente refresh mostrará la página de login
        pass

# ==================== FUNCIONES API ====================
def api_request(method: str, path: str, **kwargs):
    url = f"{API_GATEWAY_URL}{path}"
    if "json" in kwargs:
        kwargs["json"] = _serialize_payload(kwargs["json"])
    response = requests.request(method, url, timeout=30, **kwargs)
    response.raise_for_status()
    return response

def api_json(method: str, path: str, **kwargs):
    return api_request(method, path, **kwargs).json()

@st.cache_data(ttl=60)
def fetch_dashboard():
    return api_json("GET", "/dashboard")

@st.cache_data(ttl=60)
def fetch_suppliers():
    return api_json("GET", "/suppliers")

@st.cache_data(ttl=60)
def fetch_equipment(status: str | None = None, location: str | None = None):
    params = {}
    if status:
        params["status"] = status
    if location:
        params["location"] = location
    return api_json("GET", "/equipment", params=params or None)

@st.cache_data(ttl=60)
def fetch_upcoming_tasks():
    return api_json("GET", "/maintenance/upcoming")

@st.cache_data(ttl=60)
def fetch_tasks():
    return api_json("GET", "/maintenance/tasks")

@st.cache_data(ttl=60)
def fetch_logs():
    return api_json("GET", "/maintenance/logs")

@st.cache_data(ttl=60)
def fetch_report_file(fmt: str):
    resp = api_request("GET", "/reports/export", params={"format": fmt})
    disposition = resp.headers.get("Content-Disposition", f"attachment; filename=reporte.{fmt}")
    filename = disposition.split("filename=")[-1].strip("\"'")
    return resp.content, filename

def _serialize_payload(payload):
    if isinstance(payload, dict):
        return {key: _serialize_payload(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_serialize_payload(item) for item in payload]
    if isinstance(payload, (date, datetime)):
        return payload.isoformat()
    return payload

def invalidate_caches(*functions):
    for func in functions:
        func.clear()

def refresh_view(*cache_functions):
    """Invalida cachés y programa un rerun seguro."""
    invalidate_caches(*cache_functions)
    # Usar st.rerun() con manejo de errores
    try:
        st.rerun()
    except Exception as e:
        # Si hay error de rerun, al menos los cachés están invalidados
        # El usuario puede refrescar manualmente si es necesario
        st.warning("⚠️ Por favor refresca la página para ver los cambios")

# ==================== RENDERIZADO ====================
def render_metric_charts(metrics: dict):
    status_df = pd.DataFrame({
        "estado": list(metrics["equipment_by_status"].keys()),
        "valor": list(metrics["equipment_by_status"].values()),
    })
    location_df = pd.DataFrame({
        "ubicacion": list(metrics["equipment_by_location"].keys()),
        "total": list(metrics["equipment_by_location"].values()),
    })
    costs_df = pd.DataFrame({
        "periodo": list(metrics["maintenance_costs"].keys()),
        "costo": list(metrics["maintenance_costs"].values()),
    })
    aging_df = pd.DataFrame({
        "segmento": list(metrics["aging_profile"].keys()),
        "cantidad": list(metrics["aging_profile"].values()),
    })

    charts = st.tabs(["📊 Estados", "📍 Ubicaciones", "💰 Costos", "⏳ Antigüedad"])
    with charts[0]:
        if not status_df.empty:
            st.plotly_chart(
                px.pie(status_df, names="estado", values="valor", title="📊 Equipos por estado"),
                use_container_width=True,
            )
        else:
            st.info("📭 Sin datos de estado aún.")
    with charts[1]:
        if not location_df.empty:
            st.plotly_chart(
                px.bar(location_df, x="ubicacion", y="total", title="📍 Equipos por ubicación"),
                use_container_width=True,
            )
        else:
            st.info("📭 Sin ubicaciones registradas.")
    with charts[2]:
        if not costs_df.empty:
            st.plotly_chart(
                px.line(costs_df, x="periodo", y="costo", title="💰 Costos de mantenimiento", markers=True),
                use_container_width=True,
            )
        else:
            st.info("📭 Aún no hay costos de mantenimiento acumulados.")
    with charts[3]:
        if not aging_df.empty:
            st.plotly_chart(
                px.bar(aging_df, x="segmento", y="cantidad", title="⏳ Perfil de antigüedad"),
                use_container_width=True,
            )
        else:
            st.info("📭 Sin datos de antigüedad.")

def render_dashboard():
    st.header("📊 Dashboard Principal")
    data = fetch_dashboard()
    metrics = data["metrics"]
    total_equipment = sum(metrics["equipment_by_status"].values())
    equipment = fetch_equipment()
    equipment_map = {str(item["id"]): (item.get("name") or item.get("asset_tag") or str(item["id"])) for item in (equipment or [])}
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💻 Equipos totales", total_equipment)
    col2.metric("📍 Ubicaciones", len(metrics["equipment_by_location"]))
    col3.metric("📈 Series de costos", len(metrics["maintenance_costs"]))
    col4.metric("⏳ Segmentos antigüedad", len(metrics["aging_profile"]))

    render_metric_charts(metrics)

    st.subheader("📅 Calendario de mantenimientos próximos")
    upcoming = pd.DataFrame(fetch_upcoming_tasks())
    if upcoming.empty:
        st.info("📭 No hay tareas programadas en la ventana de recordatorio.")
    else:
        upcoming["status_norm"] = upcoming["status"].str.lower().fillna("")
        upcoming = upcoming[~upcoming["status_norm"].isin(["completed", "completado", "done"])]
        if upcoming.empty:
            st.info("📭 No hay tareas pendientes en la ventana de recordatorio.")
            return
        upcoming["scheduled_for"] = pd.to_datetime(upcoming["scheduled_for"])
        upcoming["equipo"] = (
            upcoming["equipment_id"].astype(str).map(equipment_map).fillna(upcoming["equipment_id"])
        )
        # Normalizamos a fecha para calcular los días restantes de forma segura
        upcoming["días_restantes"] = (
            upcoming["scheduled_for"].dt.normalize() - pd.Timestamp(date.today())
        ).dt.days
        upcoming = upcoming.sort_values("scheduled_for")
        st.dataframe(upcoming[["scheduled_for", "días_restantes", "equipo", "type", "priority", "status", "assigned_team"]])

        st.subheader("🔔 Alertas de mantenimiento")
        alert_rows = upcoming[["scheduled_for", "días_restantes", "equipo", "type", "priority"]].head(5)
        for _, row in alert_rows.iterrows():
            st.info(
                f"{row['equipo']} • {row['type']} ({row['priority']}) • {row['scheduled_for'].date()} • en {row['días_restantes']} días"
            )

def render_suppliers():
    st.header("🏢 Gestión de Proveedores")
    suppliers = fetch_suppliers()
    
    if suppliers:
        df = pd.DataFrame(suppliers)
        df["created_at"] = pd.to_datetime(df["created_at"])
        st.subheader("📋 Proveedores registrados")
        st.dataframe(df[["name", "category", "contact_email", "phone", "created_at"]])
    else:
        st.info("📭 Aún no existen proveedores registrados.")

    register, update = st.tabs(["➕ Registrar proveedor", "✏️ Actualizar / Contratos"])
    
    with register:
        with st.form("create_supplier"):
            st.subheader("➕ Nuevo proveedor")
            payload = {
                "name": st.text_input("🏷️ Nombre comercial"),
                "contact_email": st.text_input("📧 Correo de contacto"),
                "phone": st.text_input("📞 Teléfono"),
                "category": st.text_input("📂 Categoría (hardware, software, etc.)"),
                "address": st.text_area("📍 Dirección"),
            }
            if st.form_submit_button("💾 Guardar proveedor", use_container_width=True):
                try:
                    api_json("POST", "/suppliers", json=payload)
                    st.success("✅ Proveedor registrado exitosamente!")
                    refresh_view(fetch_suppliers)
                except requests.HTTPError as exc:
                    st.error(f"❌ Error: {exc.response.text}")

    with update:
        if not suppliers:
            st.warning("⚠️ Registra un proveedor antes de continuar.")
            return
        supplier_map = {f"{s['name']} ({s['category'] or 'Sin categoría'})": s for s in suppliers}
        choice = st.selectbox("🔍 Selecciona proveedor", list(supplier_map.keys()))
        selected = supplier_map[choice]

        col1, col2 = st.columns(2)
        with col1:
            with st.form("update_supplier"):
                st.subheader("✏️ Actualizar información")
                updated_payload = {
                    "name": st.text_input("🏷️ Nombre", value=selected["name"]),
                    "contact_email": st.text_input("📧 Email", value=selected.get("contact_email") or ""),
                    "phone": st.text_input("📞 Teléfono", value=selected.get("phone") or ""),
                    "category": st.text_input("📂 Categoría", value=selected.get("category") or ""),
                    "address": st.text_area("📍 Dirección", value=selected.get("address") or ""),
                }
                if st.form_submit_button("💾 Actualizar", use_container_width=True):
                    try:
                        api_json("PUT", f"/suppliers/{selected['id']}", json=updated_payload)
                        st.success("✅ Proveedor actualizado!")
                        refresh_view(fetch_suppliers)
                    except requests.HTTPError as exc:
                        st.error(f"❌ Error: {exc.response.text}")

        with col2:
            st.subheader("📄 Contratos e historial de compras")
            contracts = api_json("GET", f"/suppliers/{selected['id']}/contracts")
            if contracts:
                cdf = pd.DataFrame(contracts)
                st.dataframe(cdf[["contract_number", "start_date", "end_date", "amount"]])
            else:
                st.info("📭 No hay contratos vinculados.")

            with st.form("add_contract"):
                st.write("➕ Registrar nuevo contrato")
                contract_payload = {
                    "contract_number": st.text_input("🔢 Número de contrato"),
                    "start_date": st.date_input("📅 Inicio", value=date.today()),
                    "end_date": st.date_input("📅 Fin", value=date.today()),
                    "amount": st.number_input("💰 Monto (USD)", min_value=0.0, step=100.0),
                    "description": st.text_area("📝 Descripción"),
                }
                if st.form_submit_button("💾 Guardar contrato", use_container_width=True):
                    try:
                        api_json("POST", f"/suppliers/{selected['id']}/contracts", json=contract_payload)
                        st.success("✅ Contrato registrado!")
                        refresh_view(fetch_suppliers)
                    except requests.HTTPError as exc:
                        st.error(f"❌ Error: {exc.response.text}")

def render_equipment():
    st.header("💻 Gestión de Equipos")
    filters = st.columns(2)
    status_filter = filters[0].selectbox(
        "🔍 Filtrar por estado",
        ["Todos", "operational", "maintenance", "retired", "obsolete"],
    )
    location_filter = filters[1].text_input("🔍 Filtrar por ubicación")

    status_param = None if status_filter == "Todos" else status_filter
    equipment = fetch_equipment(status_param, location_filter or None)

    if equipment:
        df = pd.DataFrame(equipment)
        st.subheader("📦 Inventario de TI")
        st.dataframe(df[["asset_tag", "name", "type", "location", "status", "purchase_date", "supplier_id"]])
    else:
        st.info("📭 No hay equipos registrados para los filtros seleccionados.")

    tabs = st.tabs(["➕ Registrar equipo", "✏️ Actualizar equipo", "📋 Movimientos / Historial"])

    with tabs[0]:
        suppliers = fetch_suppliers()
        supplier_options = ["Ninguno (opcional)"] + [f"{s['name']} ({s.get('category', 'Sin categoría')})" for s in suppliers] if suppliers else ["Ninguno (opcional)"]
        supplier_map = {f"{s['name']} ({s.get('category', 'Sin categoría')})": s['id'] for s in suppliers} if suppliers else {}
        
        with st.form("create_equipment"):
            payload = {
                "asset_tag": st.text_input("🏷️ Asset Tag"),
                "name": st.text_input("📝 Nombre del activo"),
                "type": st.text_input("🔧 Tipo"),
                "model": st.text_input("📦 Modelo"),
                "serial_number": st.text_input("🔢 Número de serie"),
                "purchase_date": st.date_input("📅 Fecha de compra"),
                "cost": st.number_input("💰 Costo (USD)", min_value=0.0, step=100.0),
                "location": st.text_input("📍 Ubicación actual"),
                "status": st.selectbox("⚙️ Estado operativo", ["operational", "maintenance", "retired", "obsolete"]),
                "useful_life_years": st.number_input("⏳ Vida útil (años)", min_value=1, max_value=10, value=5),
            }
            selected_supplier = st.selectbox("🏢 Proveedor", supplier_options)
            if selected_supplier and selected_supplier != "Ninguno (opcional)":
                payload["supplier_id"] = supplier_map[selected_supplier]
            
            if st.form_submit_button("💾 Registrar equipo", use_container_width=True):
                try:
                    api_json("POST", "/equipment", json=payload)
                    st.success("✅ Equipo registrado correctamente!")
                    refresh_view(fetch_equipment, fetch_dashboard)
                except requests.HTTPError as exc:
                    st.error(f"❌ Error: {exc.response.text}")

    with tabs[1]:
        if not equipment:
            st.warning("⚠️ Registra equipos para poder actualizarlos.")
        else:
            equipment_map = {f"{item['asset_tag']} - {item.get('name','')}": item for item in equipment}
            selected_label = st.selectbox("🔍 Selecciona equipo", list(equipment_map.keys()))
            selected = equipment_map[selected_label]
            with st.form("update_equipment"):
                st.write("✏️ Actualizar atributos principales")
                payload = {
                    "name": st.text_input("📝 Nombre", value=selected.get("name") or ""),
                    "type": st.text_input("🔧 Tipo", value=selected.get("type") or ""),
                    "model": st.text_input("📦 Modelo", value=selected.get("model") or ""),
                    "serial_number": st.text_input("🔢 Serie", value=selected.get("serial_number") or ""),
                    "location": st.text_input("📍 Ubicación", value=selected.get("location") or ""),
                    "status": st.selectbox(
                        "⚙️ Estado",
                        ["operational", "maintenance", "retired", "obsolete"],
                        index=["operational", "maintenance", "retired", "obsolete"].index(selected.get("status", "operational")),
                    ),
                    "useful_life_years": st.number_input(
                        "⏳ Vida útil (años)", min_value=1, max_value=15, value=selected.get("useful_life_years") or 5
                    ),
                }
                if st.form_submit_button("💾 Guardar cambios", use_container_width=True):
                    try:
                        api_json("PUT", f"/equipment/{selected['id']}", json=payload)
                        st.success("✅ Equipo actualizado!")
                        refresh_view(fetch_equipment, fetch_dashboard)
                    except requests.HTTPError as exc:
                        st.error(f"❌ Error: {exc.response.text}")

    with tabs[2]:
        if not equipment:
            st.warning("⚠️ Necesitas al menos un equipo para registrar movimientos.")
            return
        equipment_options = {f"{item['asset_tag']}": item for item in equipment}
        selected_label = st.selectbox("🔍 Equipo para revisar historial", list(equipment_options.keys()), key="history_selector")
        selected = equipment_options[selected_label]
        history = api_json("GET", f"/equipment/{selected['id']}/history")
        st.subheader("📋 Historial de movimientos")
        if history:
            hist_df = pd.DataFrame(history)
            st.dataframe(hist_df[["from_location", "to_location", "assigned_to", "notes", "moved_at"]])
        else:
            st.info("📭 Aún no hay movimientos registrados.")

        with st.form("add_movement"):
            st.write("➕ Registrar nuevo movimiento / asignación")
            payload = {
                "equipment_id": selected["id"],
                "from_location": st.text_input("📍 Desde"),
                "to_location": st.text_input("📍 Hacia"),
                "assigned_to": st.text_input("👤 Asignado a"),
                "notes": st.text_area("📝 Notas"),
            }
            if st.form_submit_button("💾 Registrar movimiento", use_container_width=True):
                try:
                    api_json("POST", f"/equipment/{selected['id']}/movements", json=payload)
                    st.success("✅ Movimiento registrado!")
                    refresh_view(fetch_equipment)
                except requests.HTTPError as exc:
                    st.error(f"❌ Error: {exc.response.text}")

def render_maintenance():
    st.header("🔧 Gestión de Mantenimiento")
    tasks = fetch_tasks()
    logs = fetch_logs()

    equipment = fetch_equipment()
    equipment_map = {str(item["id"]): (item.get("name") or item.get("asset_tag") or str(item["id"])) for item in (equipment or [])}

    tabs = st.tabs([
        "📅 Calendario / Programar",
        "📝 Bitácoras / Registrar",
    ])

    with tabs[0]:
        st.subheader("📅 Calendario programado")
        scheduled = pd.DataFrame(tasks)
        if scheduled.empty:
            st.info("📭 Sin tareas registradas.")
        else:
            scheduled["scheduled_for"] = pd.to_datetime(scheduled["scheduled_for"])
            scheduled["equipo"] = (
                scheduled["equipment_id"].astype(str).map(equipment_map).fillna(scheduled["equipment_id"])
            )
            st.dataframe(scheduled[["scheduled_for", "equipo", "type", "priority", "status", "assigned_team"]])

        st.markdown("---")
        st.subheader("🗓️ Programar mantenimiento")
        equipment = fetch_equipment()
        if not equipment:
            st.warning("⚠️ Registra equipos antes de programar mantenimiento.")
        else:
            options = {f"{item['asset_tag']}": item for item in equipment}
            with st.form("schedule_task"):
                selected = st.selectbox("💻 Equipo", list(options.keys()))
                payload = {
                    "equipment_id": options[selected]["id"],
                    "scheduled_for": st.date_input("📅 Fecha programada", value=date.today()),
                    "type": st.selectbox("🔧 Tipo", ["preventive", "corrective"]),
                    "priority": st.selectbox("⚡ Prioridad", ["low", "medium", "high"]),
                    "assigned_team": st.text_input("👥 Equipo responsable"),
                }
                if st.form_submit_button("💾 Programar", use_container_width=True):
                    try:
                        api_json("POST", "/maintenance/tasks", json=payload)
                        st.success("✅ Tarea programada!")
                        refresh_view(fetch_tasks, fetch_upcoming_tasks, fetch_dashboard)
                    except requests.HTTPError as exc:
                        st.error(f"❌ Error: {exc.response.text}")

    with tabs[1]:
        st.subheader("📋 Bitácoras de reparaciones / costos")
        log_df = pd.DataFrame(logs)
        if log_df.empty:
            st.info("📭 Aún no hay bitácoras de mantenimiento.")
        else:
            st.dataframe(log_df[["completed_on", "action_taken", "cost", "notes"]])

        st.markdown("---")
        st.subheader("📝 Registrar reparación")
        if not tasks:
            st.warning("⚠️ No hay tareas para registrar reparaciones.")
            return
        pending_tasks = [
            t for t in tasks if str(t.get("status", "")).lower() not in ("completed", "completado", "done")
        ]
        if not pending_tasks:
            st.info("📭 No hay tareas pendientes para registrar reparaciones.")
            return
        pending_map = {
            f"{t['scheduled_for']} - {equipment_map.get(str(t['equipment_id']), t['equipment_id'])} ({t['type']})": t
            for t in pending_tasks
        }
        with st.form("register_log"):
            selected_task_label = st.selectbox("🔍 Tarea completada", list(pending_map.keys()))
            selected_task = pending_map[selected_task_label]
            payload = {
                "task_id": selected_task["id"],
                "completed_on": st.date_input("📅 Fecha de ejecución", value=date.today()),
                "action_taken": st.text_area("🔧 Acciones realizadas"),
                "cost": st.number_input("💰 Costo (USD)", min_value=0.0, step=50.0),
                "notes": st.text_input("📝 Notas adicionales"),
            }
            if st.form_submit_button("💾 Guardar bitácora", use_container_width=True):
                try:
                    api_json("POST", "/maintenance/logs", json=payload)
                    st.success("✅ Bitácora registrada y tarea marcada como completada!")
                    refresh_view(fetch_tasks, fetch_logs, fetch_dashboard)
                except requests.HTTPError as exc:
                    st.error(f"❌ Error: {exc.response.text}")

def render_reports():
    st.header("📊 Análisis y Reportes")
    metrics = fetch_dashboard()["metrics"]
    st.subheader("📈 Métricas clave")
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Equipos operativos", metrics["equipment_by_status"].get("operational", 0))
    col2.metric("🔧 Equipos en mantenimiento", metrics["equipment_by_status"].get("maintenance", 0))
    col3.metric("💰 Costo acumulado", f"${sum(metrics['maintenance_costs'].values()):,.2f}")

    st.subheader("📊 Visualizaciones")
    render_metric_charts(metrics)

    st.subheader("📥 Exportación de reportes")
    try:
        excel_bytes, excel_name = fetch_report_file("excel")
        pdf_bytes, pdf_name = fetch_report_file("pdf")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📊 Descargar Excel",
                data=excel_bytes,
                file_name=excel_name or "reporte.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                "📄 Descargar PDF",
                data=pdf_bytes,
                file_name=pdf_name or "reporte.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    except requests.HTTPError as exc:
        st.error(f"❌ No se pudo generar el reporte: {exc.response.text}")

# ==================== MAIN ====================
# Limpiar flag de rerun pendiente
if "pending_rerun" in st.session_state:
    del st.session_state.pending_rerun

check_auth()

if not st.session_state.authenticated:
    login_page()
else:
    # Sidebar con navegación y logout
    with st.sidebar:
        st.title("💻 Gestión de Equipos TI")
        st.markdown(f"👤 **Usuario:** {st.session_state.username}")
        st.markdown("---")
        
        section = st.radio(
            "🧭 Navegación",
            ["📊 Dashboard", "🏢 Proveedores", "💻 Equipos", "🔧 Mantenimiento", "📊 Reportes"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
    
    # Contenido principal
    if section == "📊 Dashboard":
        render_dashboard()
    elif section == "🏢 Proveedores":
        render_suppliers()
    elif section == "💻 Equipos":
        render_equipment()
    elif section == "🔧 Mantenimiento":
        render_maintenance()
    else:
        render_reports()
