import io
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="PerfilEgreso 360", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.2rem;}
.metric-card {border: 1px solid #e5e7eb; border-radius: 14px; padding: 14px; background: #ffffff;}
.small-muted {font-size: 0.86rem; color: #64748b;}
</style>
""", unsafe_allow_html=True)

REQUIRED_SHEETS = ["Estudiantes", "Evaluaciones", "Config_Lineas", "Config_RA", "Ponderaciones", "Recomendaciones"]


def read_workbook(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    missing = [s for s in REQUIRED_SHEETS if s not in xls.sheet_names]
    if missing:
        raise ValueError(f"Faltan hojas obligatorias: {', '.join(missing)}")
    return {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in REQUIRED_SHEETS}


def compute_line_summary(data, cohort_filter=None, cut_filter=None, student_filter=None):
    evals = data["Evaluaciones"].copy()
    students = data["Estudiantes"][["student_id", "nombre", "carrera", "cohorte", "ciclo"]]
    lines = data["Config_Lineas"][["linea_id", "linea_formativa", "meta_logro_pct"]]
    evals = evals.merge(students, on="student_id", how="left")
    evals = evals.merge(lines, on="linea_id", how="left")

    if cohort_filter and cohort_filter != "Todas":
        evals = evals[evals["cohorte"].astype(str) == str(cohort_filter)]
    if cut_filter and cut_filter != "Todos":
        evals = evals[evals["corte"].astype(str) == str(cut_filter)]
    if student_filter and student_filter != "Todos":
        evals = evals[evals["nombre"].astype(str) == str(student_filter)]

    if evals.empty:
        return evals, pd.DataFrame()

    summary = evals.groupby(["linea_id", "linea_formativa", "meta_logro_pct"], as_index=False).agg(
        logro_actual_pct=("logro_pct", "mean"),
        evaluaciones=("logro_pct", "count"),
        nota_promedio=("nota_1a7", "mean"),
    )
    summary["logro_actual_pct"] = summary["logro_actual_pct"].round(1)
    summary["nota_promedio"] = summary["nota_promedio"].round(2)
    summary["brecha_pct"] = (summary["logro_actual_pct"] - summary["meta_logro_pct"]).round(1)
    summary["criticidad"] = pd.cut(
        -summary["brecha_pct"],
        bins=[-999, 0, 10, 20, 999],
        labels=["Sin brecha", "Baja", "Media", "Alta"],
    ).astype(str)
    return evals, summary.sort_values("brecha_pct")


def radar_chart(summary):
    if summary.empty:
        return go.Figure()
    df = summary.sort_values("linea_formativa")
    labels = df["linea_formativa"].tolist()
    actual = df["logro_actual_pct"].tolist()
    meta = df["meta_logro_pct"].tolist()
    labels_closed = labels + labels[:1]
    actual_closed = actual + actual[:1]
    meta_closed = meta + meta[:1]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=meta_closed, theta=labels_closed, fill="toself", name="Meta esperada"))
    fig.add_trace(go.Scatterpolar(r=actual_closed, theta=labels_closed, fill="toself", name="Logro actual"))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        margin=dict(l=30, r=30, t=30, b=30),
        height=520,
    )
    return fig


def recommendations(summary, data):
    if summary.empty:
        return pd.DataFrame()
    rec = data["Recomendaciones"].copy()
    rows = []
    for _, row in summary.iterrows():
        deficit = max(0, -float(row["brecha_pct"]))
        match = rec[(rec["linea_id"] == row["linea_id"]) & (rec["umbral_desde_pct"] <= deficit) & (rec["umbral_hasta_pct"] >= deficit)]
        if match.empty:
            match = rec[rec["linea_id"] == row["linea_id"]].head(1)
        if not match.empty:
            m = match.iloc[0]
            rows.append({
                "Línea formativa": row["linea_formativa"],
                "Logro actual": f"{row['logro_actual_pct']}%",
                "Meta": f"{row['meta_logro_pct']}%",
                "Brecha": f"{row['brecha_pct']}%",
                "Criticidad": row["criticidad"],
                "Acción sugerida": m["accion_sugerida"],
                "Evidencia requerida": m["evidencia_requerida"],
            })
    return pd.DataFrame(rows)


def to_excel_bytes(summary, recs, evals):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        summary.to_excel(writer, index=False, sheet_name="Diagnóstico")
        recs.to_excel(writer, index=False, sheet_name="Recomendaciones")
        evals.to_excel(writer, index=False, sheet_name="Datos filtrados")
    return output.getvalue()


st.title("PerfilEgreso 360")
st.caption("MVP para visualización, diagnóstico y mejora del logro del Perfil de Egreso.")

with st.sidebar:
    st.header("1. Cargar datos")
    uploaded = st.file_uploader("Sube la plantilla institucional Excel", type=["xlsx"])
    st.markdown("**Hojas requeridas:** Estudiantes, Evaluaciones, Config_Lineas, Config_RA, Ponderaciones y Recomendaciones.")

if uploaded is None:
    st.info("Carga la plantilla Excel para iniciar el análisis.")
    st.stop()

try:
    data = read_workbook(uploaded)
except Exception as e:
    st.error(str(e))
    st.stop()

students = data["Estudiantes"]
evals_raw = data["Evaluaciones"].merge(students[["student_id", "nombre", "cohorte"]], on="student_id", how="left")
cohorts = ["Todas"] + sorted(evals_raw["cohorte"].dropna().astype(str).unique().tolist())
cuts = ["Todos"] + sorted(evals_raw["corte"].dropna().astype(str).unique().tolist())
students_list = ["Todos"] + sorted(evals_raw["nombre"].dropna().astype(str).unique().tolist())

c1, c2, c3 = st.columns(3)
cohort_filter = c1.selectbox("Cohorte", cohorts)
cut_filter = c2.selectbox("Corte académico", cuts)
student_filter = c3.selectbox("Estudiante", students_list)

evals, summary = compute_line_summary(data, cohort_filter, cut_filter, student_filter)
recs = recommendations(summary, data)

if summary.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

logro_global = summary["logro_actual_pct"].mean().round(1)
brechas_altas = int((summary["criticidad"] == "Alta").sum())
estudiantes = evals["student_id"].nunique()
lineas = summary["linea_id"].nunique()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Logro global", f"{logro_global}%")
m2.metric("Líneas evaluadas", lineas)
m3.metric("Estudiantes evaluados", estudiantes)
m4.metric("Brechas críticas", brechas_altas)

left, right = st.columns([1.1, 1])
with left:
    st.subheader("Radar del Perfil de Egreso")
    st.plotly_chart(radar_chart(summary), use_container_width=True)
with right:
    st.subheader("Brechas por línea formativa")
    show = summary[["linea_formativa", "logro_actual_pct", "meta_logro_pct", "brecha_pct", "criticidad"]].copy()
    show.columns = ["Línea formativa", "Logro actual", "Meta", "Brecha", "Criticidad"]
    st.dataframe(show, use_container_width=True, hide_index=True)

st.subheader("Recomendaciones de aseguramiento de la calidad")
st.dataframe(recs, use_container_width=True, hide_index=True)

st.subheader("Exportación")
excel_bytes = to_excel_bytes(summary, recs, evals)
st.download_button(
    "Descargar reporte Excel",
    data=excel_bytes,
    file_name=f"reporte_perfilegreso360_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.caption("Siguiente etapa del MVP: exportación PDF institucional, gestión de usuarios, historial de cargas y panel por carrera/facultad.")
