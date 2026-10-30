# ================================================================
# PROYECTO: CALCULADORA GEOMÉTRICA ANALÍTICA 3D
# TECNOLOGÍAS: PYTHON + STREAMLIT + PLOTLY + NUMPY
#
# DESCRIPCIÓN:
# Aplicación web interactiva para visualizar sólidos geométricos,
# modificar sus dimensiones y calcular sus propiedades.
#
# FIGURAS:
# 1. Esfera.
# 2. Elipsoide.
# 3. Prisma regular de base poligonal.
#
# INSTALACIÓN LOCAL:
# python -m pip install -r requirements.txt
#
# EJECUCIÓN:
# streamlit run app.py
# ================================================================


# ------------------------------------------------
# 1. IMPORTACIÓN DE LIBRERÍAS
# ------------------------------------------------

import streamlit as st
import numpy as np
import plotly.graph_objects as go

import math


# ------------------------------------------------
# 2. CONFIGURACIÓN GENERAL DE STREAMLIT
# ------------------------------------------------

st.set_page_config(
    page_title="Calculadora Geométrica 3D",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ------------------------------------------------
# 3. ENCABEZADO DE LA APLICACIÓN
# ------------------------------------------------

st.title("📐 Calculadora Geométrica Analítica 3D")

st.markdown(
    """
    Visualiza, modifica y analiza diferentes sólidos geométricos
    mediante una interfaz interactiva tridimensional.
    """
)

st.divider()


# ------------------------------------------------
# 4. FUNCIONES PARA CONSTRUIR LAS FIGURAS
# ------------------------------------------------


# ================================================================
# 4.1 CONSTRUCCIÓN DE LA ESFERA
# ================================================================

def construir_esfera(radio):

    """
    Construye una esfera utilizando coordenadas esféricas.

    X = r * sen(v) * cos(u)
    Y = r * sen(v) * sen(u)
    Z = r * cos(v)
    """

    u = np.linspace(0, 2 * np.pi, 70)

    v = np.linspace(0, np.pi, 70)

    U, V = np.meshgrid(u, v)

    X = radio * np.sin(V) * np.cos(U)

    Y = radio * np.sin(V) * np.sin(U)

    Z = radio * np.cos(V)

    return X, Y, Z


# ================================================================
# 4.2 CONSTRUCCIÓN DEL ELIPSOIDE
# ================================================================

def construir_elipsoide(a, b, c):

    """
    Construye un elipsoide mediante tres semiejes.

    X = a * sen(v) * cos(u)
    Y = b * sen(v) * sen(u)
    Z = c * cos(v)

    Ecuación implícita:

    X²/a² + Y²/b² + Z²/c² = 1
    """

    u = np.linspace(0, 2 * np.pi, 70)

    v = np.linspace(0, np.pi, 70)

    U, V = np.meshgrid(u, v)

    X = a * np.sin(V) * np.cos(U)

    Y = b * np.sin(V) * np.sin(U)

    Z = c * np.cos(V)

    return X, Y, Z


# ================================================================
# 4.3 CONSTRUCCIÓN DEL PRISMA
# ================================================================

def construir_prisma(n, radio, altura):

    """
    Construye un prisma recto de base poligonal regular.

    X = R * cos(angulo)
    Y = R * sen(angulo)

    La base inferior se ubica en Z = 0.
    La base superior se ubica en Z = altura.

    R representa el radio circunscrito del polígono.
    """

    # Calculamos los ángulos de los vértices.

    angulos = np.linspace(
        0,
        2 * np.pi,
        n,
        endpoint=False
    )

    # Coordenadas de los vértices inferiores.

    x = radio * np.cos(angulos)

    y = radio * np.sin(angulos)

    # Creamos las coordenadas tridimensionales.

    vertices = []

    for i in range(n):

        vertices.append([
            x[i],
            y[i],
            0
        ])

    # Agregamos los vértices de la parte superior.

    for i in range(n):

        vertices.append([
            x[i],
            y[i],
            altura
        ])

    vertices = np.array(vertices)

    # Creamos los triángulos de las bases y caras laterales.

    I, J, K = [], [], []

    # Triangulación de la base inferior y superior.

    for i in range(1, n - 1):

        # Base inferior.

        I.append(0)
        J.append(i + 1)
        K.append(i)

        # Base superior.

        I.append(n)
        J.append(n + i)
        K.append(n + i + 1)

    # Triangulación de las caras laterales.

    for i in range(n):

        siguiente = (i + 1) % n

        inferior_1 = i
        inferior_2 = siguiente

        superior_1 = i + n
        superior_2 = siguiente + n

        # Primer triángulo de la cara lateral.

        I.append(inferior_1)
        J.append(inferior_2)
        K.append(superior_2)

        # Segundo triángulo de la cara lateral.

        I.append(inferior_1)
        J.append(superior_2)
        K.append(superior_1)

    return vertices, I, J, K, x, y


# ------------------------------------------------
# 5. FUNCIONES PARA CREAR LA VISUALIZACIÓN 3D
# ------------------------------------------------

def agregar_malla(figura, X, Y, Z, color):

    """
    Agrega una superficie sombreada y líneas de referencia
    para visualizar mejor la geometría.
    """

    figura.add_trace(

        go.Surface(
            x=X,
            y=Y,
            z=Z,
            colorscale=color,
            showscale=False,
            opacity=0.88,
            name="Superficie"
        )

    )

    # Construimos líneas de alambre sobre la superficie.

    for i in range(0, X.shape[0], 8):

        figura.add_trace(
            go.Scatter3d(
                x=X[i, :],
                y=Y[i, :],
                z=Z[i, :],
                mode="lines",
                line=dict(
                    color="black",
                    width=1
                ),
                showlegend=False,
                hoverinfo="skip"
            )
        )

    for j in range(0, X.shape[1], 8):

        figura.add_trace(
            go.Scatter3d(
                x=X[:, j],
                y=Y[:, j],
                z=Z[:, j],
                mode="lines",
                line=dict(
                    color="black",
                    width=1
                ),
                showlegend=False,
                hoverinfo="skip"
            )
        )


# ================================================================
# VISUALIZACIÓN DEL PRISMA
# ================================================================

def agregar_prisma(figura, vertices, I, J, K, n):

    """
    Representa el prisma mediante una malla triangular 3D
    y dibuja sus aristas para destacar su estructura.
    """

    figura.add_trace(

        go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=I,
            j=J,
            k=K,
            color="#4C9BE8",
            opacity=0.85,
            flatshading=True,
            name="Prisma"
        )

    )

    # Dibujamos las aristas de las dos bases.

    for i in range(n):

        siguiente = (i + 1) % n

        # Arista inferior.

        figura.add_trace(
            go.Scatter3d(
                x=[
                    vertices[i, 0],
                    vertices[siguiente, 0]
                ],
                y=[
                    vertices[i, 1],
                    vertices[siguiente, 1]
                ],
                z=[
                    vertices[i, 2],
                    vertices[siguiente, 2]
                ],
                mode="lines",
                line=dict(color="black", width=4),
                showlegend=False,
                hoverinfo="skip"
            )
        )

        # Arista superior.

        figura.add_trace(
            go.Scatter3d(
                x=[
                    vertices[i + n, 0],
                    vertices[siguiente + n, 0]
                ],
                y=[
                    vertices[i + n, 1],
                    vertices[siguiente + n, 1]
                ],
                z=[
                    vertices[i + n, 2],
                    vertices[siguiente + n, 2]
                ],
                mode="lines",
                line=dict(color="black", width=4),
                showlegend=False,
                hoverinfo="skip"
            )
        )

        # Arista vertical.

        figura.add_trace(
            go.Scatter3d(
                x=[
                    vertices[i, 0],
                    vertices[i + n, 0]
                ],
                y=[
                    vertices[i, 1],
                    vertices[i + n, 1]
                ],
                z=[
                    vertices[i, 2],
                    vertices[i + n, 2]
                ],
                mode="lines",
                line=dict(color="black", width=4),
                showlegend=False,
                hoverinfo="skip"
            )
        )


# ------------------------------------------------
# 6. SELECTOR DE FIGURAS GEOMÉTRICAS
# ------------------------------------------------

st.sidebar.header("⚙️ Panel de configuración")

figura_seleccionada = st.sidebar.selectbox(

    "Selecciona una figura geométrica:",

    [
        "Esfera",
        "Elipsoide",
        "Prisma"
    ]

)


# ------------------------------------------------
# 7. CONFIGURACIÓN DE PARÁMETROS
# ------------------------------------------------

# Inicializamos las variables de cálculo.

area = 0.0

volumen = 0.0

perimetro = None

descripcion = ""


# ------------------------------------------------
# 8. CONFIGURACIÓN DE LA ESFERA
# ------------------------------------------------

if figura_seleccionada == "Esfera":

    st.sidebar.subheader("Parámetros de la esfera")

    radio = st.sidebar.slider(
        "Radio (r)",
        min_value=0.5,
        max_value=10.0,
        value=2.0,
        step=0.1
    )

    # Construimos las coordenadas.

    X, Y, Z = construir_esfera(radio)

    # Cálculos geométricos.

    area = 4 * np.pi * radio**2

    volumen = (4 / 3) * np.pi * radio**3

    descripcion = f"Radio: {radio:.2f} unidades"

    # Creamos la figura.

    grafico = go.Figure()

    agregar_malla(
        grafico,
        X, Y, Z,
        "Viridis"
    )

    limite = radio * 1.3


# ------------------------------------------------
# 9. CONFIGURACIÓN DEL ELIPSOIDE
# ------------------------------------------------

elif figura_seleccionada == "Elipsoide":

    st.sidebar.subheader("Parámetros del elipsoide")

    a = st.sidebar.slider(
        "Radio X (a)",
        0.5, 10.0, 2.0, 0.1
    )

    b = st.sidebar.slider(
        "Radio Y (b)",
        0.5, 10.0, 1.5, 0.1
    )

    c = st.sidebar.slider(
        "Radio Z (c)",
        0.5, 10.0, 1.0, 0.1
    )

    # Construimos las coordenadas.

    X, Y, Z = construir_elipsoide(a, b, c)

    # Volumen exacto del elipsoide.

    volumen = (4 / 3) * np.pi * a * b * c

    # Aproximación del área superficial mediante
    # la fórmula de Knud Thomsen.

    p = 1.6075

    area = 4 * np.pi * (
        (
            (a * b)**p +
            (a * c)**p +
            (b * c)**p
        ) / 3
    )**(1 / p)

    descripcion = (
        f"Semiejes: a={a:.2f}, "
        f"b={b:.2f}, c={c:.2f}"
    )

    grafico = go.Figure()

    agregar_malla(
        grafico,
        X, Y, Z,
        "Plasma"
    )

    limite = 1.3 * max(a, b, c)


# ------------------------------------------------
# 10. CONFIGURACIÓN DEL PRISMA
# ------------------------------------------------

elif figura_seleccionada == "Prisma":

    st.sidebar.subheader("Parámetros del prisma")

    n = st.sidebar.slider(
        "Número de lados de la base",
        min_value=3,
        max_value=20,
        value=6,
        step=1
    )

    radio = st.sidebar.slider(
        "Radio circunscrito de la base",
        min_value=0.5,
        max_value=10.0,
        value=2.0,
        step=0.1
    )

    altura = st.sidebar.slider(
        "Altura del prisma",
        min_value=0.5,
        max_value=15.0,
        value=4.0,
        step=0.1
    )

    # Construimos la geometría del prisma.

    vertices, I, J, K, x, y = construir_prisma(
        n,
        radio,
        altura
    )

    # Calculamos las propiedades de la base regular.

    angulo = 2 * np.pi / n

    area_base = (
        n * radio**2 * np.sin(angulo) / 2
    )

    perimetro = (
        2 * n * radio * np.sin(np.pi / n)
    )

    # Área lateral y total.

    area_lateral = perimetro * altura

    area = 2 * area_base + area_lateral

    # Volumen del prisma.

    volumen = area_base * altura

    descripcion = (
        f"{n} lados | Radio: {radio:.2f} | "
        f"Altura: {altura:.2f}"
    )

    grafico = go.Figure()

    agregar_prisma(
        grafico,
        vertices,
        I, J, K,
        n
    )

    limite = radio * 1.3


# ------------------------------------------------
# 11. CONFIGURACIÓN DEL GRÁFICO 3D
# ------------------------------------------------

grafico.update_layout(

    title=dict(
        text=f"Visualización 3D: {figura_seleccionada}",
        x=0.5
    ),

    height=620,

    margin=dict(
        l=0,
        r=0,
        t=60,
        b=0
    ),

    scene=dict(

        xaxis=dict(
            title="Eje X",
            range=[-limite, limite]
        ),

        yaxis=dict(
            title="Eje Y",
            range=[-limite, limite]
        ),

        zaxis=dict(
            title="Eje Z"
        ),

        aspectmode="data",

        camera=dict(
            eye=dict(
                x=1.6,
                y=1.6,
                z=1.2
            )
        )
    )
)


# ------------------------------------------------
# 12. DISTRIBUCIÓN DE LA INTERFAZ
# ------------------------------------------------

columna_grafico, columna_resultados = st.columns(
    [2.2, 1]
)


# ------------------------------------------------
# 13. VISUALIZACIÓN PRINCIPAL
# ------------------------------------------------

with columna_grafico:

    st.subheader("Representación tridimensional")

    st.plotly_chart(
        grafico,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "scrollZoom": True
        }
    )

    st.caption(
        "Puedes girar, acercar, alejar y explorar "
        "la figura utilizando el mouse."
    )


# ------------------------------------------------
# 14. RESULTADOS ANALÍTICOS
# ------------------------------------------------

with columna_resultados:

    st.subheader("📊 Resultados geométricos")

    st.info(descripcion)

    st.metric(
        label="Volumen",
        value=f"{volumen:,.3f} u³"
    )

    st.metric(
        label="Área superficial",
        value=f"{area:,.3f} u²"
    )

    # Mostramos el perímetro cuando corresponde.

    if perimetro is not None:

        st.metric(
            label="Perímetro de la base",
            value=f"{perimetro:,.3f} u"
        )

        st.metric(
            label="Área de la base",
            value=f"{area_base:,.3f} u²"
        )

    st.divider()

    st.markdown("**Interpretación:**")

    if figura_seleccionada == "Esfera":

        st.write(
            "La esfera presenta simetría en sus tres "
            "dimensiones y su volumen depende del "
            "cubo del radio."
        )

    elif figura_seleccionada == "Elipsoide":

        st.write(
            "El elipsoide presenta tres semiejes "
            "independientes que determinan su forma "
            "y volumen."
        )

    elif figura_seleccionada == "Prisma":

        st.write(
            "El prisma está compuesto por dos bases "
            "poligonales iguales y caras laterales "
            "rectangulares."
        )


# ------------------------------------------------
# 15. INFORMACIÓN TÉCNICA
# ------------------------------------------------

st.divider()

with st.expander("📐 Consultar fórmulas matemáticas"):

    if figura_seleccionada == "Esfera":

        st.latex(r"A = 4\pi r^2")

        st.latex(r"V = \frac{4}{3}\pi r^3")

    elif figura_seleccionada == "Elipsoide":

        st.latex(r"V = \frac{4}{3}\pi abc")

        st.latex(
            r"A \approx 4\pi "
            r"\left(\frac{(ab)^p+(ac)^p+(bc)^p}{3}"
            r"\right)^{1/p}"
        )

        st.caption(
            "El área superficial se estima mediante "
            "la aproximación de Knud Thomsen, con p=1.6075."
        )

    elif figura_seleccionada == "Prisma":

        st.latex(
            r"A_b = \frac{nR^2}{2}"
            r"\sin\left(\frac{2\pi}{n}\right)"
        )

        st.latex(
            r"P_b = 2nR\sin\left(\frac{\pi}{n}\right)"
        )

        st.latex(
            r"A_T = 2A_b + P_bh"
        )

        st.latex(
            r"V = A_bh"
        )


# ------------------------------------------------
# 16. PIE DE PÁGINA
# ------------------------------------------------

st.divider()

st.caption(
    "Calculadora Geométrica Analítica 3D | "
    "Desarrollada con Python, Streamlit, NumPy y Plotly."
)

# ================================================================
# FIN DEL PROGRAMA
# ================================================================