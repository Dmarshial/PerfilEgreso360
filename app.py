import io
import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='PerfilEgreso 360', page_icon='🎓', layout='wide', initial_sidebar_state='expanded')

PRIMARY = '#0B1F3A'
SECONDARY = '#123B6D'
ACCENT = '#16C2D5'
MAGENTA = '#D83F87'
GOLD = '#F5B82E'
GREEN = '#24C08B'
RED = '#EF4444'
BG = '#F6F8FC'
CARD = '#FFFFFF'
TEXT = '#172033'
MUTED = '#687387'

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*='css'] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: {BG}; color: {TEXT}; }}
.block-container {{ padding-top: 0.8rem; max-width: 1320px; }}
[data-testid='stSidebar'] {{ background: linear-gradient(180deg, {PRIMARY} 0%, #081527 100%); }}
[data-testid='stSidebar'] * {{ color: #fff !important; }}
[data-testid='stSidebar'] .stButton button {{
    background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.16); color: white; border-radius: 14px;
    height: 46px; font-weight: 700; width: 100%; justify-content: flex-start;
}}
[data-testid='stSidebar'] .stButton button:hover {{ background: rgba(22,194,213,.18); border-color: {ACCENT}; }}
.hero {{
    background: radial-gradient(circle at 10% 10%, rgba(216,63,135,.22), transparent 28%),
                radial-gradient(circle at 90% 0%, rgba(22,194,213,.26), transparent 30%),
                linear-gradient(135deg, {PRIMARY} 0%, {SECONDARY} 54%, #081527 100%);
    border-radius: 28px; padding: 34px 40px; color: white; box-shadow: 0 24px 70px rgba(11,31,58,.25); margin-bottom: 24px;
}}
.brand-row {{ display:flex; align-items:center; gap:18px; }}
.logo-mark {{
    width:76px; height:76px; border-radius:22px; background: conic-gradient(from 140deg, {MAGENTA}, #7C3AED, #2F80ED, {ACCENT}, {MAGENTA});
    display:flex; align-items:center; justify-content:center; font-size:34px; font-weight:900; box-shadow: 0 12px 30px rgba(0,0,0,.20);
}}
.hero h1 {{ font-size: 52px; line-height: 1; margin: 0; letter-spacing: -1.8px; }}
.hero p {{ font-size: 17px; color: rgba(255,255,255,.84); margin-top: 12px; max-width: 900px; }}
.pillbar {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:22px; }}
.pill {{ padding: 12px 16px; border-radius: 999px; background: rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.18); font-weight:700; }}
.pill.active {{ background:white; color:{PRIMARY}; }}
.card {{ background:{CARD}; border:1px solid #E7ECF4; border-radius: 22px; padding: 22px; box-shadow: 0 14px 38px rgba(15,23,42,.06); }}
.dark-card {{ background: linear-gradient(180deg, #0E2748 0%, #071A31 100%); border:1px solid rgba(255,255,255,.10); border-radius:24px; padding:24px; color:white; box-shadow: 0 16px 50px rgba(11,31,58,.23); }}
.kpi {{ background:white; border:1px solid #E7ECF4; border-radius: 20px; padding:18px; box-shadow: 0 10px 30px rgba(15,23,42,.05); }}
.kpi-label {{ color:{MUTED}; font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:.04em; }}
.kpi-value {{ color:{PRIMARY}; font-size:32px; font-weight:900; margin-top:6px; }}
.kpi-sub {{ color:{MUTED}; font-size:13px; margin-top:2px; }}
.section-title {{ font-size: 30px; font-weight: 900; color:{PRIMARY}; letter-spacing:-.8px; margin: 10px 0 6px; }}
.section-sub {{ color:{MUTED}; font-size: 15px; margin-bottom: 18px; }}
.nav-caption {{ color: rgba(255,255,255,.55) !important; text-transform:uppercase; font-size:12px; letter-spacing:.08em; font-weight:800; margin: 16px 0 8px; }}
.badge {{ display:inline-block; padding:6px 10px; border-radius:999px; font-size:12px; font-weight:800; }}
.badge-red {{ background:#FEE2E2; color:#991B1B; }}
.badge-yellow {{ background:#FEF3C7; color:#92400E; }}
.badge-green {{ background:#DCFCE7; color:#166534; }}
.footer {{ color:#95A0B5; text-align:center; padding:25px 0; }}
.stTabs [data-baseweb='tab-list'] {{ gap: 12px; }}
.stTabs [data-baseweb='tab'] {{ background: white; border-radius: 999px; padding: 12px 18px; border:1px solid #E7ECF4; }}
.stTabs [aria-selected='true'] {{ background: {PRIMARY}; color: white; }}
</style>
""", unsafe_allow_html=True)

REQUIRED_SHEETS = ['Estudiantes','Evaluaciones','Config_Lineas','Config_RA','Ponderaciones','Recomendaciones']

def sample_data():
    estudiantes = pd.DataFrame({
        'student_id':[1,2,3,4,5,6,7,8,9,10],
        'rut':['11.111.111-1','22.222.222-2','33.333.333-3','44.444.444-4','55.555.555-5','66.666.666-6','77.777.777-7','88.888.888-8','99.999.999-9','10.101.010-0'],
        'nombre':['Juan Pérez','Camila Rojas','Matías Silva','Fernanda Morales','Diego Vargas','Valentina Soto','Benjamín Castro','Antonia Núñez','Sebastián Lagos','Martina Fuentes'],
        'cohorte':['2024','2024','2024','2025','2025','2025','2026','2026','2026','2026'],
        'carrera':['Ciencias de la Actividad Física y del Deporte']*10,
        'sede':['Santiago','Santiago','Santiago','Santiago','Valparaíso','Valparaíso','Santiago','Santiago','Valparaíso','Santiago'],
        'ciclo':['Inicial','Intermedio','Avanzado','Inicial','Intermedio','Avanzado','Inicial','Intermedio','Avanzado','Inicial']
    })
    lineas = pd.DataFrame({
        'linea_id':['L1','L2','L3','L4','L5','L6','L7'],
        'linea':['Fundamentos de la Actividad Física','Evaluación Funcional','Prescripción del Ejercicio','Intervención en Contextos Reales','Investigación Aplicada','Gestión Deportiva','Comunicación y Liderazgo'],
        'meta':[85,85,85,85,85,85,85]
    })
    ra = pd.DataFrame({
        'ra_id':['RA1','RA2','RA3','RA4','RA5','RA6','RA7'],
        'resultado_aprendizaje':['Comprende bases morfofuncionales','Evalúa condición física','Diseña programas de ejercicio','Interviene en contextos reales','Analiza evidencia científica','Gestiona procesos deportivos','Comunica y lidera equipos'],
        'linea_id':['L1','L2','L3','L4','L5','L6','L7']
    })
    rng = np.random.default_rng(7)
    rows=[]
    tipos=['Prueba','Práctica','Interciclo','Nacional']
    for sid in estudiantes.student_id:
        for r in ra.ra_id:
            for tipo in tipos:
                base = rng.normal(5.1, .65)
                if r in ['RA2','RA3']:
                    base -= .55
                nota = float(np.clip(base, 2.5, 7.0))
                rows.append([sid, f'Asignatura {r}', r, tipo, round(nota,1)])
    evaluaciones = pd.DataFrame(rows, columns=['student_id','asignatura','ra_id','tipo_evaluacion','nota'])
    ponderaciones = pd.DataFrame({'tipo_evaluacion':['Prueba','Práctica','Interciclo','Nacional'], 'peso':[35,35,20,10]})
    recomendaciones = pd.DataFrame({
        'linea':['Fundamentos de la Actividad Física','Evaluación Funcional','Prescripción del Ejercicio','Intervención en Contextos Reales','Investigación Aplicada','Gestión Deportiva','Comunicación y Liderazgo'],
        'brecha_min':[0,0,0,0,0,0,0], 'brecha_max':[100,100,100,100,100,100,100],
        'recomendacion':['Refuerzo conceptual con cápsulas y evaluación formativa.','Taller práctico de aplicación de test y análisis de resultados.','Casos integrados de prescripción por nivel de riesgo y objetivo.','Simulación de intervención en contextos escolares, comunitarios y deportivos.','Tutoría de lectura científica, análisis de datos y escritura académica.','Proyecto aplicado de planificación, gestión y evaluación deportiva.','Laboratorio de comunicación, liderazgo y retroalimentación efectiva.'],
        'evidencia':['Plan remedial y actas de seguimiento','Lista de asistencia, rúbrica y resultados pre/post','Banco de casos, rúbricas y comparación de logro','Registro de simulaciones y pauta de desempeño','Informe breve, rúbrica y base de datos','Carta Gantt, KPI y reporte de implementación','Pauta de observación y videoevidencia']
    })
    return {'Estudiantes':estudiantes,'Evaluaciones':evaluaciones,'Config_Lineas':lineas,'Config_RA':ra,'Ponderaciones':ponderaciones,'Recomendaciones':recomendaciones}

def normalize(data):
    out = {}
    for k,v in data.items():
        df = v.copy()
        df.columns = [str(c).strip().lower().replace(' ', '_').replace('id_estudiante','student_id').replace('id_ra','ra_id').replace('id_linea','linea_id').replace('nombre_linea','linea').replace('tipo_evaluacion','tipo_evaluacion').replace('nota_1a7','nota') for c in df.columns]
        out[k] = df
    return out

def read_excel(file):
    raw = pd.read_excel(file, sheet_name=None)
    # keep exact sheet names expected if present; otherwise normalize common names
    mapping = {s.lower().strip():s for s in raw.keys()}
    data = {}
    for sheet in REQUIRED_SHEETS:
        key = sheet.lower()
        if key in mapping:
            data[sheet] = raw[mapping[key]]
        else:
            data[sheet] = pd.DataFrame()
    return normalize(data)

def build_model(data):
    students = data['Estudiantes'].copy()
    evals = data['Evaluaciones'].copy()
    lineas = data['Config_Lineas'].copy()
    ra = data['Config_RA'].copy()
    pond = data['Ponderaciones'].copy()
    recs = data['Recomendaciones'].copy()
    for df in [students, evals, lineas, ra, pond, recs]:
        df.columns = [c.lower() for c in df.columns]
    evals['nota'] = pd.to_numeric(evals['nota'], errors='coerce')
    evals['logro_pct'] = ((evals['nota'] - 1) / 6 * 100).clip(0,100)
    if 'tipo_evaluacion' in evals and 'tipo_evaluacion' in pond.columns:
        pond['peso'] = pd.to_numeric(pond['peso'], errors='coerce')
        evals = evals.merge(pond[['tipo_evaluacion','peso']], on='tipo_evaluacion', how='left')
        evals['peso'] = evals['peso'].fillna(100)
    else:
        evals['peso'] = 100
    evals = evals.merge(ra[['ra_id','resultado_aprendizaje','linea_id']], on='ra_id', how='left')
    evals = evals.merge(lineas[['linea_id','linea','meta']], on='linea_id', how='left')
    evals = evals.merge(students[['student_id','nombre','cohorte','carrera','sede','ciclo']], on='student_id', how='left')
    grouped = evals.groupby(['student_id','nombre','cohorte','carrera','sede','ciclo','linea','meta'], dropna=False).apply(lambda x: np.average(x['logro_pct'], weights=x['peso'])).reset_index(name='logro')
    grouped['brecha'] = grouped['meta'] - grouped['logro']
    grouped['criticidad'] = pd.cut(grouped['brecha'], bins=[-999,0,10,20,999], labels=['Sin brecha','Baja','Media','Alta'])
    cohort = grouped.groupby(['cohorte','linea','meta'], dropna=False)['logro'].mean().reset_index()
    cohort['brecha'] = cohort['meta'] - cohort['logro']
    return students, evals, grouped, cohort, lineas, recs

def template_bytes():
    data = sample_data()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for name, df in data.items():
            df.to_excel(writer, sheet_name=name, index=False)
    return output.getvalue()

def export_bytes(grouped, cohort):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        grouped.to_excel(writer, sheet_name='Reporte_Individual', index=False)
        cohort.to_excel(writer, sheet_name='Reporte_Cohorte', index=False)
    return output.getvalue()

def radar(df, title, value_col='logro'):
    d = df.sort_values('linea')
    cats = d['linea'].tolist()
    values = d[value_col].round(1).tolist()
    meta = d['meta'].round(1).tolist() if 'meta' in d else [85]*len(values)
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=meta+[meta[0]], theta=cats+[cats[0]], fill='toself', name='Meta esperada', line=dict(color=GREEN, width=3), fillcolor='rgba(36,192,139,.14)'))
    fig.add_trace(go.Scatterpolar(r=values+[values[0]], theta=cats+[cats[0]], fill='toself', name='Logro actual', line=dict(color=ACCENT, width=3), fillcolor='rgba(22,194,213,.28)'))
    fig.update_layout(template='plotly_dark', height=520, title=title, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', polar=dict(bgcolor='rgba(9,25,45,0)', radialaxis=dict(range=[0,100], tickfont=dict(color='white'), gridcolor='rgba(255,255,255,.18)'), angularaxis=dict(tickfont=dict(color='white', size=11), gridcolor='rgba(255,255,255,.12)')), legend=dict(orientation='h', y=-.1))
    return fig

def bar_brechas(df, title):
    d = df.sort_values('brecha', ascending=True).copy()
    d['brecha_pos'] = d['brecha'].clip(lower=0)
    fig = px.bar(d, x='brecha_pos', y='linea', orientation='h', title=title, text=d['brecha_pos'].round(1).astype(str)+'%')
    fig.update_traces(marker_color=RED, textposition='outside')
    fig.update_layout(height=420, template='plotly_white', xaxis_title='Brecha respecto de la meta', yaxis_title='', margin=dict(l=10,r=30,t=60,b=10))
    return fig

def progress_bars(df, title):
    d = df.sort_values('logro')
    fig = px.bar(d, x='logro', y='linea', orientation='h', color='logro', range_x=[0,100], color_continuous_scale=['#EF4444','#F5B82E','#24C08B'], title=title, text=d['logro'].round(1).astype(str)+'%')
    fig.update_layout(height=470, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(11,31,58,0.95)', xaxis_title='Logro (%)', yaxis_title='', coloraxis_showscale=False)
    return fig

def render_nav():
    st.sidebar.markdown("<div style='height:8px'></div><div class='brand-row'><div class='logo-mark' style='width:52px;height:52px;border-radius:16px;font-size:24px'>360</div><div><div style='font-size:22px;font-weight:900'>PerfilEgreso</div><div style='font-size:12px;color:rgba(255,255,255,.55)!important'>USEK · IDAF</div></div></div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='nav-caption'>Navegación</div>", unsafe_allow_html=True)
    options = ['Inicio','Reporte 1 · Alerta temprana','Reporte 2 · Competencias','Reporte 3 · Líneas formativas','Reporte 4 · Total líneas','Reporte 5 · Total competencias','Configuración','Reportes']
    choice = st.sidebar.radio('', options, label_visibility='collapsed')
    st.sidebar.markdown("<div class='nav-caption'>Carga institucional</div>", unsafe_allow_html=True)
    uploaded = st.sidebar.file_uploader('Subir Excel institucional', type=['xlsx'])
    use_demo = st.sidebar.toggle('Usar datos de ejemplo', value=True)
    st.sidebar.download_button('Descargar plantilla modelo', data=template_bytes(), file_name='plantilla_perfilegreso360.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return choice, uploaded, use_demo

def render_hero():
    st.markdown(f"""
    <div class='hero'>
      <div class='brand-row'>
        <div class='logo-mark'>360</div>
        <div>
          <h1>PerfilEgreso 360</h1>
          <p>Plataforma de visualización, diagnóstico y aseguramiento del logro del Perfil de Egreso para carreras universitarias.</p>
        </div>
      </div>
      <div class='pillbar'>
        <span class='pill active'>⚠ Alerta temprana</span><span class='pill'>📊 Competencias</span><span class='pill'>▣ Líneas formativas</span><span class='pill'>🎯 Brechas</span><span class='pill'>📄 Reportes</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

def load_or_demo(uploaded, use_demo):
    if uploaded is not None:
        return read_excel(uploaded)
    if use_demo:
        return normalize(sample_data())
    return None

choice, uploaded, use_demo = render_nav()
data = load_or_demo(uploaded, use_demo)
render_hero()

if data is None:
    st.markdown("<div class='card'><h2>Sube la plantilla institucional o activa datos de ejemplo</h2><p>El sistema requiere las hojas: Estudiantes, Evaluaciones, Config_Lineas, Config_RA, Ponderaciones y Recomendaciones.</p></div>", unsafe_allow_html=True)
    st.stop()

try:
    students, evals, grouped, cohort, lineas, recs = build_model(data)
except Exception as e:
    st.error('No fue posible procesar el Excel. Revisa que tenga las hojas y columnas requeridas.')
    st.exception(e)
    st.stop()

cohortes = sorted([str(x) for x in grouped['cohorte'].dropna().unique()])
cohorte_sel = st.sidebar.selectbox('Cohorte', cohortes, index=len(cohortes)-1 if cohortes else 0)
student_names = grouped[grouped['cohorte'].astype(str)==cohorte_sel]['nombre'].dropna().unique().tolist()
student_sel = st.sidebar.selectbox('Estudiante', student_names) if student_names else None
cohort_df = cohort[cohort['cohorte'].astype(str)==cohorte_sel]
student_df = grouped[(grouped['cohorte'].astype(str)==cohorte_sel) & (grouped['nombre']==student_sel)] if student_sel else grouped.head(0)

avg = float(cohort_df['logro'].mean()) if len(cohort_df) else 0
brechas_altas = int((cohort_df['brecha']>20).sum()) if len(cohort_df) else 0
alertas = int((evals['nota'] < 4.0).sum()) if len(evals) else 0
est_count = int(grouped[grouped['cohorte'].astype(str)==cohorte_sel]['student_id'].nunique())

if choice == 'Inicio':
    st.markdown("<div class='section-title'>Inicio · Gobierno académico del Perfil de Egreso</div><div class='section-sub'>Vista ejecutiva para monitorear logro, brechas, riesgo académico y acciones de mejora.</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for col, label, value, sub in [(c1,'Logro global',f'{avg:.1f}%','Promedio de cohorte'),(c2,'Estudiantes',est_count,'Evaluados en la cohorte'),(c3,'Alertas tempranas',alertas,'Notas menores a 4.0'),(c4,'Brechas críticas',brechas_altas,'Sobre 20 puntos')]:
        col.markdown(f"<div class='kpi'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div><div class='kpi-sub'>{sub}</div></div>", unsafe_allow_html=True)
    st.write('')
    a,b = st.columns([1.1,1])
    with a:
        st.markdown("<div class='dark-card'>", unsafe_allow_html=True)
        st.plotly_chart(radar(cohort_df, 'Radar de logro por líneas formativas'), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with b:
        st.markdown("<div class='card'><h3>Debilidades prioritarias</h3></div>", unsafe_allow_html=True)
        st.plotly_chart(bar_brechas(cohort_df, 'Brechas por línea formativa'), use_container_width=True)

elif choice.startswith('Reporte 1'):
    st.markdown("<div class='section-title'>Reporte 1 · Sistema de Alerta Temprana</div><div class='section-sub'>Detección inmediata de estudiantes con calificación menor a 4.0 por asignatura y cohorte.</div>", unsafe_allow_html=True)
    low = evals[(evals['cohorte'].astype(str)==cohorte_sel) & (evals['nota']<4.0)].copy()
    c1,c2,c3 = st.columns(3)
    c1.markdown(f"<div class='kpi'><div class='kpi-label'>Total alertas</div><div class='kpi-value'>{len(low)}</div><div class='kpi-sub'>Evaluaciones bajo 4.0</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi'><div class='kpi-label'>Estudiantes en riesgo</div><div class='kpi-value'>{low['student_id'].nunique()}</div><div class='kpi-sub'>Con al menos una alerta</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='kpi'><div class='kpi-label'>Asignaturas críticas</div><div class='kpi-value'>{low['asignatura'].nunique()}</div><div class='kpi-sub'>Con notas menores a 4.0</div></div>", unsafe_allow_html=True)
    if len(low):
        counts = low.groupby('asignatura')['student_id'].nunique().reset_index(name='estudiantes')
        fig = px.bar(counts.sort_values('estudiantes'), x='estudiantes', y='asignatura', orientation='h', text='estudiantes', title='Número de estudiantes con calificación < 4.0 por asignatura')
        fig.update_traces(marker_color=RED)
        fig.update_layout(height=480, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(11,31,58,0.95)')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(low[['nombre','cohorte','asignatura','resultado_aprendizaje','linea','tipo_evaluacion','nota']], use_container_width=True, hide_index=True)
    else:
        st.success('No se detectan calificaciones bajo 4.0 en la cohorte seleccionada.')

elif choice.startswith('Reporte 2'):
    st.markdown("<div class='section-title'>Reporte 2 · Tributación a Competencias</div><div class='section-sub'>Índice de progreso individual asociado a resultados de aprendizaje y competencias del perfil.</div>", unsafe_allow_html=True)
    comp = evals[(evals['cohorte'].astype(str)==cohorte_sel)&(evals['nombre']==student_sel)].groupby('resultado_aprendizaje')['logro_pct'].mean().reset_index(name='logro')
    fig = px.bar(comp.sort_values('logro'), x='logro', y='resultado_aprendizaje', orientation='h', range_x=[0,100], text=comp.sort_values('logro')['logro'].round(1).astype(str)+'%', title=f'Competencias / RA · {student_sel}')
    fig.update_traces(marker_color=ACCENT)
    fig.update_layout(height=520, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(11,31,58,0.95)', xaxis_title='Logro (%)', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(comp.sort_values('logro'), use_container_width=True, hide_index=True)

elif choice.startswith('Reporte 3'):
    st.markdown("<div class='section-title'>Reporte 3 · Tributación a Líneas Formativas</div><div class='section-sub'>Avance del estudiante en cada línea formativa del plan de estudios.</div>", unsafe_allow_html=True)
    a,b = st.columns([1,1])
    with a:
        st.markdown("<div class='dark-card'>", unsafe_allow_html=True)
        st.plotly_chart(radar(student_df, f'Perfil formativo · {student_sel}'), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with b:
        st.plotly_chart(progress_bars(student_df, 'Logro por línea formativa'), use_container_width=True)
    st.dataframe(student_df[['linea','logro','meta','brecha','criticidad']], use_container_width=True, hide_index=True)

elif choice.startswith('Reporte 4'):
    st.markdown("<div class='section-title'>Reporte 4 · Índice Total de Tributación a Líneas Formativas</div><div class='section-sub'>Lectura global de la trayectoria formativa del estudiante y su contribución al perfil de egreso.</div>", unsafe_allow_html=True)
    st.plotly_chart(progress_bars(student_df, f'Total líneas formativas · {student_sel}'), use_container_width=True)
    prom = student_df['logro'].mean()
    nivel = 'Desempeño Estratégico' if prom>=90 else 'Desempeño Integrado Alto' if prom>=80 else 'Desempeño en Desarrollo' if prom>=70 else 'Desempeño Insuficiente'
    st.markdown(f"<div class='card'><h2>Interpretación del Perfil de Egreso</h2><p>El estudiante presenta un promedio global aproximado de <b>{prom:.1f}%</b>. Según la escala institucional, corresponde a <b>{nivel}</b>.</p><p>La lectura permite evidenciar fortalezas, brechas y coherencia entre asignaturas, resultados de aprendizaje y líneas formativas.</p></div>", unsafe_allow_html=True)

elif choice.startswith('Reporte 5'):
    st.markdown("<div class='section-title'>Reporte 5 · Índice Total de Competencias del Perfil de Egreso</div><div class='section-sub'>Síntesis de logro del perfil profesional desde resultados de aprendizaje, competencias y trayectoria formativa.</div>", unsafe_allow_html=True)
    comp = evals[(evals['cohorte'].astype(str)==cohorte_sel)&(evals['nombre']==student_sel)].groupby(['resultado_aprendizaje','linea'])['logro_pct'].mean().reset_index(name='logro')
    fig = px.bar(comp.sort_values('logro'), x='logro', y='resultado_aprendizaje', color='linea', orientation='h', range_x=[0,100], title='Índice total de competencias')
    fig.update_layout(height=560, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(11,31,58,0.95)', xaxis_title='Logro (%)', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div class='card'><h3>Lectura desde Assurance of Learning</h3><p>Este reporte permite verificar el logro del perfil de egreso, analizar efectividad curricular, detectar brechas formativas y generar evidencia para acreditación.</p></div>", unsafe_allow_html=True)

elif choice == 'Configuración':
    st.markdown("<div class='section-title'>Configuración del modelo</div><div class='section-sub'>Revisión de líneas formativas, resultados de aprendizaje, ponderaciones y reglas de recomendación.</div>", unsafe_allow_html=True)
    tab1,tab2,tab3,tab4 = st.tabs(['Líneas','Resultados de aprendizaje','Ponderaciones','Recomendaciones'])
    with tab1: st.dataframe(data['Config_Lineas'], use_container_width=True, hide_index=True)
    with tab2: st.dataframe(data['Config_RA'], use_container_width=True, hide_index=True)
    with tab3: st.dataframe(data['Ponderaciones'], use_container_width=True, hide_index=True)
    with tab4: st.dataframe(data['Recomendaciones'], use_container_width=True, hide_index=True)

elif choice == 'Reportes':
    st.markdown("<div class='section-title'>Reportes y exportación</div><div class='section-sub'>Descarga de resultados para gestión académica, comité curricular y aseguramiento de la calidad.</div>", unsafe_allow_html=True)
    st.download_button('Descargar reporte Excel general', data=export_bytes(grouped, cohort), file_name='reporte_perfilegreso360.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    st.dataframe(grouped, use_container_width=True, hide_index=True)

st.markdown("<div class='footer'>PerfilEgreso 360 · USEK / IDAF · Sistema de visualización, diagnóstico y mejora continua del Perfil de Egreso</div>", unsafe_allow_html=True)
