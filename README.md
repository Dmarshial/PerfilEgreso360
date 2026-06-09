# PerfilEgreso 360 - MVP

Sistema inicial para visualizar el logro del Perfil de Egreso mediante carga de Excel, radar de desempeño, detección de brechas y recomendaciones de aseguramiento de la calidad.

## Archivos incluidos

- `app.py`: aplicación Streamlit.
- `plantilla_institucional_perfilegreso360.xlsx`: plantilla de carga de datos.
- `requirements.txt`: librerías necesarias.

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Flujo de uso

1. Completar la plantilla Excel institucional.
2. Ejecutar la aplicación.
3. Cargar la plantilla en el panel lateral.
4. Filtrar por cohorte, corte o estudiante.
5. Revisar radar, brechas y recomendaciones.
6. Exportar reporte Excel.

## Estructura de datos

La plantilla contiene seis hojas obligatorias:

1. `Estudiantes`: identificación, carrera, cohorte y ciclo.
2. `Evaluaciones`: notas, actividades, RA, línea formativa y logro porcentual.
3. `Config_Lineas`: líneas formativas y meta de logro.
4. `Config_RA`: resultados de aprendizaje asociados a líneas y asignaturas.
5. `Ponderaciones`: pesos de cada fuente de evidencia.
6. `Recomendaciones`: banco de acciones de mejora según brecha.

## Próximas mejoras sugeridas

- Exportación PDF con formato institucional.
- Login por roles: administrador, director de carrera, docente.
- Historial de cargas y auditoría.
- Base de datos PostgreSQL o Supabase.
- Dashboard por carrera, sede, facultad y cohorte.
- Motor de recomendaciones avanzado.
