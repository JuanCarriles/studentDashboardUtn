import streamlit as st
import pandas as pd
from deltalake import DeltaTable
import plotly.graph_objects as go
import os

# ──────────────────────────────────────────────
# Configuración de la página
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="📊 Dashboard de Alumnos",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Estilos CSS – forzar texto claro en TODO
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Forzar texto claro en TODA la app ── */
    .stApp, .stApp * {
        color: #e0e0f0 !important;
    }

    /* ── Fondo principal oscuro ── */
    .stApp {
        background: #0e0e1a !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12121a 0%, #1a1a2e 100%) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #c8c8e0 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #9090b0 !important;
        font-weight: 500 !important;
    }

    /* ── Tarjetas de métricas ── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    div[data-testid="stMetric"] label {
        color: #a0a0c0 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    /* Delta (el subtexto "X alumnos") */
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #90d0ff !important;
        font-size: 0.85rem !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] svg {
        display: none;
    }

    /* ── Tablas ── */
    .stDataFrame, .stDataFrame * {
        color: #d0d0e8 !important;
    }
    .stDataFrame thead th {
        background: #1e1e2e !important;
        color: #a0a0d0 !important;
        font-weight: 600 !important;
    }
    .stDataFrame tbody td {
        background: #14141e !important;
        color: #c8c8e0 !important;
    }

    /* ── Captions y textos secundarios ── */
    .stCaption, [data-testid="stCaption"], small {
        color: #8888aa !important;
    }

    /* ── Títulos y subtítulos ── */
    h1, h2, h3, h4, h5, h6 {
        color: #e8e8ff !important;
    }

    /* ── Dividers ── */
    hr {
        border-color: rgba(255,255,255,0.08) !important;
    }

    /* ── Botones ── */
    .stDownloadButton button {
        background: linear-gradient(135deg, #6C63FF, #48c6ef) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: opacity 0.2s !important;
    }
    .stDownloadButton button:hover {
        opacity: 0.85 !important;
    }

    /* ── Header personalizado ── */
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .main-header h1 {
        background: linear-gradient(90deg, #6C63FF, #48c6ef);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .main-header p {
        color: #8888aa !important;
        font-size: 1rem;
    }

    /* ── Selectbox dropdowns ── */
    .stSelectbox > div > div {
        background: #1a1a2e !important;
        border-color: rgba(255,255,255,0.15) !important;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Carga de datos (cacheada)
# ──────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    """Lee las tablas DeltaLake silver ya limpias y las concatena."""
    base_path = os.path.join(os.path.dirname(__file__), "Data", "silver")

    frames = []
    for plan_dir in ["2008", "2023"]:
        path = os.path.join(base_path, plan_dir)
        if os.path.exists(path):
            dt = DeltaTable(path)
            df = dt.to_pandas()
            frames.append(df)

    if not frames:
        st.error("⚠️ No se encontraron tablas DeltaLake en Data/silver/")
        st.stop()

    df_all = pd.concat(frames, ignore_index=True)

    # Calcular porcentajes (protección contra división por cero)
    total = df_all["Total_Inscriptos"].replace(0, pd.NA)
    df_all["PCT_Libres"] = (df_all["Total_Libres"] / total * 100).fillna(0).round(1)
    df_all["PCT_Regulares"] = (df_all["Total_Regulares"] / total * 100).fillna(0).round(1)
    df_all["PCT_Promocionados"] = (df_all["Total_Promocionados"] / total * 100).fillna(0).round(1)

    # Limpiar espacios en blanco en los nombres de texto
    for col in ["Especialidad_Nombre", "Materia_Nombre"]:
        if col in df_all.columns:
            df_all[col] = df_all[col].str.strip()

    return df_all


df = cargar_datos()


import hashlib

# Hash para admin
ADMIN_HASH = "d5f79309d33084a2a439259a339fb25c423466b04f96af696e7078938f894545"

CODIGOS_ACCESO = {
    "39ef8f31d0da680489a9ee27fbb7aae463649feca145351a8b04ca69127a29ef": "Ingeniería en Sistemas de Información",
    "769485c82fbd36f35c88348310178e198f7baab84048d06cdd079d46c1acf8da": "Ingeniería Eléctrica",
    "33052eab97f393f947c111dc384c9105021cf2fbfadffe0461712f0bbe313348": "Ingeniería Electrónica",
    "c1041d8013062c05dcfe099eb0d5852f916fd9dea120bca819a9648fed1bdf14": "Ingeniería Mecánica",
    "d352f7a6195604ceb149687b0b3f6a10e88f9db5eae9b7ce99b998206c4626fd": "Ingeniería Civil",
}

def verificar_codigo(codigo_input):
    """Hashea el código ingresado y verifica acceso (admin o carrera)."""
    hash_input = hashlib.sha256(codigo_input.upper().encode()).hexdigest()
    if hash_input == ADMIN_HASH:
        return "__ADMIN__"
    return CODIGOS_ACCESO.get(hash_input)

# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎓 Dashboard de Alumnos UTN</h1>
    <p>Análisis interactivo de inscripciones por plan, especialidad y materia</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ──────────────────────────────────────────────
# Gate de acceso – pedir código
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔐 Acceso")
    st.caption("Ingresá el código de tu carrera para acceder a los datos.")

    codigo_ingresado = st.text_input(
        "🔑 Código de acceso",
        type="password",
        placeholder="Ingresá tu código",
        key="_codigo_acceso",
    )

    codigo_input = codigo_ingresado.strip()

# Validar código (hashear y buscar)
resultado_acceso = verificar_codigo(codigo_input) if codigo_input else None

if not resultado_acceso:
    st.markdown("")
    st.markdown(
        """
        <div style="text-align:center; padding: 4rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🔒</div>
            <h2 style="color: #e0e0ff !important;">Acceso restringido</h2>
            <p style="color: #8888aa; font-size: 1.1rem; max-width: 500px; margin: 0 auto;">
                Ingresá el código de tu carrera en la barra lateral para acceder
                al dashboard de datos académicos.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ──────────────────────────────────────────────
# Acceso concedido – determinar modo (admin o carrera)
# ──────────────────────────────────────────────
es_admin = resultado_acceso == "__ADMIN__"

def get_index(options_list, value):
    """Devuelve el índice del valor en la lista, o 0 si no existe."""
    try:
        return options_list.index(value)
    except ValueError:
        return 0

with st.sidebar:
    if es_admin:
        st.success("👑 **Modo Administrador**")
        st.divider()
        st.markdown("## 🔎 Filtros")

        # Admin: puede elegir cualquier especialidad
        especialidades_todas = sorted(df["Especialidad_Nombre"].unique())
        esp_seleccionada = st.selectbox(
            "🏛️ Especialidad", especialidades_todas,
            index=get_index(especialidades_todas, st.session_state.get("_esp_admin")),
            key="_esp_admin",
        )
        df_esp = df[df["Especialidad_Nombre"] == esp_seleccionada]
    else:
        esp_seleccionada = resultado_acceso
        st.success(f"✅ **{esp_seleccionada}**")
        st.divider()
        st.markdown("## 🔎 Filtros")
        df_esp = df[df["Especialidad_Nombre"] == esp_seleccionada]

    if df_esp.empty:
        st.error(f"No se encontraron datos para {esp_seleccionada}.")
        st.stop()

    # Plan
    planes_disponibles = sorted(df_esp["Plan"].unique())
    plan_seleccionado = st.selectbox(
        "📋 Plan", planes_disponibles,
        index=get_index(planes_disponibles, st.session_state.get("_plan")),
        key="_plan",
    )
    df_filtrado = df_esp[df_esp["Plan"] == plan_seleccionado]

    # Materia
    materias = sorted(df_filtrado["Materia_Nombre"].unique())
    materia_seleccionada = st.selectbox(
        "📚 Materia", materias,
        index=get_index(materias, st.session_state.get("_mat")),
        key="_mat",
    )
    df_materia = df_filtrado[df_filtrado["Materia_Nombre"] == materia_seleccionada]

    st.divider()
    st.markdown(f"**Registros filtrados:** {len(df_filtrado)}")


# Colores globales para los gráficos
COLOR_LIBRES = "#ef4444"
COLOR_REGULARES = "#f59e0b"
COLOR_PROMO = "#22c55e"
COLOR_NUEVOS = "#818cf8"
COLOR_RECURSANTES = "#38bdf8"

# Layout base de plotly para fondo transparente y texto claro
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#d0d0e8", size=13),
)


# ──────────────────────────────────────────────
# Métricas de la materia seleccionada
# ──────────────────────────────────────────────
st.markdown(f"### 📌 {materia_seleccionada}")
st.caption(f"Plan {plan_seleccionado}  ·  {esp_seleccionada}")

if not df_materia.empty:
    row = df_materia.iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Inscriptos", int(row["Total_Inscriptos"]))
    col2.metric("🔴 Libres", f"{row['PCT_Libres']}%", f"{int(row['Total_Libres'])} alumnos")
    col3.metric("🟡 Regulares", f"{row['PCT_Regulares']}%", f"{int(row['Total_Regulares'])} alumnos")
    col4.metric("🟢 Promocionados", f"{row['PCT_Promocionados']}%", f"{int(row['Total_Promocionados'])} alumnos")

    st.markdown("")

    # ──────────────────────────────────────────
    # Fila 1 de gráficos: Dona + Barras generales
    # ──────────────────────────────────────────
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### 🍩 Distribución de la materia")

        labels = ["Libres", "Regulares", "Promocionados"]
        values = [
            int(row["Total_Libres"]),
            int(row["Total_Regulares"]),
            int(row["Total_Promocionados"]),
        ]
        colors = [COLOR_LIBRES, COLOR_REGULARES, COLOR_PROMO]

        fig_dona = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker=dict(colors=colors, line=dict(color="#1a1a2e", width=2)),
            textinfo="label+percent",
            textfont=dict(size=14, color="#ffffff"),
            hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>",
        )])
        fig_dona.update_layout(
            **PLOTLY_LAYOUT,
            showlegend=False,
            height=380,
            margin=dict(t=10, b=10, l=10, r=10),
        )
        st.plotly_chart(fig_dona, use_container_width=True)

    with chart_col2:
        st.markdown("#### 📊 Nuevos Inscriptos vs Recursantes")

        cat_labels = ["Libres", "Regulares", "Promocionados"]
        nuevos = [
            int(row["Nuevos_Inscriptos_Libres"]),
            int(row["Nuevos_Inscriptos_Regulares"]),
            int(row["Nuevos_Inscriptos_Promocionados"]),
        ]
        recursantes = [
            int(row["Recursantes_Libres"]),
            int(row["Recursantes_Regulares"]),
            int(row["Recursantes_Promocionados"]),
        ]

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Nuevos Inscriptos",
            x=cat_labels, y=nuevos,
            marker_color=COLOR_NUEVOS,
            text=nuevos, textposition="inside",
            textfont=dict(color="#ffffff", size=13),
            hovertemplate="<b>Nuevos – %{x}</b>: %{y}<extra></extra>",
        ))
        fig_bar.add_trace(go.Bar(
            name="Recursantes",
            x=cat_labels, y=recursantes,
            marker_color=COLOR_RECURSANTES,
            text=recursantes, textposition="inside",
            textfont=dict(color="#ffffff", size=13),
            hovertemplate="<b>Recursantes – %{x}</b>: %{y}<extra></extra>",
        ))
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            barmode="stack",
            height=380,
            margin=dict(t=10, b=40, l=40, r=10),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="center", x=0.5,
                font=dict(color="#d0d0e8", size=12),
            ),
            xaxis=dict(tickfont=dict(color="#c0c0d8")),
            yaxis=dict(tickfont=dict(color="#c0c0d8")),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ──────────────────────────────────────────
    # NUEVA SECCIÓN: Desglose Nuevos vs Recursantes
    # ──────────────────────────────────────────
    st.divider()
    st.markdown("### 🔬 Desglose: Nuevos Inscriptos vs Recursantes")
    st.caption(f"Composición detallada de cada categoría para **{materia_seleccionada}**")

    # Tabla resumen
    desglose_data = {
        "Categoría": ["Libres", "Regulares", "Promocionados", "**TOTAL**"],
        "Nuevos Inscriptos": [
            int(row["Nuevos_Inscriptos_Libres"]),
            int(row["Nuevos_Inscriptos_Regulares"]),
            int(row["Nuevos_Inscriptos_Promocionados"]),
            int(row["Nuevos_Inscriptos"]),
        ],
        "Recursantes": [
            int(row["Recursantes_Libres"]),
            int(row["Recursantes_Regulares"]),
            int(row["Recursantes_Promocionados"]),
            int(row["Recursantes"]),
        ],
        "Total": [
            int(row["Total_Libres"]),
            int(row["Total_Regulares"]),
            int(row["Total_Promocionados"]),
            int(row["Total_Inscriptos"]),
        ],
    }
    df_desglose = pd.DataFrame(desglose_data)

    # Calcular porcentajes de composición (qué % de los libres son nuevos vs recursantes)
    total_safe = df_desglose["Total"].replace(0, pd.NA)
    df_desglose["% Nuevos"] = (df_desglose["Nuevos Inscriptos"] / total_safe * 100).fillna(0).round(1).astype(str) + "%"
    df_desglose["% Recursantes"] = (df_desglose["Recursantes"] / total_safe * 100).fillna(0).round(1).astype(str) + "%"

    desg_col1, desg_col2 = st.columns([1, 1])

    with desg_col1:
        st.dataframe(df_desglose, use_container_width=True, hide_index=True)

    with desg_col2:
        # Gráfico de barras agrupadas (lado a lado) para comparar
        categorias = ["Libres", "Regulares", "Promocionados"]

        fig_desg = go.Figure()
        fig_desg.add_trace(go.Bar(
            name="Nuevos Inscriptos",
            x=categorias,
            y=[int(row["Nuevos_Inscriptos_Libres"]), int(row["Nuevos_Inscriptos_Regulares"]), int(row["Nuevos_Inscriptos_Promocionados"])],
            marker=dict(color=COLOR_NUEVOS, line=dict(width=0)),
            text=[int(row["Nuevos_Inscriptos_Libres"]), int(row["Nuevos_Inscriptos_Regulares"]), int(row["Nuevos_Inscriptos_Promocionados"])],
            textposition="outside",
            textfont=dict(color="#c0c0e0", size=13),
        ))
        fig_desg.add_trace(go.Bar(
            name="Recursantes",
            x=categorias,
            y=[int(row["Recursantes_Libres"]), int(row["Recursantes_Regulares"]), int(row["Recursantes_Promocionados"])],
            marker=dict(color=COLOR_RECURSANTES, line=dict(width=0)),
            text=[int(row["Recursantes_Libres"]), int(row["Recursantes_Regulares"]), int(row["Recursantes_Promocionados"])],
            textposition="outside",
            textfont=dict(color="#c0c0e0", size=13),
        ))
        fig_desg.update_layout(
            **PLOTLY_LAYOUT,
            barmode="group",
            height=350,
            margin=dict(t=30, b=40, l=40, r=10),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="center", x=0.5,
                font=dict(color="#d0d0e8", size=12),
            ),
            xaxis=dict(tickfont=dict(color="#c0c0d8")),
            yaxis=dict(tickfont=dict(color="#c0c0d8"), title="Cantidad", title_font=dict(color="#a0a0c0")),
        )
        st.plotly_chart(fig_desg, use_container_width=True)

else:
    st.warning("No se encontraron datos para esa selección.")

# ──────────────────────────────────────────────
# Gráfico comparativo de TODAS las materias
# ──────────────────────────────────────────────
st.divider()
st.markdown("### 📈 Comparativa: todas las materias de la especialidad")
st.caption(f"{esp_seleccionada} – Plan {plan_seleccionado}")

if not df_filtrado.empty:
    df_comp = df_filtrado.sort_values("Total_Inscriptos", ascending=True)

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        name="Libres",
        y=df_comp["Materia_Nombre"], x=df_comp["Total_Libres"],
        orientation="h", marker_color=COLOR_LIBRES,
    ))
    fig_comp.add_trace(go.Bar(
        name="Regulares",
        y=df_comp["Materia_Nombre"], x=df_comp["Total_Regulares"],
        orientation="h", marker_color=COLOR_REGULARES,
    ))
    fig_comp.add_trace(go.Bar(
        name="Promocionados",
        y=df_comp["Materia_Nombre"], x=df_comp["Total_Promocionados"],
        orientation="h", marker_color=COLOR_PROMO,
    ))
    fig_comp.update_layout(
        **PLOTLY_LAYOUT,
        barmode="stack",
        height=max(350, len(df_comp) * 38),
        margin=dict(t=10, b=20, l=10, r=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font=dict(color="#d0d0e8", size=12),
        ),
        xaxis=dict(title="Cantidad de alumnos", tickfont=dict(color="#c0c0d8"), title_font=dict(color="#a0a0c0")),
        yaxis=dict(tickfont=dict(color="#c0c0d8")),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

# ──────────────────────────────────────────────
# Tabla de datos + Descarga CSV
# ──────────────────────────────────────────────
st.divider()
st.markdown("### 🗂️ Tabla de datos filtrados")

cols_mostrar = [
    "Materia_Nombre", "Total_Inscriptos",
    "Total_Libres", "PCT_Libres",
    "Total_Regulares", "PCT_Regulares",
    "Total_Promocionados", "PCT_Promocionados",
    "Nuevos_Inscriptos", "Recursantes",
]

df_tabla = df_filtrado[cols_mostrar].sort_values("Total_Inscriptos", ascending=False)
st.dataframe(df_tabla, use_container_width=True, hide_index=True)

csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Descargar datos como CSV",
    data=csv,
    file_name=f"alumnos_{esp_seleccionada.replace(' ','_')}_plan{plan_seleccionado}.csv",
    mime="text/csv",
)
