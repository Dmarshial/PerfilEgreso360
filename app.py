import io
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="PerfilEgreso 360", page_icon="🎓", layout="wide")

st.markdown('''
<style>
.block-container {padding-top: 1.3rem; max-width: 1400px;}
.metric-card {border:1px solid #e5e7eb;border-radius:16px;padding:18px;background:#ffffff;}
.small-muted {font-size:0.88rem;color:#64748b;}
.hero {padding:22px 26px;border-radius:18px;background:linear-gradient(90deg,#eef2ff,#f8fafc);border:1px solid #e5e7eb;}
</style>
''', unsafe_allow_html=True)

REQUIRED_SHEETS = ["Estudiantes", "Evaluaciones", "Config_Lineas", "Config_RA", "Ponderaciones", "Recomendaciones"]


def sample_data():
    students = pd.DataFrame({
        "student_id": [1,2,3,4,5,6,7,8],
        "rut": ["11111111-1","22222222-2","33333333-3","44444444-4","55555555-5","66666666-6","77777777-7","88888888-8"],
        "nombre": ["Ana Rojas","Benjamín Soto","Camila Pérez","Diego Muñoz","Elena Vargas","Felipe Díaz","Gabriela León","Hugo Silva"],
        "carrera": ["Ciencias de la Actividad Física y del Deporte"]*8,
        "sede": ["Santiago"]*8,
        "cohorte": ["2026"]*4 + ["2025"]*4,
        "ciclo": ["Inicial","Inicial","Intermedio","Intermedio","Intermedio","Avanzado","Avanzado","Avanzado"],
    })
    lines = pd.DataFrame({
        "linea_id": ["L1","L2","L3","L4","L5","L6","L7","L8"],
        "linea_formativa": ["Fundamentos de la AF","Evaluación funcional","Prescripción del ejercicio","Intervención en contextos reales","Gestión deportiva","Investigación aplicada","Ética y responsabilidad","Comunicación y liderazgo"],
        "meta_logro_pct": [85,85,85,85,85,85,85,85],
    })
    ra = pd.DataFrame({
        "ra_id": ["RA1","RA2","RA3","RA4","RA5","RA6","RA7","RA8"],
        "resultado_aprendizaje": ["Comprende fundamentos de la actividad física","Aplica evaluaciones funcionales","Diseña programas de ejercicio","Interviene en contextos reales","Gestiona procesos deportivos","Analiza evidencia científica","Actúa con responsabilidad profesional","Comunica y lidera equipos"],
        "linea_id": ["L1","L2","L3","L4","L5","L6","L7","L8"],
    })
    ponder = pd.DataFrame({"tipo_evaluacion": ["Prueba","Práctica","Interciclo","Nacional"], "peso_pct": [30,40,20,10]})
    recs = []
    for _, r in lines.iterrows():
        for desde, hasta, crit, accion in [
            (0, 9, "Baja", "Mantener seguimiento y retroalimentación formativa."),
            (10, 19, "Media", "Implementar taller de reforzamiento aplicado y revisión de evidencias."),
            (20, 100, "Alta", "Activar plan de mejora curricular con acciones remediales, seguimiento y evidencia formal."),
        ]:
            recs.append({"linea_id": r["linea_id"], "umbral_desde_pct": desde, "umbral_hasta_pct": hasta, "criticidad": crit, "accion_sugerida": accion, "evidencia_requerida": "Acta, planificación, asistencia, evaluación pre-post e informe de seguimiento."})
    recs = pd.DataFrame(recs)
    rows = []
    rng = np.random.default_rng(9)
    cortes = ["I Corte", "II Corte", "III Corte"]
    for _, s in students.iterrows():
        for _, l in lines.iterrows():
            for corte in cortes:
                base = rng.normal(74, 10)
                if l["linea_id"] in ["L2", "L3"]:
                    base -= 9
                logro = float(np.clip(base, 40, 98))
                nota = round(1 + (logro/100)*6, 1)
                rows.append({"student_id": s["student_id"], "asignatura": "Asignatura integradora", "ra_id": "RA" + l["linea_id"][1:], "linea_id": l["linea_id"], "tipo_evaluacion": rng.choice(["Prueba","Práctica","Interciclo"]), "corte": corte, "logro_pct": round(logro,1), "nota_1a7": nota})
    evals = pd.DataFrame(rows)
    return {"Estudiantes": students, "Evaluaciones": evals, "Config_Lineas": lines, "Config_RA": ra, "Ponderaciones": ponder, "Recomendaciones": recs}


def template_bytes():
    data = sample_data()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for sheet in REQUIRED_SHEETS:
            data[sheet].to_excel(writer, index=False, sheet_name=sheet)
    return output.getvalue()


def read_workbook(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    missing = [s for s in REQUIRED_SHEETS if s not in xls.sheet_names]
    if missing:
        raise ValueError(f"Faltan hojas obligatorias: {', '.join(missing)}")
    data = {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in REQUIRED_SHEETS}
    return normalize_columns(data)


def normalize_columns(data):
    for k in data:
        data[k].columns = [str(c).strip() for c in data[k].columns]
    return data


def compute_line_summary(data, cohort_filter="Todas", cut_filter="Todos", cycle_filter="Todos", student_filter="Todos"):
    evals = data["Evaluaciones"].copy()
    students = data["Estudiantes"][["student_id", "nombre", "carrera", "cohorte", "ciclo"]].copy()
    lines = data["Config_Lineas"][["linea_id", "linea_formativa", "meta_logro_pct"]].copy()
    evals = evals.merge(students, on="student_id", how="left")
    evals = evals.merge(lines, on="linea_id", how="left")
    if cohort_filter != "Todas":
        evals = evals[evals["cohorte"].astype(str) == str(cohort_filter)]
    if cut_filter != "Todos":
        evals = evals[evals["corte"].astype(str) == str(cut_filter)]
    if cycle_filter != "Todos":
        evals = evals[evals["ciclo"].astype(str) == str(cycle_filter)]
    if student_filter != "Todos":
        evals = evals[evals["nombre"].astype(str) == str(student_filter)]
    if evals.empty:
        return evals, pd.DataFrame()
    summary = evals.groupby(["linea_id", "linea_formativa", "meta_logro_pct"], as_index=False).agg(
        logro_actual_pct=("logro_pct", "mean"), evaluaciones=("logro_pct", "count"), nota_promedio=("nota_1a7", "mean")
    )
    summary["logro_actual_pct"] = summary["logro_actual_pct"].round(1)
    summary["nota_promedio"] = summary["nota_promedio"].round(2)
    summary["brecha_pct"] = (summary["logro_actual_pct"] - summary["meta_logro_pct"]).round(1)
    summary["criticidad"] = pd.cut(-summary["brecha_pct"], bins=[-999,0,10,20,999], labels=["Sin brecha","Baja","Media","Alta"]).astype(str)
    return evals, summary.sort_values("brecha_pct")


def radar_chart(summary):
    df = summary.sort_values("linea_formativa")
    labels = df["linea_formativa"].tolist()
    actual = df["logro_actual_pct"].tolist()
    meta = df["meta_logro_pct"].tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=meta + meta[:1], theta=labels + labels[:1], fill="toself", name="Meta esperada"))
    fig.add_trace(go.Scatterpolar(r=actual + actual[:1], theta=labels + labels[:1], fill="toself", name="Logro actual"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])), showlegend=True, height=520, margin=dict(l=30,r=30,t=30,b=30))
    return fig


def evolution_chart(evals):
    if "corte" not in evals.columns or evals.empty:
        return go.Figure()
    df = evals.groupby("corte", as_index=False)["logro_pct"].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["corte"], y=df["logro_pct"], mode="lines+markers", name="Logro global"))
    fig.update_layout(yaxis=dict(range=[0,100], title="Logro %"), xaxis_title="Corte", height=360, margin=dict(l=20,r=20,t=25,b=20))
    return fig


def recommendations(summary, data):
    rec = data["Recomendaciones"].copy()
    rows = []
    for _, row in summary.iterrows():
        deficit = max(0, -float(row["brecha_pct"]))
        match = rec[(rec["linea_id"] == row["linea_id"]) & (rec["umbral_desde_pct"] <= deficit) & (rec["umbral_hasta_pct"] >= deficit)]
        if match.empty:
            match = rec[rec["linea_id"] == row["linea_id"]].head(1)
        if not match.empty:
            m = match.iloc[0]
            rows.append({"Línea formativa": row["linea_formativa"], "Logro actual": f"{row['logro_actual_pct']}%", "Meta": f"{row['meta_logro_pct']}%", "Brecha": f"{row['brecha_pct']}%", "Criticidad": row["criticidad"], "Acción sugerida": m["accion_sugerida"], "Evidencia requerida": m["evidencia_requerida"]})
    return pd.DataFrame(rows)


def to_excel_bytes(summary, recs, evals):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        summary.to_excel(writer, index=False, sheet_name="Diagnostico")
        recs.to_excel(writer, index=False, sheet_name="Recomendaciones")
        evals.to_excel(writer, index=False, sheet_name="Datos_filtrados")
    return output.getvalue()


st.title("PerfilEgreso 360")
st.caption("Sistema MVP para visualización, diagnóstico, recomendaciones y reportes del Perfil de Egreso.")
st.markdown('<div class="hero"><b>Flujo:</b> Captura de datos → Configuración del modelo → Análisis por corte/cohorte → Recomendaciones de calidad → Reportes exportables.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Módulos")
    page = st.radio("Selecciona", ["1. Captura de datos", "2. Configuración", "3. Dashboard y diagnóstico", "4. Recomendaciones", "5. Reportes"], label_visibility="collapsed")
    uploaded = st.file_uploader("Sube la plantilla institucional Excel", type=["xlsx"])
    use_sample = st.toggle("Usar datos de ejemplo", value=False)
    st.download_button("Descargar plantilla modelo", data=template_bytes(), file_name="plantilla_perfilegreso360.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("**Hojas requeridas:** Estudiantes, Evaluaciones, Config_Lineas, Config_RA, Ponderaciones y Recomendaciones.")

if use_sample:
    data = sample_data()
elif uploaded is not None:
    try:
        data = read_workbook(uploaded)
    except Exception as e:
        st.error(str(e))
        st.stop()
else:
    data = None

if page == "1. Captura de datos":
    st.header("1. Captura de datos")
    st.write("Permite cargar información institucional desde Excel para iniciar el análisis de logro del perfil de egreso.")
    st.info("Puedes subir tu Excel en la barra lateral o activar datos de ejemplo para revisar el sistema completo.")
    st.dataframe(pd.DataFrame({"Hoja requerida": REQUIRED_SHEETS, "Estado": ["Obligatoria"]*len(REQUIRED_SHEETS)}), use_container_width=True, hide_index=True)
    if data:
        st.success("Archivo cargado correctamente.")
        cols = st.columns(6)
        for i, sheet in enumerate(REQUIRED_SHEETS):
            cols[i % 6].metric(sheet, f"{len(data[sheet])} filas")
    st.stop()

if data is None:
    st.warning("Carga una plantilla Excel o activa 'Usar datos de ejemplo' para visualizar los módulos.")
    st.stop()

students = data["Estudiantes"]
evals_raw = data["Evaluaciones"].merge(students[["student_id", "nombre", "cohorte", "ciclo"]], on="student_id", how="left")
cohorts = ["Todas"] + sorted(evals_raw["cohorte"].dropna().astype(str).unique().tolist())
cuts = ["Todos"] + sorted(evals_raw["corte"].dropna().astype(str).unique().tolist())
cycles = ["Todos"] + sorted(evals_raw["ciclo"].dropna().astype(str).unique().tolist())
students_list = ["Todos"] + sorted(evals_raw["nombre"].dropna().astype(str).unique().tolist())

f1, f2, f3, f4 = st.columns(4)
cohort_filter = f1.selectbox("Cohorte", cohorts)
cut_filter = f2.selectbox("Corte", cuts)
cycle_filter = f3.selectbox("Ciclo", cycles)
student_filter = f4.selectbox("Estudiante", students_list)

evals, summary = compute_line_summary(data, cohort_filter, cut_filter, cycle_filter, student_filter)
recs = recommendations(summary, data) if not summary.empty else pd.DataFrame()

if summary.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

if page == "2. Configuración":
    st.header("2. Configuración del modelo")
    tabs = st.tabs(["Líneas formativas", "Resultados de aprendizaje", "Ponderaciones"])
    tabs[0].dataframe(data["Config_Lineas"], use_container_width=True, hide_index=True)
    tabs[1].dataframe(data["Config_RA"], use_container_width=True, hide_index=True)
    tabs[2].dataframe(data["Ponderaciones"], use_container_width=True, hide_index=True)

elif page == "3. Dashboard y diagnóstico":
    st.header("3. Dashboard y diagnóstico por corte/cohorte")
    logro_global = summary["logro_actual_pct"].mean().round(1)
    brechas_altas = int((summary["criticidad"] == "Alta").sum())
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Logro global", f"{logro_global}%")
    m2.metric("Líneas evaluadas", summary["linea_id"].nunique())
    m3.metric("Estudiantes evaluados", evals["student_id"].nunique())
    m4.metric("Brechas críticas", brechas_altas)
    left, right = st.columns([1.1,1])
    with left:
        st.subheader("Radar del Perfil de Egreso")
        st.plotly_chart(radar_chart(summary), use_container_width=True)
    with right:
        st.subheader("Brechas por línea formativa")
        show = summary[["linea_formativa","logro_actual_pct","meta_logro_pct","brecha_pct","criticidad"]].copy()
        show.columns = ["Línea formativa","Logro actual","Meta","Brecha","Criticidad"]
        st.dataframe(show, use_container_width=True, hide_index=True)
    st.subheader("Evolución por corte")
    st.plotly_chart(evolution_chart(evals), use_container_width=True)

elif page == "4. Recomendaciones":
    st.header("4. Recomendaciones y aseguramiento de la calidad")
    st.write("El sistema transforma las brechas detectadas en acciones de mejora trazables.")
    st.dataframe(recs, use_container_width=True, hide_index=True)

elif page == "5. Reportes":
    st.header("5. Reportes y exportación")
    st.write("Exporta el diagnóstico filtrado, las recomendaciones y los datos utilizados para análisis institucional.")
    excel_bytes = to_excel_bytes(summary, recs, evals)
    st.download_button("Descargar reporte Excel", data=excel_bytes, file_name=f"reporte_perfilegreso360_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.subheader("Vista previa del diagnóstico")
    st.dataframe(summary, use_container_width=True, hide_index=True)
