import pandas as pd
import matplotlib.pyplot as plt

print("Inicio del análisis de datos universitarios")
# Cargar datos
# Asegúrate de que el archivo esté en el mismo directorio o ajusta la ruta
archivo = "datos_universitarios.xlsx"
df = pd.read_excel(archivo)
# FILTRO: Excluir años previos a 2010 si existe la columna 'AÑO INGRESO'
if 'AÑO INGRESO' in df.columns:
    df = df[df['AÑO INGRESO'].astype(int) >= 2010]

# Filtrar filas válidas (sin nulos en las columnas relevantes)
df_filtrado = df.dropna(subset=["EDAD", "DURACION PLAN DE ESTUDIO (SEMESTRES)"])

# Convertir a tipo numérico por si acaso
edades = pd.to_numeric(df_filtrado["EDAD"], errors="coerce")
duracion = pd.to_numeric(df_filtrado["DURACION PLAN DE ESTUDIO (SEMESTRES)"], errors="coerce")

# Gráfico de dispersión
plt.figure(figsize=(8,5))
plt.scatter(edades, duracion, alpha=0.5)
plt.title("Relación entre edad y duración de la carrera")
plt.xlabel("Edad de la persona")
plt.ylabel("Duración de la carrera (semestres)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Correlación
correlacion = edades.corr(duracion)
print("*" * 70);
print(f"Correlación entre edad y duración de la carrera: {correlacion:.2f}")

# Correlación entre edad y valor arancel
if "VALOR ARANCEL (PESOS)" in df.columns:
    df_filtrado_arancel = df.dropna(subset=["EDAD", "VALOR ARANCEL (PESOS)"])
    edades_arancel = pd.to_numeric(df_filtrado_arancel["EDAD"], errors="coerce")
    arancel = pd.to_numeric(df_filtrado_arancel["VALOR ARANCEL (PESOS)"], errors="coerce")
    correlacion_arancel = edades_arancel.corr(arancel)
    print(f"Correlación entre edad y valor del arancel: {correlacion_arancel:.2f}")
else:
    print("No existe la columna 'VALOR ARANCEL (PESOS)' en el archivo.")

# --- Matriz de correlación entre todos los campos numéricos ---
# Seleccionar solo columnas numéricas relevantes
campos_numericos = [
    "EDAD",
    "DURACION PLAN DE ESTUDIO (SEMESTRES)",
    "DURACION PROCESO TITULACION (SEMESTRES)",
    "DURACION TOTAL CARRERA (SEMESTRES)",
    "VALOR MATRICULA (PESOS)",
    "VALOR ARANCEL (PESOS)",
    "AÑOS DE ACREDITACION"
]

# Filtrar solo las columnas que existan en el archivo
campos_existentes = [col for col in campos_numericos if col in df.columns]
# Forzar inclusión de todas las columnas, aunque tengan solo nulos
for col in campos_numericos:
    if col not in df.columns:
        df[col] = pd.NA
df_numerico = df[campos_numericos].apply(pd.to_numeric, errors="coerce")

# Calcular matriz de correlación
matriz_corr = df_numerico.corr()
print("\nMatriz de correlación entre campos numéricos:")
print(matriz_corr)

# --- Gráfico de correlaciones (heatmap) ---
import seaborn as sns
import matplotlib.pyplot as plt
# Crear máscara para eliminar la mitad superior
import numpy as np
mask = np.triu(np.ones_like(matriz_corr, dtype=bool), k=1)
plt.figure(figsize=(10,8))
sns.heatmap(matriz_corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, mask=mask)
plt.title("Mapa de calor de correlaciones entre campos numéricos (solo mitad inferior)")
plt.tight_layout()
plt.show()

# Mostrar las correlaciones más fuertes (mayor a 0.5 o menor a -0.5, excluyendo la diagonal)
print("\nCorrelaciones fuertes (>|0.5|):")
ya_mostradas = set()
for i, col1 in enumerate(matriz_corr.columns):
    for j, col2 in enumerate(matriz_corr.columns):
        if col1 != col2 and (col2, col1) not in ya_mostradas and j > i:
            corr_val = matriz_corr.loc[col1, col2]
            if abs(corr_val) > 0.5:
                print(f"{col1} vs {col2}: {corr_val:.2f}")
                ya_mostradas.add((col1, col2))

print("\n--- Análisis de cruces de campos interesantes ---")

# 1. Duración de la carrera vs. Tipo de institución
if "DURACION PLAN DE ESTUDIO (SEMESTRES)" in df.columns and "TIPO DE INSTITUCION" in df.columns:
    print("\nDuración promedio de la carrera por tipo de institución:")
    promedios = df.groupby("TIPO DE INSTITUCION")["DURACION PLAN DE ESTUDIO (SEMESTRES)"].mean().round(1)
    print(promedios)
    # Gráfico de barras
    plt.figure()
    promedios.plot(kind='bar', color='skyblue')
    plt.title('Duración promedio de la carrera por tipo de institución')
    plt.ylabel('Duración (semestres)')
    plt.xlabel('Tipo de institución')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# 2. Valor arancel vs. Área de conocimiento
if "VALOR ARANCEL (PESOS)" in df.columns and "AREA CONOCIMIENTO" in df.columns:
    print("\nValor arancel promedio por área de conocimiento:")
    promedios = df.groupby("AREA CONOCIMIENTO")["VALOR ARANCEL (PESOS)"].mean().round(1)
    print(promedios)
    # Gráfico de barras
    plt.figure()
    promedios.plot(kind='bar', color='orange')
    plt.title('Valor arancel promedio por área de conocimiento')
    plt.ylabel('Valor arancel (pesos)')
    plt.xlabel('Área de conocimiento')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# 3. Edad vs. Modalidad
if "EDAD" in df.columns and "MODALIDAD" in df.columns:
    print("\nEdad promedio por modalidad:")
    promedios = df.groupby("MODALIDAD")["EDAD"].mean().round(1)
    print(promedios)
    # Gráfico de barras
    plt.figure()
    promedios.plot(kind='bar', color='green')
    plt.title('Edad promedio por modalidad')
    plt.ylabel('Edad promedio')
    plt.xlabel('Modalidad')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# 4. Duración total carrera vs. Región/Comuna de sede
if "DURACION TOTAL CARRERA (SEMESTRES)" in df.columns and "COMUNA SEDE" in df.columns:
    print("\nDuración total de carrera promedio por comuna de sede (top 10):")
    promedios = df.groupby("COMUNA SEDE")["DURACION TOTAL CARRERA (SEMESTRES)"].mean().round(1).sort_values(ascending=False).head(10)
    print(promedios)
    # Gráfico de barras
    plt.figure()
    promedios.plot(kind='bar', color='purple')
    plt.title('Duración total de carrera promedio por comuna de sede (top 10)')
    plt.ylabel('Duración total (semestres)')
    plt.xlabel('Comuna de sede')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# 5. Género vs. Área de conocimiento
if "GENERO" in df.columns and "AREA CONOCIMIENTO" in df.columns:
    print("\nDistribución de género por área de conocimiento:")
    print(df.groupby(["AREA CONOCIMIENTO", "GENERO"]).size().unstack(fill_value=0))
    # Gráfico de barras apiladas
    tabla = df.groupby(["AREA CONOCIMIENTO", "GENERO"]).size().unstack(fill_value=0)
    if tabla.shape[0] == 0 or tabla.shape[1] == 0:
        print("⚠️ No hay datos suficientes para mostrar el gráfico de distribución de género por área de conocimiento.")
    else:
        plt.figure()
        tabla.plot(kind='bar', stacked=True)
        plt.title('Distribución de género por área de conocimiento')
        plt.ylabel('Cantidad de estudiantes')
        plt.xlabel('Área de conocimiento')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

# 6. Año de ingreso vs. Valor matrícula/arancel
if "AÑO INGRESO" in df.columns and "VALOR ARANCEL (PESOS)" in df.columns:
    print("\nValor arancel promedio por año de ingreso:")
    promedios = df.groupby("AÑO INGRESO")["VALOR ARANCEL (PESOS)"].mean().round(1)
    print(promedios)
    # Gráfico de línea
    plt.figure()
    promedios.plot(kind='line', marker='o', color='red')
    plt.title('Valor arancel promedio por año de ingreso')
    plt.ylabel('Valor arancel (pesos)')
    plt.xlabel('Año de ingreso')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# 7. Duración plan de estudio vs. Nivel de estudio carrera
if "DURACION PLAN DE ESTUDIO (SEMESTRES)" in df.columns and "NIVEL DE ESTUDIO CARRERA" in df.columns:
    print("\nDuración promedio del plan de estudio por nivel de estudio de la carrera:")
    promedios = df.groupby("NIVEL DE ESTUDIO CARRERA")["DURACION PLAN DE ESTUDIO (SEMESTRES)"].mean().round(1)
    print(promedios)
    # Gráfico de barras
    plt.figure()
    promedios.plot(kind='bar', color='teal')
    plt.title('Duración promedio del plan de estudio por nivel de estudio')
    plt.ylabel('Duración (semestres)')
    plt.xlabel('Nivel de estudio')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# 8. Duración total carrera vs. Años de acreditación
if "DURACION TOTAL CARRERA (SEMESTRES)" in df.columns and "AÑOS DE ACREDITACION" in df.columns:
    print("\nCorrelación entre duración total de la carrera y años de acreditación:")
    duracion = pd.to_numeric(df["DURACION TOTAL CARRERA (SEMESTRES)"], errors="coerce")
    acreditacion = pd.to_numeric(df["AÑOS DE ACREDITACION"], errors="coerce")
    print(duracion.corr(acreditacion))

# 9. Edad vs. Requisito de ingreso
if "EDAD" in df.columns and "REQUISITO INGRESO" in df.columns:
    print("\nEdad promedio por requisito de ingreso:")
    promedios = df.groupby("REQUISITO INGRESO")["EDAD"].mean().round(1)
    print(promedios)
    # Gráfico de barras
    plt.figure()
    promedios.plot(kind='bar', color='brown')
    plt.title('Edad promedio por requisito de ingreso')
    plt.ylabel('Edad promedio')
    plt.xlabel('Requisito de ingreso')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# 10. Duración plan de estudio vs. Jornada
if "DURACION PLAN DE ESTUDIO (SEMESTRES)" in df.columns and "JORNADA" in df.columns:
    print("\nDuración promedio del plan de estudio por jornada:")
    promedios = df.groupby("JORNADA")["DURACION PLAN DE ESTUDIO (SEMESTRES)"].mean().round(1)
    print(promedios)
    # Gráfico de barras
    plt.figure()
    promedios.plot(kind='bar', color='gray')
    plt.title('Duración promedio del plan de estudio por jornada')
    plt.ylabel('Duración (semestres)')
    plt.xlabel('Jornada')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

print("\n--- Cruces de información entre 3 o más campos ---")

# 1. Promedio de duración de carrera por género y tipo de institución
if all(col in df.columns for col in ["DURACION PLAN DE ESTUDIO (SEMESTRES)", "GENERO", "TIPO DE INSTITUCION"]):
    print("\nDuración promedio de la carrera por género y tipo de institución:")
    promedios = df.groupby(["GENERO", "TIPO DE INSTITUCION"])["DURACION PLAN DE ESTUDIO (SEMESTRES)"].mean().round(1)
    print(promedios)

# 2. Valor arancel promedio por área de conocimiento y modalidad
if all(col in df.columns for col in ["VALOR ARANCEL (PESOS)", "AREA CONOCIMIENTO", "MODALIDAD"]):
    print("\nValor arancel promedio por área de conocimiento y modalidad:")
    promedios = df.groupby(["AREA CONOCIMIENTO", "MODALIDAD"])["VALOR ARANCEL (PESOS)"].mean().round(1)
    print(promedios)

# 3. Edad promedio por jornada y requisito de ingreso
if all(col in df.columns for col in ["EDAD", "JORNADA", "REQUISITO INGRESO"]):
    print("\nEdad promedio por jornada y requisito de ingreso:")
    promedios = df.groupby(["JORNADA", "REQUISITO INGRESO"])["EDAD"].mean().round(1)
    print(promedios)

# 4. Duración total carrera promedio por comuna, tipo de institución y área de conocimiento (top 10)
if all(col in df.columns for col in ["DURACION TOTAL CARRERA (SEMESTRES)", "COMUNA SEDE", "TIPO DE INSTITUCION", "AREA CONOCIMIENTO"]):
    print("\nDuración total de carrera promedio por comuna, tipo de institución y área de conocimiento (top 10):")
    promedios = df.groupby(["COMUNA SEDE", "TIPO DE INSTITUCION", "AREA CONOCIMIENTO"])["DURACION TOTAL CARRERA (SEMESTRES)"].mean().round(1).sort_values(ascending=False).head(10)
    print(promedios)

# 5. Cantidad de estudiantes por año de ingreso, género y área de conocimiento
if all(col in df.columns for col in ["AÑO INGRESO", "GENERO", "AREA CONOCIMIENTO"]):
    print("\nCantidad de estudiantes por año de ingreso, género y área de conocimiento (top 10):")
    top10 = df.groupby(["AÑO INGRESO", "GENERO", "AREA CONOCIMIENTO"]).size().sort_values(ascending=False).head(10)
    print(top10)
    # Gráfico de barras
    if not top10.empty:
        plt.figure()
        top10.plot(kind='bar', color='navy')
        plt.title('Cantidad de estudiantes por año, género y área de conocimiento (top 10)')
        plt.ylabel('Cantidad de estudiantes')
        plt.xlabel('Año, Género, Área de conocimiento')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
