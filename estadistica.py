import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from openpyxl import load_workbook
import numpy as np

# Configurar el estilo de los gráficos
plt.style.use('default')
sns.set_palette("husl")

def analizar_genero_carreras(archivo_excel):
    """
    Analiza la relación entre el género y las carreras/áreas de conocimiento
    """
    try:
        # Cargar el archivo Excel
        df = pd.read_excel(archivo_excel)
        
        print("✅ Archivo cargado exitosamente")
        print(f"📊 Total de registros: {len(df)}")
        print("\n📋 Columnas disponibles:")
        print(df.columns.tolist())
        
        # Verificar que exista la columna GENERO
        if 'GENERO' not in df.columns:
            print("❌ No se encuentra la columna 'GENERO'")
            print("Columnas disponibles:", df.columns.tolist())
            return
        
        # Limpiar y estandarizar los datos de género
        df['GENERO'] = df['GENERO'].str.upper().str.strip()
        # FILTRO: Excluir años previos a 2010
        if 'AÑO INGRESO' in df.columns:
            df = df[df['AÑO INGRESO'].astype(int) >= 2010]
        # FILTRO: Excluir carreras con menos de 15 matrículas por año
        nombre_carrera_col = 'NOMBRE CARRERA' if 'NOMBRE CARRERA' in df.columns else 'CARRERA'
        if nombre_carrera_col in df.columns and 'AÑO INGRESO' in df.columns:
            conteo_carreras = df.groupby(['AÑO INGRESO', nombre_carrera_col]).size().reset_index(name='matriculas')
            carreras_validas = conteo_carreras[conteo_carreras['matriculas'] >= 15][['AÑO INGRESO', nombre_carrera_col]]
            df = df.merge(carreras_validas, on=['AÑO INGRESO', nombre_carrera_col], how='inner')
        # Contar distribución por género
        distribucion_genero = df['GENERO'].value_counts()
        print(f"\n👥 Distribución por género:")
        for genero, cantidad in distribucion_genero.items():
            porcentaje = (cantidad / len(df)) * 100
            print(f"   {genero}: {cantidad} ({porcentaje:.1f}%)")
        
        # Análisis 1: Carreras con mayor presencia femenina
        print("\n" + "="*60)
        print("🎓 CARRERAS CON MAYOR PRESENCIA FEMENINA")
        print("="*60)
        
        if 'NOMBRE CARRERA' in df.columns:
            analizar_por_categoria(df, 'NOMBRE CARRERA', 'Carrera')
        
        # Análisis 2: Áreas de conocimiento con mayor presencia femenina
        print("\n" + "="*60)
        print("📚 ÁREAS DE CONOCIMIENTO CON MAYOR PRESENCIA FEMENINA")
        print("="*60)
        
        if 'AREA CONOCIMIENTO' in df.columns:
            analizar_por_categoria(df, 'AREA CONOCIMIENTO', 'Área de conocimiento')
        
        # Análisis 3: Evolución temporal por año de ingreso
        if 'AÑO INGRESO' in df.columns:
            analizar_evolucion_temporal(df)
        
        # Análisis 4: Por tipo de institución
        if 'TIPO DE INSTITUCION' in df.columns:
            analizar_por_tipo_institucion(df)
            
        # Generar gráficos
        generar_graficos(df)
        
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")

def analizar_por_categoria(df, columna_categoria, nombre_categoria):
    """
    Analiza la distribución de género por categoría específica
    """
    # Filtrar solo mujeres
    mujeres_df = df[df['GENERO'].str.contains('FEMENINO|MUJER|F', na=False, case=False)]
    
    # Contar por categoría
    conteo_categorias = mujeres_df[columna_categoria].value_counts().head(10)
    
    print(f"\nTop 10 {nombre_categoria.lower()}s con más mujeres:")
    for i, (categoria, cantidad) in enumerate(conteo_categorias.items(), 1):
        total_categoria = df[df[columna_categoria] == categoria].shape[0]
        porcentaje_mujeres = (cantidad / total_categoria * 100) if total_categoria > 0 else 0
        print(f"{i:2d}. {categoria}: {cantidad} mujeres ({porcentaje_mujeres:.1f}% del total)")
    
    return conteo_categorias

def analizar_evolucion_temporal(df):
    """
    Analiza la evolución de la matrícula femenina por año
    """
    print("\n" + "="*60)
    print("📈 EVOLUCIÓN TEMPORAL DE MATRÍCULA FEMENINA")
    print("="*60)
    
    # Agrupar por año de ingreso
    evolucion = df.groupby('AÑO INGRESO')['GENERO'].apply(
        lambda x: (x.str.contains('FEMENINO|MUJER|F', case=False, na=False).sum() / len(x)) * 100
    ).reset_index()
    
    evolucion.columns = ['Año', 'Porcentaje_Mujeres']
    evolucion = evolucion.sort_values('Año')
    
    print("Evolución del porcentaje de mujeres por año:")
    for _, row in evolucion.iterrows():
        print(f"  {int(row['Año'])}: {row['Porcentaje_Mujeres']:.1f}%")

def analizar_por_tipo_institucion(df):
    """
    Analiza la distribución por tipo de institución
    """
    print("\n" + "="*60)
    print("🏫 DISTRIBUCIÓN POR TIPO DE INSTITUCIÓN")
    print("="*60)
    
    if 'TIPO DE INSTITUCION' in df.columns:
        distribucion_instituciones = df.groupby('TIPO DE INSTITUCION')['GENERO'].apply(
            lambda x: {
                'Total': len(x),
                'Mujeres': x.str.contains('FEMENINO|MUJER|F', case=False, na=False).sum(),
                'Porcentaje_Mujeres': (x.str.contains('FEMENINO|MUJER|F', case=False, na=False).sum() / len(x)) * 100
            }
        ).reset_index()

        for _, row in distribucion_instituciones.iterrows():
            stats = row['GENERO']
            if isinstance(stats, dict):
                print(f"\n{row['TIPO DE INSTITUCION']}:")
                print(f"  Total estudiantes: {stats['Total']}")
                print(f"  Mujeres: {stats['Mujeres']}")
                print(f"  Porcentaje mujeres: {stats['Porcentaje_Mujeres']:.1f}%")
            else:
                print(f"\n{row['TIPO DE INSTITUCION']}:")
                print(f"  Total estudiantes: {stats}")
                print(f"  Mujeres: -")
                print(f"  Porcentaje mujeres: -")

def generar_graficos(df):
    """
    Genera gráficos para visualizar los resultados
    """
    try:
        # Configurar el tamaño de las figuras
        plt.figure(figsize=(15, 10))
        
        # Gráfico 1: Distribución por género
        plt.subplot(2, 2, 1)
        distribucion_genero = df['GENERO'].value_counts()
        plt.pie(distribucion_genero.values, labels=distribucion_genero.index, autopct='%1.1f%%')
        plt.title('Distribución por Género')
        
        # Gráfico 2: Top carreras con más mujeres
        plt.subplot(2, 2, 2)
        if 'NOMBRE CARRERA' in df.columns:
            mujeres_df = df[df['GENERO'].str.contains('FEMENINO|MUJER|F', na=False, case=False)]
            top_carreras = mujeres_df['NOMBRE CARRERA'].value_counts().head(8)
            plt.barh(range(len(top_carreras)), top_carreras.values)
            plt.yticks(range(len(top_carreras)), top_carreras.index, fontsize=8)
            plt.title('Top 8 Carreras con más Mujeres')
            plt.xlabel('Cantidad de Mujeres')
        
        # Gráfico 3: Distribución por áreas de conocimiento
        plt.subplot(2, 2, 3)
        if 'AREA CONOCIMIENTO' in df.columns:
            areas_mujeres = df[df['GENERO'].str.contains('FEMENINO|MUJER|F', na=False, case=False)]
            areas_dist = areas_mujeres['AREA CONOCIMIENTO'].value_counts().head(6)
            plt.bar(areas_dist.index, areas_dist.values)
            plt.xticks(rotation=45, ha='right')
            plt.title('Mujeres por Área de Conocimiento (Top 6)')
            plt.ylabel('Cantidad de Mujeres')
        
        # Gráfico 4: Evolución temporal
        plt.subplot(2, 2, 4)
        if 'AÑO INGRESO' in df.columns:
            evolucion = df.groupby('AÑO INGRESO')['GENERO'].apply(
                lambda x: (x.str.contains('FEMENINO|MUJER|F', case=False, na=False).sum() / len(x)) * 100
            )
            # Convertir los años a enteros para el eje x
            anos_enteros = evolucion.index.astype(int)
            plt.plot(anos_enteros, evolucion.values, marker='o')
            plt.title('Evolución del % de Mujeres por Año')
            plt.xlabel('Año de Ingreso')
            plt.ylabel('Porcentaje de Mujeres (%)')
            plt.xticks(anos_enteros)
            plt.ylim(0, 100)
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('analisis_genero_carreras.png', dpi=300, bbox_inches='tight')
        print(f"\n📊 Gráficos guardados como 'analisis_genero_carreras.png'")
        
    except Exception as e:
        print(f"⚠️ Error al generar gráficos: {e}")

def analisis_detallado_carreras(df, top_n=5):
    """
    Análisis detallado de las carreras con mayor y menor presencia femenina
    """
    print("\n" + "="*60)
    print("🔍 ANÁLISIS DETALLADO POR CARRERA")
    print("="*60)
    
    if 'NOMBRE CARRERA' in df.columns:
        # Calcular porcentaje de mujeres por carrera
        stats_carreras = df.groupby('NOMBRE CARRERA').agg({
            'GENERO': [
                ('total', 'count'),
                ('mujeres', lambda x: x.str.contains('FEMENINO|MUJER|F', case=False, na=False).sum())
            ]
        }).reset_index()
        
        # Aplanar las columnas multiindex
        stats_carreras.columns = ['Carrera', 'Total', 'Mujeres']
        stats_carreras['Porcentaje_Mujeres'] = (stats_carreras['Mujeres'] / stats_carreras['Total']) * 100
        
        # Carreras con mayor porcentaje de mujeres
        top_femeninas = stats_carreras.nlargest(top_n, 'Porcentaje_Mujeres')
        print(f"\n🏆 Top {top_n} carreras con MAYOR porcentaje de mujeres:")
        for i, (_, row) in enumerate(top_femeninas.iterrows(), 1):
            print(f"{i}. {row['Carrera']}: {row['Porcentaje_Mujeres']:.1f}% ({row['Mujeres']}/{row['Total']})")
        
        # Carreras con menor porcentaje de mujeres
        top_masculinas = stats_carreras.nsmallest(top_n, 'Porcentaje_Mujeres')
        print(f"\n🔧 Top {top_n} carreras con MENOR porcentaje de mujeres:")
        for i, (_, row) in enumerate(top_masculinas.iterrows(), 1):
            print(f"{i}. {row['Carrera']}: {row['Porcentaje_Mujeres']:.1f}% ({row['Mujeres']}/{row['Total']})")

# Ejecutar el análisis
if __name__ == "__main__":
    # Reemplaza con la ruta de tu archivo Excel
    archivo_excel = "datos_universitarios.xlsx"  # Cambia por el nombre de tu archivo
    
    print("🔍 INICIANDO ANÁLISIS DE GÉNERO Y CARRERAS")
    print("="*60)
    
    # Ejecutar análisis principal
    analizar_genero_carreras(archivo_excel)
    
    # Cargar datos para análisis adicional
    try:
        df = pd.read_excel(archivo_excel)
        df['GENERO'] = df['GENERO'].str.upper().str.strip()
        
        # Ejecutar análisis detallado
        analisis_detallado_carreras(df)
        
        print("\n✅ Análisis completado exitosamente!")
        print("\n📁 Resultados disponibles en:")
        print("   - Consola: Resumen estadístico")
        print("   - Archivo: analisis_genero_carreras.png (gráficos)")
        
    except Exception as e:
        print(f"❌ Error en análisis adicional: {e}")