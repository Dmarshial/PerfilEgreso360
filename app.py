import os
import io
import base64
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# =========================================================
# PERFIL EGRESO 360 · V4
# Plataforma ejecutiva para lectura de actas institucionales,
# análisis del Perfil de Egreso, brechas, reportes y módulo IA.
# =========================================================

st.set_page_config(
    page_title="PerfilEgreso 360",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

BRAND = {
    "name": "PerfilEgreso 360",
    "subtitle": "Gobierno académico del Perfil de Egreso",
    "institution": "USEK · IDAF",
    "primary": "#08234A",
    "secondary": "#0E4D92",
    "accent": "#00A6A6",
    "accent2": "#F05A5B",
    "bg": "#F4F7FB",
    "card": "#FFFFFF",
    "text": "#111827",
    "muted": "#64748B",
}

# -----------------------------
# CSS ejecutivo con alto contraste
# -----------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
    .stApp {{ background: linear-gradient(180deg, #f7faff 0%, #eef3f9 100%); }}
    section[data-testid="stSidebar"] {{ background: #071A33 !important; border-right: 1px solid rgba(255,255,255,.08); }}
    section[data-testid="stSidebar"] * {{ color: #F8FAFC !important; }}
    section[data-testid="stSidebar"] .stRadio label {{ color: #F8FAFC !important; font-weight: 650; }}
    section[data-testid="stSidebar"] .stSelectbox label, section[data-testid="stSidebar"] .stFileUploader label {{ color: #F8FAFC !important; }}
    .block-container {{ padding-top: 1.4rem; max-width: 1500px; }}
    .brand-wrap {{
        background: linear-gradient(135deg, #061B36 0%, #0E3B75 54%, #123B55 100%);
        color: white; border-radius: 30px; padding: 36px 42px; box-shadow: 0 28px 75px rgba(8,35,74,.22);
        border: 1px solid rgba(255,255,255,.10); margin-bottom: 26px; position: relative; overflow: hidden;
    }}
    .brand-wrap:after {{ content: ''; position: absolute; right: -100px; top: -120px; width: 460px; height: 460px; background: radial-gradient(circle, rgba(0,166,166,.33), transparent 65%); }}
    .brand-row {{ display:flex; align-items:center; justify-content:space-between; gap: 28px; position: relative; z-index:2; }}
    .brand-left {{ flex: 1.1; }}
    .logo-box {{ width: 78px; height: 78px; border-radius: 22px; display:flex; align-items:center; justify-content:center; font-size: 26px; font-weight:900; color:white; background: linear-gradient(135deg, #16A3D8 0%, #7B61FF 52%, #F05A5B 100%); box-shadow: 0 18px 35px rgba(0,0,0,.23); }}
    .brand-title {{ font-size: 3.0rem; line-height: 1.0; font-weight: 900; margin: 16px 0 10px 0; letter-spacing:-.04em; }}
    .brand-sub {{ font-size: 1.04rem; color: #DDEBFF; max-width: 920px; }}
    .hero-people {{ flex:.75; min-height: 210px; border-radius: 24px; background: rgba(255,255,255,.09); border: 1px solid rgba(255,255,255,.16); display:flex; align-items:center; justify-content:center; padding:18px; }}
    .chip-row {{ display:flex; flex-wrap:wrap; gap: 10px; margin-top: 22px; }}
    .chip {{ padding: 10px 14px; border-radius: 999px; background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.18); color:#fff; font-weight:800; font-size:.88rem; }}
    .card {{ background: #FFFFFF; border-radius: 22px; padding: 22px; border: 1px solid #E2E8F0; box-shadow: 0 16px 45px rgba(15, 23, 42, .07); }}
    .metric-card {{ background: #FFFFFF; border-radius: 20px; padding: 22px; border:1px solid #E2E8F0; box-shadow: 0 14px 36px rgba(15,23,42,.06); min-height: 140px; }}
    .metric-label {{ font-size: .75rem; color: #64748B; font-weight:900; text-transform:uppercase; letter-spacing:.08em; }}
    .metric-value {{ font-size: 2.25rem; color: #08234A; font-weight:900; margin-top: 12px; letter-spacing:-.04em; }}
    .metric-help {{ font-size: .88rem; color:#64748B; margin-top:4px; }}
    .section-title {{ color:#08234A; font-weight:900; font-size:2rem; letter-spacing:-.03em; margin: 16px 0 8px; }}
    .section-subtitle {{ color:#64748B; font-size:1rem; margin-bottom: 20px; }}
    .dark-panel {{ background: linear-gradient(135deg, #071A33, #0B2D5C); color:white; border-radius:24px; padding:24px; border: 1px solid rgba(255,255,255,.12); box-shadow: 0 20px 50px rgba(8,35,74,.18); }}
    .dark-panel h3, .dark-panel h4, .dark-panel p, .dark-panel li {{ color:white !important; }}
    .alert-badge {{ display:inline-block; padding:7px 12px; border-radius:999px; background:#FEE2E2; color:#991B1B; font-weight:900; font-size:.82rem; }}
    .ok-badge {{ display:inline-block; padding:7px 12px; border-radius:999px; background:#DCFCE7; color:#166534; font-weight:900; font-size:.82rem; }}
    .warn-badge {{ display:inline-block; padding:7px 12px; border-radius:999px; background:#FEF3C7; color:#92400E; font-weight:900; font-size:.82rem; }}
    .explain {{ background: #ECFDF5; border-left: 6px solid #00A6A6; border-radius: 14px; padding: 16px 18px; color:#064E3B; margin: 14px 0; }}
    .info-box {{ background: #EFF6FF; border-left: 6px solid #0E4D92; border-radius: 14px; padding: 16px 18px; color:#1E3A8A; margin: 14px 0; }}
    .footer {{ color:#64748B; font-size:.85rem; padding: 30px 0 8px; }}
    div[data-testid="stDataFrame"] {{ border-radius: 18px; overflow:hidden; }}
    .stButton > button {{ border-radius: 999px; font-weight:800; border: 1px solid #CBD5E1; padding: .55rem 1.1rem; }}
    .stDownloadButton > button {{ border-radius: 999px; font-weight:800; background:#08234A; color:white; border:0; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Ilustración SVG institucional generada por código
# -----------------------------
def people_svg() -> str:
    svg = """
    <svg width="420" height="230" viewBox="0 0 420 230" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="420" height="230" rx="28" fill="url(#g)"/>
      <circle cx="338" cy="58" r="56" fill="#00A6A6" fill-opacity="0.22"/>
      <circle cx="92" cy="185" r="72" fill="#7B61FF" fill-opacity="0.18"/>
      <rect x="62" y="125" width="298" height="52" rx="18" fill="white" fill-opacity="0.16" stroke="white" stroke-opacity="0.26"/>
      <rect x="83" y="143" width="104" height="9" rx="4.5" fill="white" fill-opacity="0.76"/>
      <rect x="83" y="158" width="158" height="7" rx="3.5" fill="white" fill-opacity="0.38"/>
      <rect x="252" y="140" width="78" height="26" rx="13" fill="#F05A5B" fill-opacity="0.92"/>
      <circle cx="152" cy="81" r="28" fill="#DDEBFF"/>
      <path d="M98 124C105 92 127 78 152 78C177 78 199 92 206 124" fill="#DDEBFF" fill-opacity="0.90"/>
      <circle cx="230" cy="72" r="24" fill="#A7F3D0"/>
      <path d="M188 120C194 93 211 81 230 81C250 81 267 93 273 120" fill="#A7F3D0" fill-opacity="0.9"/>
      <circle cx="292" cy="91" r="20" fill="#FECACA"/>
      <path d="M258 124C263 102 276 92 292 92C309 92 322 102 327 124" fill="#FECACA" fill-opacity="0.9"/>
      <path d="M56 58H125" stroke="white" stroke-opacity="0.7" stroke-width="8" stroke-linecap="round"/>
      <path d="M56 78H101" stroke="white" stroke-opacity="0.35" stroke-width="7" stroke-linecap="round"/>
      <defs><linearGradient id="g" x1="0" y1="0" x2="420" y2="230"><stop stop-color="#0E4D92"/><stop offset="1" stop-color="#071A33"/></linearGradient></defs>
    </svg>
    """
    return base64.b64encode(svg.encode()).decode()

# -----------------------------
# Funciones de lectura y normalización
# -----------------------------
LINEA_MAP = {
    "PSICOLOGIA": "Psicología, Salud y Conducta Motriz",
    "TEORIA DEL ENTRENAMIENTO": "Entrenamiento y Prescripción del Ejercicio",
    "FISIOLOGIA": "Ciencias Morfofuncionales y Fisiología",
    "FITNESS": "Práctica Aplicada y Acondicionamiento",
    "ANATOMIA": "Ciencias Morfofuncionales y Fisiología",
    "LESIONES": "Prevención, Recuperación y Seguridad",
}

COMPETENCIA_MAP = {
    "PSICOLOGIA": "Analizar factores psicosociales asociados a la actividad física y salud.",
    "TEORIA DEL ENTRENAMIENTO": "Planificar procesos de entrenamiento físico según objetivos y contexto.",
    "FISIOLOGIA": "Interpretar respuestas fisiológicas vinculadas al ejercicio físico.",
    "FITNESS": "Aplicar sesiones prácticas de acondicionamiento físico seguro.",
    "ANATOMIA": "Relacionar estructuras anatómicas con movimiento y ejercicio.",
    "LESIONES": "Reconocer principios de prevención y recuperación funcional en actividad física.",
}

def _clean_text(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

def normalize_note(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, str):
        x = x.strip().replace(",", ".")
        if x in ["/", "", "nan", "NaN"]:
            return np.nan
    try:
        val = float(x)
        if val < 1 or val > 7:
            return np.nan
        return val
    except Exception:
        return np.nan

def note_to_pct(note):
    if pd.isna(note):
        return np.nan
    # Escala 1.0-7.0 a 0-100, con 4.0 como umbral de aprobación 50% aprox.
    return max(0, min(100, (float(note) - 1.0) / 6.0 * 100))

def find_carrera_and_year(raw: pd.DataFrame) -> Tuple[str, str, str]:
    carrera = "Carrera no identificada"
    year = ""
    periodo = ""
    for _, row in raw.iterrows():
        vals = [str(v) for v in row.tolist() if not pd.isna(v)]
        txt = " | ".join(vals)
        if "TECNICO" in txt.upper() or "CARRERA" in txt.upper():
            for v in vals:
                if "TECNICO" in v.upper() or "CIENCIAS" in v.upper():
                    carrera = v.strip()
        if "AÑO" in txt.upper():
            year = txt.split("AÑO:")[-1].strip() if "AÑO:" in txt else year
        if "Periodo" in txt or "PERIODO" in txt.upper():
            periodo = txt.split(":")[-1].strip()
    return carrera, year, periodo

def subject_line(subject: str) -> str:
    u = subject.upper()
    for k, v in LINEA_MAP.items():
        if k in u:
            return v
    return "Formación Disciplinar Integrada"

def subject_comp(subject: str) -> str:
    u = subject.upper()
    for k, v in COMPETENCIA_MAP.items():
        if k in u:
            return v
    return f"Integrar aprendizajes asociados a {subject.title()}."

def parse_acta_sheet(raw: pd.DataFrame, sheet_name: str = "Sheet") -> Dict[str, pd.DataFrame]:
    carrera, year, periodo = find_carrera_and_year(raw)
    # En el archivo USEK: fila 10 asignaturas, fila 11 subcolumnas NF/%A, datos desde fila 12.
    # Buscamos fila que contenga N° ORDEN y R.U.T.
    header_row = None
    for i in range(min(25, len(raw))):
        joined = " ".join([_clean_text(x).upper() for x in raw.iloc[i].tolist()])
        if "N° ORDEN" in joined or "Nº ORDEN" in joined or "R.U.T" in joined:
            header_row = i
            break
    if header_row is None:
        header_row = 11
    subject_row = max(0, header_row - 1)

    subjects = []
    for col in range(raw.shape[1] - 1):
        sub_header = _clean_text(raw.iat[header_row, col]).upper()
        subj_name = _clean_text(raw.iat[subject_row, col])
        if sub_header == "NF" and subj_name:
            subjects.append((col, subj_name))
        # A veces la asignatura está en columna anterior y NF debajo en col actual.
        elif sub_header == "NF" and col > 0 and _clean_text(raw.iat[subject_row, col-1]):
            subjects.append((col, _clean_text(raw.iat[subject_row, col-1])))

    records_students = []
    records_eval = []
    start = header_row + 1
    for ridx in range(start, len(raw)):
        orden = _clean_text(raw.iat[ridx, 0]) if raw.shape[1] > 0 else ""
        rut = _clean_text(raw.iat[ridx, 4]) if raw.shape[1] > 4 else ""
        if not orden or not rut or rut.lower() == "nan":
            continue
        paterno = _clean_text(raw.iat[ridx, 1])
        materno = _clean_text(raw.iat[ridx, 2])
        nombres = _clean_text(raw.iat[ridx, 3])
        nombre = " ".join([nombres, paterno, materno]).strip().title()
        student_id = rut if rut else str(orden)
        situacion = _clean_text(raw.iat[ridx, 29]) if raw.shape[1] > 29 else ""
        records_students.append({
            "student_id": student_id,
            "rut": rut,
            "nombre": nombre,
            "cohorte": year or "2025",
            "carrera": carrera,
            "sede": "Santiago",
            "semestre": periodo or "2",
            "situacion": situacion,
            "origen": sheet_name,
        })
        for col, subj in subjects:
            nota = normalize_note(raw.iat[ridx, col]) if col < raw.shape[1] else np.nan
            asistencia = raw.iat[ridx, col + 1] if col + 1 < raw.shape[1] else np.nan
            if not pd.isna(nota):
                linea = subject_line(subj)
                comp = subject_comp(subj)
                records_eval.append({
                    "student_id": student_id,
                    "nombre": nombre,
                    "cohorte": year or "2025",
                    "carrera": carrera,
                    "asignatura": subj.strip().title(),
                    "linea": linea,
                    "competencia": comp,
                    "tipo_evaluacion": "Acta semestral NF",
                    "nota_1a7": nota,
                    "logro_pct": round(note_to_pct(nota), 1),
                    "asistencia_pct": pd.to_numeric(asistencia, errors="coerce"),
                    "alerta_temprana": "Sí" if nota < 4.0 else "No",
                    "origen": sheet_name,
                })
    return {
        "students": pd.DataFrame(records_students).drop_duplicates("student_id") if records_students else pd.DataFrame(),
        "evals": pd.DataFrame(records_eval),
        "meta": pd.DataFrame([{"carrera": carrera, "anio": year, "periodo": periodo}]),
    }

def read_workbook(file) -> Dict[str, pd.DataFrame]:
    data = {}
    xl = pd.ExcelFile(file)
    required = {"Estudiantes", "Evaluaciones", "Config_Lineas", "Config_RA", "Ponderaciones", "Recomendaciones"}
    if required.issubset(set(xl.sheet_names)):
        students = pd.read_excel(file, sheet_name="Estudiantes")
        evals = pd.read_excel(file, sheet_name="Evaluaciones")
        lineas = pd.read_excel(file, sheet_name="Config_Lineas")
        recs = pd.read_excel(file, sheet_name="Recomendaciones")
        # normalización
        students.columns = [str(c).strip() for c in students.columns]
        evals.columns = [str(c).strip() for c in evals.columns]
        # nombres esperados flexibles
        rename = {
            "ID_Estudiante": "student_id", "Nombre": "nombre", "Cohorte": "cohorte", "Rut": "rut", "Carrera": "carrera",
            "Asignatura": "asignatura", "Nota": "nota_1a7", "Tipo_Evaluacion": "tipo_evaluacion", "ID_RA": "id_ra",
            "Nombre_Linea": "linea", "Meta_Logro": "meta_logro", "Linea": "linea", "Recomendacion": "recomendacion",
        }
        students = students.rename(columns={k:v for k,v in rename.items() if k in students.columns})
        evals = evals.rename(columns={k:v for k,v in rename.items() if k in evals.columns})
        if "nota_1a7" in evals.columns and "logro_pct" not in evals.columns:
            evals["logro_pct"] = evals["nota_1a7"].apply(note_to_pct)
        if "linea" not in evals.columns:
            # Mapear por asignatura
            evals["linea"] = evals["asignatura"].apply(subject_line) if "asignatura" in evals.columns else "Línea formativa"
        if "competencia" not in evals.columns:
            evals["competencia"] = evals["asignatura"].apply(subject_comp) if "asignatura" in evals.columns else "Competencia del perfil de egreso"
        if "nombre" not in evals.columns and "student_id" in evals.columns and "student_id" in students.columns:
            evals = evals.merge(students[["student_id", "nombre", "cohorte"]].drop_duplicates("student_id"), on="student_id", how="left")
        data = {"students": students, "evals": evals, "lineas_cfg": lineas, "recs": recs, "meta": pd.DataFrame()}
        return data

    # Si no tiene la plantilla, asumimos acta institucional USEK u otro acta ancha.
    all_students, all_evals, all_meta = [], [], []
    for s in xl.sheet_names:
        raw = pd.read_excel(file, sheet_name=s, header=None)
        parsed = parse_acta_sheet(raw, s)
        if not parsed["students"].empty:
            all_students.append(parsed["students"])
        if not parsed["evals"].empty:
            all_evals.append(parsed["evals"])
        all_meta.append(parsed["meta"])
    students = pd.concat(all_students, ignore_index=True).drop_duplicates("student_id") if all_students else pd.DataFrame()
    evals = pd.concat(all_evals, ignore_index=True) if all_evals else pd.DataFrame()
    meta = pd.concat(all_meta, ignore_index=True) if all_meta else pd.DataFrame()
    return {"students": students, "evals": evals, "lineas_cfg": pd.DataFrame(), "recs": default_recommendations(), "meta": meta}

def demo_data() -> Dict[str, pd.DataFrame]:
    students = pd.DataFrame({
        "student_id": ["20087089-1", "17416810-5", "22241784-8", "19394875-2", "21555111-1", "18777111-6"],
        "rut": ["20087089-1", "17416810-5", "22241784-8", "19394875-2", "21555111-1", "18777111-6"],
        "nombre": ["Sofía Andrade Huepe", "Marta Arévalo Medina", "Tomás Barrios", "Camila Reyes", "Diego Morales", "Valentina Soto"],
        "cohorte": ["2025"]*6,
        "carrera": ["TNS en Preparación Física"]*6,
        "sede": ["Santiago"]*6,
        "semestre": ["2"]*6,
        "situacion": ["P", "R", "S", "P", "P", "P"],
    })
    subjects = [
        "Psicología de la Actividad Física y la Salud",
        "Teoría del Entrenamiento",
        "Fisiología de la Actividad Física",
        "Fitness y Running (P.T.)",
        "Anatomía Funcional",
        "Lesiones en la Actividad Física",
    ]
    rows = []
    base = {
        "Sofía Andrade Huepe": [5.9,6.5,5.4,6.9,5.8,7.0],
        "Marta Arévalo Medina": [1.0,5.3,5.4,2.9,5.4,7.0],
        "Tomás Barrios": [2.4,1.0, np.nan, 1.0, np.nan,1.0],
        "Camila Reyes": [4.8,5.5,4.9,5.2,5.8,4.1],
        "Diego Morales": [6.3,6.1,5.9,6.5,6.0,5.8],
        "Valentina Soto": [3.8,4.2,4.0,5.2,4.8,3.9],
    }
    for _, strow in students.iterrows():
        notes = base[strow.nombre]
        for subj, note in zip(subjects, notes):
            if not pd.isna(note):
                rows.append({
                    "student_id": strow.student_id,
                    "nombre": strow.nombre,
                    "cohorte": strow.cohorte,
                    "carrera": strow.carrera,
                    "asignatura": subj,
                    "linea": subject_line(subj),
                    "competencia": subject_comp(subj),
                    "tipo_evaluacion": "Demo NF",
                    "nota_1a7": note,
                    "logro_pct": round(note_to_pct(note),1),
                    "asistencia_pct": np.random.choice([60, 71, 72, 76, 80, 90]),
                    "alerta_temprana": "Sí" if note < 4.0 else "No",
                })
    return {"students": students, "evals": pd.DataFrame(rows), "lineas_cfg": pd.DataFrame(), "recs": default_recommendations(), "meta": pd.DataFrame()}

def default_recommendations():
    return pd.DataFrame([
        {"nivel":"Crítica", "brecha_min":20, "brecha_max":100, "recomendacion":"Implementar plan de mejora inmediato: talleres prácticos, reforzamiento docente, evaluación integradora y seguimiento por corte."},
        {"nivel":"Media", "brecha_min":10, "brecha_max":19.9, "recomendacion":"Aplicar acciones de refuerzo focalizadas, tutorías y revisión de instrumentos de evaluación."},
        {"nivel":"Baja", "brecha_min":0, "brecha_max":9.9, "recomendacion":"Mantener seguimiento y retroalimentación formativa para sostener el logro."},
    ])

def compute_analytics(evals: pd.DataFrame, students: pd.DataFrame, meta_goal: float = 85.0) -> Dict[str, pd.DataFrame]:
    if evals.empty:
        return {}
    df = evals.copy()
    df["logro_pct"] = pd.to_numeric(df.get("logro_pct"), errors="coerce")
    df["nota_1a7"] = pd.to_numeric(df.get("nota_1a7"), errors="coerce")
    if "linea" not in df.columns:
        df["linea"] = "Línea formativa"
    if "competencia" not in df.columns:
        df["competencia"] = "Competencia del perfil de egreso"
    lineas = df.groupby("linea", as_index=False).agg(
        logro=("logro_pct", "mean"),
        nota_promedio=("nota_1a7", "mean"),
        evaluaciones=("nota_1a7", "count"),
        estudiantes=("student_id", "nunique"),
    )
    lineas["meta"] = meta_goal
    lineas["brecha"] = (lineas["meta"] - lineas["logro"]).clip(lower=0)
    lineas["criticidad"] = np.select([lineas.brecha>=20, lineas.brecha>=10], ["Crítica", "Media"], default="Baja")
    comps = df.groupby("competencia", as_index=False).agg(logro=("logro_pct","mean"), nota_promedio=("nota_1a7","mean"), evaluaciones=("nota_1a7","count"))
    comps["meta"] = meta_goal
    comps["brecha"] = (comps["meta"] - comps["logro"]).clip(lower=0)
    subjects = df.groupby("asignatura", as_index=False).agg(
        nota_promedio=("nota_1a7", "mean"),
        logro=("logro_pct", "mean"),
        estudiantes=("student_id", "nunique"),
        alertas=("alerta_temprana", lambda s: (s.astype(str).str.lower()=="sí").sum()),
    ).sort_values("alertas", ascending=False)
    indiv = df.groupby(["student_id", "nombre"], as_index=False).agg(
        logro=("logro_pct", "mean"), nota_promedio=("nota_1a7","mean"), alertas=("alerta_temprana", lambda s: (s.astype(str).str.lower()=="sí").sum())
    )
    return {"lineas": lineas, "competencias": comps, "asignaturas": subjects, "individual": indiv, "evals": df, "students": students}

def severity_badge(level: str) -> str:
    if level == "Crítica": return '<span class="alert-badge">Crítica</span>'
    if level == "Media": return '<span class="warn-badge">Media</span>'
    return '<span class="ok-badge">Baja</span>'

# -----------------------------
# Gráficos
# -----------------------------
def fig_radar(lineas: pd.DataFrame, title="Radar del Perfil de Egreso"):
    cats = lineas["linea"].tolist()
    vals = lineas["logro"].round(1).tolist()
    meta = lineas["meta"].round(1).tolist()
    if cats:
        cats2 = cats + [cats[0]]
        vals2 = vals + [vals[0]]
        meta2 = meta + [meta[0]]
    else:
        cats2, vals2, meta2 = [], [], []
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=meta2, theta=cats2, fill='toself', name='Meta esperada', line=dict(color="#00A6A6", width=3), fillcolor='rgba(0,166,166,.12)'))
    fig.add_trace(go.Scatterpolar(r=vals2, theta=cats2, fill='toself', name='Logro actual', line=dict(color="#F05A5B", width=3), fillcolor='rgba(240,90,91,.18)'))
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, color="#08234A")),
        polar=dict(bgcolor="rgba(255,255,255,0)", radialaxis=dict(visible=True, range=[0,100], tickfont=dict(color="#64748B")), angularaxis=dict(tickfont=dict(color="#08234A", size=11))),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-.10), height=500, margin=dict(l=40,r=40,t=70,b=70)
    )
    return fig

def fig_brechas(lineas: pd.DataFrame):
    d = lineas.sort_values("brecha", ascending=True)
    colors = ["#F05A5B" if v>=20 else "#F59E0B" if v>=10 else "#22C55E" for v in d["brecha"]]
    fig = go.Figure(go.Bar(x=d["brecha"], y=d["linea"], orientation='h', marker_color=colors, text=d["brecha"].round(1).astype(str)+" pts", textposition="outside"))
    fig.update_layout(title="Brechas por línea formativa", xaxis_title="Puntos bajo la meta", yaxis_title="", height=430, margin=dict(l=20,r=70,t=60,b=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(range=[0, max(30, float(d["brecha"].max())+8)], gridcolor="#E2E8F0")
    return fig

def fig_alertas(asignaturas: pd.DataFrame):
    d = asignaturas.sort_values("alertas", ascending=True).tail(10)
    fig = go.Figure(go.Bar(x=d["alertas"], y=d["asignatura"], orientation="h", marker_color="#F05A5B", text=d["alertas"], textposition="outside"))
    fig.update_layout(title="Reporte 1 · Alerta temprana por asignatura", xaxis_title="Estudiantes con nota < 4.0", height=430, margin=dict(l=20,r=80,t=60,b=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(gridcolor="#E2E8F0")
    return fig

def fig_horizontal(df: pd.DataFrame, label_col: str, value_col: str, title: str):
    d = df.sort_values(value_col, ascending=True)
    fig = go.Figure(go.Bar(x=d[value_col], y=d[label_col], orientation="h", marker_color="#0E4D92", text=d[value_col].round(1).astype(str)+"%", textposition="outside"))
    fig.update_layout(title=title, xaxis_title="Logro (%)", yaxis_title="", height=max(430, len(d)*55), margin=dict(l=20,r=80,t=60,b=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(range=[0,105], gridcolor="#E2E8F0")
    return fig

# -----------------------------
# Plantilla Excel
# -----------------------------
def create_template() -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        demo = demo_data()
        demo["students"].to_excel(writer, sheet_name="Estudiantes", index=False)
        demo["evals"][ ["student_id","asignatura","linea","competencia","tipo_evaluacion","nota_1a7","logro_pct","asistencia_pct"] ].to_excel(writer, sheet_name="Evaluaciones", index=False)
        pd.DataFrame({"linea": sorted(demo["evals"].linea.unique()), "meta_logro": 85}).to_excel(writer, sheet_name="Config_Lineas", index=False)
        pd.DataFrame({"competencia": sorted(demo["evals"].competencia.unique()), "linea": [subject_line(x) for x in sorted(demo["evals"].asignatura.unique())[:len(sorted(demo["evals"].competencia.unique()))]]}).to_excel(writer, sheet_name="Config_RA", index=False)
        pd.DataFrame({"tipo_evaluacion": ["Prueba", "Práctica", "Acta semestral NF", "Interciclo", "Nacional"], "peso": [30,30,30,5,5]}).to_excel(writer, sheet_name="Ponderaciones", index=False)
        default_recommendations().to_excel(writer, sheet_name="Recomendaciones", index=False)
    return output.getvalue()

# -----------------------------
# IA / análisis narrativo
# -----------------------------
def rules_based_analysis(analytics: Dict[str, pd.DataFrame], carrera="Carrera") -> str:
    if not analytics:
        return "No existen datos suficientes para generar análisis."
    lineas = analytics["lineas"].sort_values("brecha", ascending=False)
    prom = lineas["logro"].mean()
    crit = lineas[lineas["brecha"] >= 20]
    med = lineas[(lineas["brecha"] >= 10) & (lineas["brecha"] < 20)]
    top = lineas.iloc[0]
    txt = []
    txt.append(f"### Análisis ejecutivo del Perfil de Egreso · {carrera}\n")
    txt.append(f"El logro global estimado del perfil de egreso alcanza **{prom:.1f}%**, calculado a partir de las evaluaciones cargadas y su tributación a líneas formativas y competencias. ")
    if not crit.empty:
        txt.append(f"Se identifican **{len(crit)} brechas críticas** superiores a 20 puntos respecto de la meta institucional. La principal debilidad corresponde a **{top['linea']}**, con una brecha de **{top['brecha']:.1f} puntos**.")
    elif not med.empty:
        txt.append(f"No se observan brechas críticas, pero existen **{len(med)} brechas medias** que requieren seguimiento sistemático. La mayor brecha corresponde a **{top['linea']}**.")
    else:
        txt.append("El perfil presenta un desarrollo equilibrado, sin brechas medias o críticas respecto de la meta configurada.")
    txt.append("\n### Recomendaciones de aseguramiento de la calidad\n")
    for _, r in lineas.head(4).iterrows():
        if r.brecha >= 20:
            rec = "implementar un plan de mejora inmediato con talleres aplicados, reforzamiento metodológico, revisión de instrumentos y seguimiento en el siguiente corte."
        elif r.brecha >= 10:
            rec = "aplicar acciones focalizadas de refuerzo, tutorías y evaluación formativa para cerrar la brecha."
        else:
            rec = "mantener seguimiento, retroalimentación y monitoreo de evidencia para sostener el logro."
        txt.append(f"- **{r['linea']}**: logro {r['logro']:.1f}%, meta {r['meta']:.0f}%, brecha {r['brecha']:.1f}. Se recomienda {rec}")
    txt.append("\n### Uso para gestión curricular\nEste análisis permite pasar de una lectura centrada solo en notas a una lectura de contribución curricular real al perfil de egreso, generando evidencia para comités curriculares, planes de mejora, autoevaluación y acreditación.")
    return "\n".join(txt)

def openai_analysis(analytics: Dict[str, pd.DataFrame], carrera: str) -> str:
    api_key = st.secrets.get("OPENAI_API_KEY", None) if hasattr(st, "secrets") else None
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return rules_based_analysis(analytics, carrera)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        lineas = analytics["lineas"].to_dict(orient="records")
        asignaturas = analytics["asignaturas"].head(10).to_dict(orient="records")
        prompt = f"""
        Actúa como experto en aseguramiento de la calidad universitaria y perfil de egreso.
        Carrera: {carrera}
        Datos agregados por línea formativa: {lineas}
        Alertas por asignatura: {asignaturas}
        Genera un análisis ejecutivo en español con: diagnóstico, brechas, causas probables, acciones de mejora, indicadores de seguimiento y texto útil para informe de autoevaluación. No inventes datos personales.
        """
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":"Eres un analista experto en educación superior, perfil de egreso, Assurance of Learning y mejora continua."},{"role":"user","content":prompt}],
            temperature=0.25,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return rules_based_analysis(analytics, carrera) + f"\n\n> Nota: no se pudo conectar con OpenAI; se generó análisis local. Detalle técnico: {e}"

# -----------------------------
# Exportaciones
# -----------------------------
def export_excel(analytics: Dict[str, pd.DataFrame]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for name, df in analytics.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                safe = name[:31]
                df.to_excel(writer, sheet_name=safe, index=False)
    return output.getvalue()

# -----------------------------
# Sidebar / Estado
# -----------------------------
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin:18px 0 18px;">
      <div class="logo-box" style="width:54px;height:54px;border-radius:16px;font-size:19px;">360</div>
      <div><div style="font-weight:900;font-size:1.15rem;">PerfilEgreso</div><div style="font-size:.78rem;color:#DDEBFF!important;">USEK · IDAF</div></div>
    </div>
    """, unsafe_allow_html=True)
    section = st.radio(
        "Navegación",
        ["Inicio", "Captura de datos", "Configuración", "Análisis y diagnóstico", "Recomendaciones IA", "Reportes"],
        index=0,
    )
    st.markdown("---")
    uploaded = st.file_uploader("Subir Excel institucional", type=["xlsx", "xls"])
    use_demo = st.toggle("Usar datos de ejemplo", value=True if uploaded is None else False)
    st.download_button("Descargar plantilla modelo", data=create_template(), file_name="plantilla_perfilegreso360.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("---")
    meta_goal = st.slider("Meta institucional de logro (%)", 50, 100, 85)
    st.caption("La app lee la plantilla PerfilEgreso 360 o actas institucionales tipo USEK con columnas NF/%A.")

# Carga de datos
load_error = None
if uploaded is not None:
    try:
        data = read_workbook(uploaded)
    except Exception as e:
        load_error = str(e)
        data = demo_data()
elif use_demo:
    data = demo_data()
else:
    data = {"students": pd.DataFrame(), "evals": pd.DataFrame(), "lineas_cfg": pd.DataFrame(), "recs": default_recommendations(), "meta": pd.DataFrame()}

analytics = compute_analytics(data.get("evals", pd.DataFrame()), data.get("students", pd.DataFrame()), float(meta_goal)) if not data.get("evals", pd.DataFrame()).empty else {}

carrera = "Carrera no cargada"
if not data.get("students", pd.DataFrame()).empty and "carrera" in data["students"].columns:
    carrera = str(data["students"]["carrera"].dropna().iloc[0]) if not data["students"]["carrera"].dropna().empty else carrera

# -----------------------------
# Header principal
# -----------------------------
st.markdown(f"""
<div class="brand-wrap">
  <div class="brand-row">
    <div class="brand-left">
      <div class="logo-box">360</div>
      <div class="brand-title">PerfilEgreso 360</div>
      <div class="brand-sub">Plataforma ejecutiva para visualizar, diagnosticar, recomendar y evidenciar el logro del Perfil de Egreso en carreras universitarias.</div>
      <div class="chip-row">
        <div class="chip">⚠️ Alerta temprana</div>
        <div class="chip">📊 Competencias</div>
        <div class="chip">▣ Líneas formativas</div>
        <div class="chip">🎯 Brechas</div>
        <div class="chip">🤖 Análisis IA</div>
        <div class="chip">📄 Reportes</div>
      </div>
    </div>
    <div class="hero-people"><img src="data:image/svg+xml;base64,{people_svg()}" style="width:100%;height:auto;border-radius:24px;"/></div>
  </div>
</div>
""", unsafe_allow_html=True)

if load_error:
    st.error(f"No se pudo leer el archivo cargado: {load_error}")

# -----------------------------
# Páginas
# -----------------------------
def show_kpis():
    if not analytics:
        return
    lineas = analytics["lineas"]
    indiv = analytics["individual"]
    asignaturas = analytics["asignaturas"]
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        ("Logro global", f"{lineas['logro'].mean():.1f}%", "Promedio de líneas formativas"),
        ("Estudiantes", f"{len(indiv)}", "Con evaluaciones procesadas"),
        ("Alertas tempranas", f"{int(asignaturas['alertas'].sum())}", "Notas menores a 4.0"),
        ("Brechas críticas", f"{int((lineas['brecha']>=20).sum())}", "Líneas con brecha ≥ 20 pts"),
    ]
    for col, (lab, val, help_) in zip([c1,c2,c3,c4], kpis):
        with col:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>{lab}</div><div class='metric-value'>{val}</div><div class='metric-help'>{help_}</div></div>", unsafe_allow_html=True)

def show_methodology():
    st.markdown("""
    <div class="explain">
    <b>¿Cómo funciona?</b><br>
    1) El sistema lee notas finales, asistencia y asignaturas desde el Excel institucional. <br>
    2) Cada asignatura se asocia a una línea formativa y competencia del Perfil de Egreso. <br>
    3) Las notas se transforman a porcentaje de logro. <br>
    4) Se compara el logro contra la meta institucional configurada. <br>
    5) La brecha resultante activa alertas, recomendaciones y reportes de aseguramiento de la calidad.
    </div>
    """, unsafe_allow_html=True)

if section == "Inicio":
    st.markdown("<div class='section-title'>Inicio · Gobierno académico del Perfil de Egreso</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-subtitle'>Vista ejecutiva de {carrera}. Monitorea logro, brechas, riesgo académico y acciones de mejora.</div>", unsafe_allow_html=True)
    show_methodology()
    if analytics:
        show_kpis()
        st.write("")
        left, right = st.columns([1.15, .85])
        with left:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.plotly_chart(fig_radar(analytics["lineas"]), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.plotly_chart(fig_brechas(analytics["lineas"]), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Sube un Excel institucional o activa los datos de ejemplo para iniciar.")

elif section == "Captura de datos":
    st.markdown("<div class='section-title'>1. Captura de datos</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Carga archivos Excel institucionales sin transformar manualmente los datos. La app reconoce plantilla PerfilEgreso 360 y actas USEK con NF/%A.</div>", unsafe_allow_html=True)
    show_methodology()
    c1, c2 = st.columns([.8, 1.2])
    with c1:
        st.markdown("<div class='card'><h3>Estado de carga</h3>", unsafe_allow_html=True)
        if uploaded:
            st.success(f"Archivo cargado: {uploaded.name}")
        elif use_demo:
            st.warning("Usando datos de ejemplo.")
        else:
            st.info("Sin archivo cargado.")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        if not data.get("evals", pd.DataFrame()).empty:
            st.markdown("<div class='card'><h3>Vista previa de evaluaciones procesadas</h3>", unsafe_allow_html=True)
            st.dataframe(data["evals"].head(20), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    if not data.get("students", pd.DataFrame()).empty:
        st.markdown("<div class='card'><h3>Estudiantes detectados</h3>", unsafe_allow_html=True)
        st.dataframe(data["students"].head(30), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif section == "Configuración":
    st.markdown("<div class='section-title'>2. Configuración del modelo</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Parametriza la meta, líneas formativas, competencias y reglas de brecha.</div>", unsafe_allow_html=True)
    show_methodology()
    if analytics:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='card'><h3>Líneas formativas detectadas</h3>", unsafe_allow_html=True)
            cfg = analytics["lineas"][["linea", "meta", "evaluaciones", "estudiantes"]].copy()
            st.dataframe(cfg, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='card'><h3>Competencias detectadas</h3>", unsafe_allow_html=True)
            st.dataframe(analytics["competencias"][["competencia", "meta", "evaluaciones"]], use_container_width=True, height=420)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Carga datos para visualizar la configuración detectada.")

elif section == "Análisis y diagnóstico":
    st.markdown("<div class='section-title'>3. Análisis y diagnóstico</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Identificación de brechas por cohorte, línea formativa, competencia, asignatura y estudiante.</div>", unsafe_allow_html=True)
    if analytics:
        show_kpis()
        tab1, tab2, tab3, tab4 = st.tabs(["Radar", "Brechas", "Asignaturas críticas", "Estudiantes"])
        with tab1:
            st.plotly_chart(fig_radar(analytics["lineas"], "Radar de logro por líneas formativas"), use_container_width=True)
        with tab2:
            st.plotly_chart(fig_brechas(analytics["lineas"]), use_container_width=True)
            display = analytics["lineas"].copy()
            display["criticidad"] = display["criticidad"].astype(str)
            st.dataframe(display.sort_values("brecha", ascending=False), use_container_width=True)
        with tab3:
            st.plotly_chart(fig_alertas(analytics["asignaturas"]), use_container_width=True)
            st.dataframe(analytics["asignaturas"], use_container_width=True)
        with tab4:
            st.dataframe(analytics["individual"].sort_values("logro"), use_container_width=True)
    else:
        st.info("Carga datos para iniciar el análisis.")

elif section == "Recomendaciones IA":
    st.markdown("<div class='section-title'>4. Recomendaciones y análisis IA</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Genera interpretación ejecutiva, acciones de mejora y texto útil para informes de aseguramiento de la calidad.</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-box'><b>Privacidad:</b> el análisis IA trabaja preferentemente con datos agregados: carrera, cohorte, líneas, competencias, metas, logros y brechas. Evita enviar RUT o información personal salvo que sea estrictamente necesario.</div>", unsafe_allow_html=True)
    if analytics:
        c1, c2 = st.columns([.9,1.1])
        with c1:
            st.markdown("<div class='card'><h3>Debilidades priorizadas</h3>", unsafe_allow_html=True)
            for _, r in analytics["lineas"].sort_values("brecha", ascending=False).iterrows():
                st.markdown(f"**{r['linea']}** · logro {r['logro']:.1f}% · brecha {r['brecha']:.1f} pts · {severity_badge(r['criticidad'])}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            if st.button("🤖 Generar análisis automático", type="primary"):
                st.session_state["ai_text"] = openai_analysis(analytics, carrera)
            ai_text = st.session_state.get("ai_text", rules_based_analysis(analytics, carrera))
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(ai_text)
            st.markdown("</div>", unsafe_allow_html=True)
            st.download_button("Descargar análisis en TXT", data=ai_text.encode("utf-8"), file_name="analisis_ia_perfilegreso360.txt", mime="text/plain")
    else:
        st.info("Carga datos para generar recomendaciones.")

elif section == "Reportes":
    st.markdown("<div class='section-title'>5. Reportes ejecutivos</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Reportes internos alineados a aseguramiento de la calidad: alerta temprana, competencias, líneas formativas, total líneas y total competencias.</div>", unsafe_allow_html=True)
    if analytics:
        report = st.selectbox("Selecciona reporte", [
            "Reporte 1 · Alerta temprana",
            "Reporte 2 · Tributación a competencias",
            "Reporte 3 · Tributación a líneas formativas",
            "Reporte 4 · Índice total de líneas formativas",
            "Reporte 5 · Índice total de competencias",
            "Exportación general",
        ])
        if report.startswith("Reporte 1"):
            st.markdown("<div class='dark-panel'><h3>Reporte 1 · Sistema de Alerta Temprana</h3><p>Detecta estudiantes y asignaturas con notas menores a 4.0 para activar intervenciones oportunas.</p></div>", unsafe_allow_html=True)
            st.plotly_chart(fig_alertas(analytics["asignaturas"]), use_container_width=True)
            st.dataframe(analytics["individual"].sort_values("alertas", ascending=False), use_container_width=True)
        elif report.startswith("Reporte 2"):
            st.markdown("<div class='dark-panel'><h3>Reporte 2 · Tributación a Competencias</h3><p>Visualiza el avance de competencias clave del perfil de egreso.</p></div>", unsafe_allow_html=True)
            st.plotly_chart(fig_horizontal(analytics["competencias"], "competencia", "logro", "Logro por competencia"), use_container_width=True)
        elif report.startswith("Reporte 3"):
            st.markdown("<div class='dark-panel'><h3>Reporte 3 · Tributación a Líneas Formativas</h3><p>Mide el avance de agrupaciones curriculares con propósitos compartidos.</p></div>", unsafe_allow_html=True)
            st.plotly_chart(fig_horizontal(analytics["lineas"], "linea", "logro", "Logro por línea formativa"), use_container_width=True)
        elif report.startswith("Reporte 4"):
            st.markdown("<div class='dark-panel'><h3>Reporte 4 · Índice Total de Líneas Formativas</h3><p>Entrega lectura global del desarrollo del estudiante/cohorte en cada dominio formativo.</p></div>", unsafe_allow_html=True)
            st.plotly_chart(fig_radar(analytics["lineas"], "Índice total de líneas formativas"), use_container_width=True)
            st.dataframe(analytics["lineas"].sort_values("logro", ascending=False), use_container_width=True)
        elif report.startswith("Reporte 5"):
            st.markdown("<div class='dark-panel'><h3>Reporte 5 · Índice Total de Competencias</h3><p>Permite evidenciar la coherencia curricular y el logro del perfil de egreso.</p></div>", unsafe_allow_html=True)
            st.plotly_chart(fig_horizontal(analytics["competencias"], "competencia", "logro", "Índice total de competencias"), use_container_width=True)
            st.markdown(rules_based_analysis(analytics, carrera))
        else:
            st.markdown("<div class='card'><h3>Exportación general</h3><p>Descarga resultados procesados para gestión interna, comités curriculares o acreditación.</p></div>", unsafe_allow_html=True)
        st.download_button("Descargar resultados en Excel", data=export_excel(analytics), file_name=f"perfilegreso360_resultados_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("Carga datos para generar reportes.")

st.markdown(f"<div class='footer'>© {datetime.now().year} PerfilEgreso 360 · {BRAND['institution']} · Prototipo MVP para análisis curricular y aseguramiento de la calidad.</div>", unsafe_allow_html=True)
