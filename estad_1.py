import pandas as pd
import matplotlib.pyplot as plt
import unicodedata


# Cargar datos
df = pd.read_excel("datos_universitarios.xlsx")




# Función para normalizar texto (eliminar tildes y pasar a minúsculas)
def normalizar(texto):
    if pd.isnull(texto):
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(texto).lower())
        if unicodedata.category(c) != 'Mn'
    )


# Normalizar columna de nombre de carrera
df['NOMBRE CARRERA NORMALIZADO'] = df['NOMBRE CARRERA'].apply(normalizar)

# --- Análisis de la cantidad total de personas matriculadas por año ---
# Filtrar solo años completos (enteros)
df_anos_completos = df[df['AÑO INGRESO'].apply(lambda x: float(x).is_integer())]
df_anos_completos['AÑO INGRESO'] = df_anos_completos['AÑO INGRESO'].astype(int)
matriculas_totales = df_anos_completos.groupby('AÑO INGRESO').size().sort_index()
print("\nCantidad total de personas matriculadas por año (solo años enteros):")
print(matriculas_totales)

# Gráfico de la cantidad total de personas matriculadas por año (solo años enteros)
plt.figure(figsize=(10,5))
plt.plot(matriculas_totales.index.astype(int), matriculas_totales.values, marker='o', color='tab:blue')
plt.title('Cantidad total de personas matriculadas por año (solo años enteros)')
plt.xlabel('Año de ingreso')
plt.ylabel('Cantidad de personas matriculadas')
plt.xticks(matriculas_totales.index.astype(int))
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# --- Análisis para carreras del área de la salud ---

# Palabras clave asociadas a salud
palabras_salud = [
    "salud", "enfermeria", "medicina", "kinesiologia", "nutricion", "odontologia", "tecnologia medica",
    "fisioterapia", "terapia", "quimica y farmacia", "bioquimica", "obstetricia", "matroneria", "fonoaudiologia",
    "psicologia", "laboratorio clinico", "paramedico", "tecnico en enfermeria", "tecnico en salud"
]

# Filtrar carreras de salud (normalizando)
df_salud = df[df['NOMBRE CARRERA NORMALIZADO'].str.contains('|'.join(palabras_salud), case=False, na=False)]

# Agrupar por año de ingreso y contar matrículas
tendencia_salud = df_salud.groupby('AÑO INGRESO').size()
total_anual_salud = df.groupby('AÑO INGRESO').size()
porcentaje_salud = (tendencia_salud / total_anual_salud * 100).fillna(0)

# Gráfico combinado: cantidad y porcentaje de matrículas en salud por año
fig, ax1 = plt.subplots(figsize=(10,5))
color1 = 'tab:red'
ax1.set_xlabel('Año de ingreso')
ax1.set_ylabel('Cantidad de matrículas (salud)', color=color1)
ax1.plot(tendencia_salud.index.astype(int), tendencia_salud.values, marker='o', color=color1, label='Cantidad de matrículas (salud)')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
color2 = 'tab:purple'
ax2.set_ylabel('Porcentaje (%)', color=color2)
ax2.plot(porcentaje_salud.index.astype(int), porcentaje_salud.values, marker='s', color=color2, label='Porcentaje (%)')
ax2.tick_params(axis='y', labelcolor=color2)

fig.suptitle('Matrículas en carreras del área de la salud por año')
fig.tight_layout()
fig.legend(loc='upper left', bbox_to_anchor=(0.15, 0.85))
plt.show()


# --- Gráficos de cantidad de mujeres y hombres en carreras de salud por año ---
# Filtrar mujeres y hombres en carreras de salud (normalizando)
df_salud_mujeres = df_salud[df_salud['GENERO'].str.lower().str.contains('femenino|mujer|f', na=False)]
df_salud_hombres = df_salud[df_salud['GENERO'].str.lower().str.contains('masculino|hombre|m', na=False)]

# Agrupar por año de ingreso
matriculas_mujeres_salud = df_salud_mujeres.groupby('AÑO INGRESO').size()
matriculas_hombres_salud = df_salud_hombres.groupby('AÑO INGRESO').size()

# Gráfico de mujeres en carreras de salud
plt.figure(figsize=(10,5))
plt.plot(matriculas_mujeres_salud.index.astype(int), matriculas_mujeres_salud.values, marker='o', color='deeppink', label='Mujeres')
plt.title('Cantidad de mujeres matriculadas en carreras de salud por año')
plt.xlabel('Año de ingreso')
plt.ylabel('Cantidad de mujeres')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico de hombres en carreras de salud
plt.figure(figsize=(10,5))
plt.plot(matriculas_hombres_salud.index.astype(int), matriculas_hombres_salud.values, marker='o', color='navy', label='Hombres')
plt.title('Cantidad de hombres matriculados en carreras de salud por año')
plt.xlabel('Año de ingreso')
plt.ylabel('Cantidad de hombres')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# --- Comparación de matrículas en carreras de salud: prepandemia vs pandemia (2020-2021) ---
# Usar solo años enteros
df_salud_anos = df_salud[df_salud['AÑO INGRESO'].apply(lambda x: float(x).is_integer())].copy()
df_salud_anos['AÑO INGRESO'] = df_salud_anos['AÑO INGRESO'].astype(int)

# Definir periodos
prepandemia = df_salud_anos[df_salud_anos['AÑO INGRESO'] < 2020]
pandemia = df_salud_anos[df_salud_anos['AÑO INGRESO'].isin([2020, 2021])]

matriculas_pre = prepandemia.groupby('AÑO INGRESO').size()
matriculas_pandemia = pandemia.groupby('AÑO INGRESO').size()

print("\nMatrículas en carreras de salud - Años prepandemia:")
print(matriculas_pre)
print("\nMatrículas en carreras de salud - Años pandemia (2020-2021):")
print(matriculas_pandemia)

# Gráfico comparativo
plt.figure(figsize=(8,5))
plt.bar(matriculas_pre.index, matriculas_pre.values, color='skyblue', label='Pre-pandemia')
plt.bar(matriculas_pandemia.index, matriculas_pandemia.values, color='salmon', label='Pandemia (2020-2021)')
plt.title('Matrículas en carreras de salud: Pre-pandemia vs Pandemia (2020-2021)')
plt.xlabel('Año de ingreso')
plt.ylabel('Cantidad de matrículas')
plt.legend()
plt.xticks(sorted(list(matriculas_pre.index) + list(matriculas_pandemia.index)))
plt.tight_layout()
plt.show()

import pandas as pd
import matplotlib.pyplot as plt
import unicodedata

# Función para normalizar texto (eliminar tildes y pasar a minúsculas)
def normalizar(texto):
    if pd.isnull(texto):
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(texto).lower())
        if unicodedata.category(c) != 'Mn'
    )

# Cargar datos
df = pd.read_excel("datos_universitarios.xlsx")

# Normalizar columna de nombre de carrera
df['NOMBRE CARRERA NORMALIZADO'] = df['NOMBRE CARRERA'].apply(normalizar)

# --- Análisis de la cantidad total de personas matriculadas por año ---
# Filtrar solo años completos (enteros)
df_anos_completos = df[df['AÑO INGRESO'].apply(lambda x: float(x).is_integer())]
df_anos_completos['AÑO INGRESO'] = df_anos_completos['AÑO INGRESO'].astype(int)
matriculas_totales = df_anos_completos.groupby('AÑO INGRESO').size().sort_index()
print("\nCantidad total de personas matriculadas por año (solo años enteros):")
print(matriculas_totales)

# Gráfico de la cantidad total de personas matriculadas por año (solo años enteros)
plt.figure(figsize=(10,5))
plt.plot(matriculas_totales.index, matriculas_totales.values, marker='o', color='tab:blue')
plt.title('Cantidad total de personas matriculadas por año (solo años enteros)')
plt.xlabel('Año de ingreso')
plt.ylabel('Cantidad de personas matriculadas')
plt.xticks(matriculas_totales.index)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# --- Análisis para carreras del área de la salud ---

# Palabras clave asociadas a salud
palabras_salud = [
    "salud", "enfermeria", "medicina", "kinesiologia", "nutricion", "odontologia", "tecnologia medica",
    "fisioterapia", "terapia", "quimica y farmacia", "bioquimica", "obstetricia", "matroneria", "fonoaudiologia",
    "psicologia", "laboratorio clinico", "paramedico", "tecnico en enfermeria", "tecnico en salud"
]

# Filtrar carreras de salud (normalizando)
df_salud = df[df['NOMBRE CARRERA NORMALIZADO'].str.contains('|'.join(palabras_salud), case=False, na=False)]

# Agrupar por año de ingreso y contar matrículas
tendencia_salud = df_salud.groupby('AÑO INGRESO').size()
total_anual_salud = df.groupby('AÑO INGRESO').size()
porcentaje_salud = (tendencia_salud / total_anual_salud * 100).fillna(0)

# Gráfico combinado: cantidad y porcentaje de matrículas en salud por año
fig, ax1 = plt.subplots(figsize=(10,5))
color1 = 'tab:red'
ax1.set_xlabel('Año de ingreso')
ax1.set_ylabel('Cantidad de matrículas (salud)', color=color1)
ax1.plot(tendencia_salud.index, tendencia_salud.values, marker='o', color=color1, label='Cantidad de matrículas (salud)')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
color2 = 'tab:purple'
ax2.set_ylabel('Porcentaje (%)', color=color2)
ax2.plot(porcentaje_salud.index, porcentaje_salud.values, marker='s', color=color2, label='Porcentaje (%)')
ax2.tick_params(axis='y', labelcolor=color2)

fig.suptitle('Matrículas en carreras del área de la salud por año')
fig.tight_layout()
fig.legend(loc='upper left', bbox_to_anchor=(0.15, 0.85))
plt.show()


# Palabras clave asociadas a temas de campo, animales, plantaciones, etc.
palabras_clave = [
    "agro", "veterinaria", "agricultura", "forestal", "pecuaria", "zootecnia",
    "alimentos", "plantas", "bosque", "rural", "lecheria", "fruticultura", "horticultura"
]

# Filtrar carreras relacionadas (normalizando)
df_campo = df[df['NOMBRE CARRERA NORMALIZADO'].str.contains('|'.join(palabras_clave), case=False, na=False)]

# Agrupar por año de ingreso y contar matrículas
tendencia = df_campo.groupby('AÑO INGRESO').size()

print("Tendencia de matrículas en carreras de campo/animales/plantaciones por año:")
print(tendencia)

# Si quieres ver el porcentaje respecto al total de matrículas por año:
total_anual = df.groupby('AÑO INGRESO').size()
porcentaje = (tendencia / total_anual * 100).fillna(0)

print("\nPorcentaje de matrículas en carreras de campo respecto al total por año:")
print(porcentaje)

# Gráfico combinado: cantidad y porcentaje de matrículas por año
fig, ax1 = plt.subplots(figsize=(10,5))

color1 = 'tab:blue'
ax1.set_xlabel('Año de ingreso')
ax1.set_ylabel('Cantidad de matrículas', color=color1)
ax1.plot(tendencia.index, tendencia.values, marker='o', color=color1, label='Cantidad de matrículas')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
color2 = 'tab:green'
ax2.set_ylabel('Porcentaje (%)', color=color2)
ax2.plot(porcentaje.index, porcentaje.values, marker='s', color=color2, label='Porcentaje (%)')
ax2.tick_params(axis='y', labelcolor=color2)

fig.suptitle('Matrículas en carreras de campo/animales/plantaciones por año')
fig.tight_layout()
fig.legend(loc='upper left', bbox_to_anchor=(0.15, 0.85))
plt.show()