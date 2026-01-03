import os
import pandas as pd
import glob
from pathlib import Path
import re

def create_season_race_order(season):
    """
    Devuelve el orden de carreras para una temporada específica.
    Esto es necesario para mapear nombres de carrera a números de round.
    Basado en el calendario real de F1.
    """
    # Orden de carreras por temporada (basado en calendarios F1 históricos)
    season_calendars = {
        2012: [
            'Australian', 'Malaysian', 'Chinese', 'Bahrain', 'Spanish',
            'Monaco', 'Canadian', 'European', 'British', 'German',
            'Hungarian', 'Belgian', 'Italian', 'Singapore', 'Japanese',
            'Korean', 'Indian', 'Abu_Dhabi', 'United_States', 'Brazilian'
        ],
        2013: [
            'Australian', 'Malaysian', 'Chinese', 'Bahrain', 'Spanish',
            'Monaco', 'Canadian', 'British', 'German', 'Hungarian',
            'Belgian', 'Italian', 'Singapore', 'Korean', 'Japanese',
            'Indian', 'Abu_Dhabi', 'United_States', 'Brazilian'
        ],
        2014: [
            'Australian', 'Malaysian', 'Bahrain', 'Chinese', 'Spanish',
            'Monaco', 'Canadian', 'Austrian', 'British', 'German',
            'Hungarian', 'Belgian', 'Italian', 'Singapore', 'Japanese',
            'Russian', 'United_States', 'Brazilian', 'Abu_Dhabi'
        ],
        2015: [
            'Australian', 'Malaysian', 'Chinese', 'Bahrain', 'Spanish',
            'Monaco', 'Canadian', 'Austrian', 'British', 'Hungarian',
            'Belgian', 'Italian', 'Singapore', 'Japanese', 'Russian',
            'United_States', 'Mexican', 'Brazilian', 'Abu_Dhabi'
        ],
        2016: [
            'Australian', 'Bahrain', 'Chinese', 'Russian', 'Spanish',
            'Monaco', 'Canadian', 'European', 'Austrian', 'British',
            'Hungarian', 'German', 'Belgian', 'Italian', 'Singapore',
            'Malaysian', 'Japanese', 'United_States', 'Mexican', 'Brazilian', 'Abu_Dhabi'
        ],
        2017: [
            'Australian', 'Chinese', 'Bahrain', 'Russian', 'Spanish',
            'Monaco', 'Canadian', 'Azerbaijan', 'Austrian', 'British',
            'Hungarian', 'Belgian', 'Italian', 'Singapore', 'Malaysian',
            'Japanese', 'United_States', 'Mexican', 'Brazilian', 'Abu_Dhabi'
        ],
        2018: [
            'Australian', 'Bahrain', 'Chinese', 'Azerbaijan', 'Spanish',
            'Monaco', 'Canadian', 'French', 'Austrian', 'British',
            'German', 'Hungarian', 'Belgian', 'Italian', 'Singapore',
            'Russian', 'Japanese', 'United_States', 'Mexican', 'Brazilian', 'Abu_Dhabi'
        ],
        2019: [
            'Australian', 'Bahrain', 'Chinese', 'Azerbaijan', 'Spanish',
            'Monaco', 'Canadian', 'French', 'Austrian', 'British',
            'German', 'Hungarian', 'Belgian', 'Italian', 'Singapore',
            'Russian', 'Japanese', 'Mexican', 'United_States', 'Brazilian', 'Abu_Dhabi'
        ],
        2020: [
            'Austrian', 'Styrian', 'Hungarian', 'British', '70th_Anniversary',
            'Spanish', 'Belgian', 'Italian', 'Tuscan', 'Russian',
            'Eifel', 'Portuguese', 'Emilia-Romagna', 'Turkish', 'Bahrain', 'Sakhir', 'Abu_Dhabi'
        ],
        2021: [
            'Bahrain', 'Emilia-Romagna', 'Portuguese', 'Spanish', 'Monaco',
            'Azerbaijan', 'French', 'Styrian', 'Austrian', 'British',
            'Hungarian', 'Belgian', 'Dutch', 'Italian', 'Russian',
            'Turkish', 'United_States', 'Mexico_City', 'São_Paulo', 'Qatar', 'Saudi_Arabian', 'Abu_Dhabi'
        ],
        2022: [
            'Bahrain', 'Saudi_Arabian', 'Australian', 'Emilia-Romagna', 'Miami',
            'Spanish', 'Monaco', 'Azerbaijan', 'Canadian', 'British',
            'Austrian', 'French', 'Hungarian', 'Belgian', 'Dutch',
            'Italian', 'Singapore', 'Japanese', 'United_States', 'Mexico_City', 'São_Paulo', 'Abu_Dhabi'
        ],
        2023: [
            'Bahrain', 'Saudi_Arabian', 'Australian', 'Azerbaijan', 'Miami',
            'Monaco', 'Spanish', 'Canadian', 'Austrian', 'British',
            'Hungarian', 'Belgian', 'Dutch', 'Italian', 'Singapore',
            'Japanese', 'Qatar', 'United_States', 'Mexico_City', 'São_Paulo', 'Las_Vegas', 'Abu_Dhabi'
        ],
        2024: [
            'Bahrain', 'Saudi_Arabian', 'Australian', 'Japanese', 'Chinese',
            'Miami', 'Emilia-Romagna', 'Monaco', 'Canadian', 'Spanish',
            'Austrian', 'British', 'Hungarian', 'Belgian', 'Dutch',
            'Italian', 'Azerbaijan', 'Singapore', 'United_States', 'Mexico_City',
            'São_Paulo', 'Las_Vegas', 'Qatar', 'Abu_Dhabi'
        ]
    }
    
    return season_calendars.get(season, [])

def normalize_race_name(filename):
    """
    Normaliza el nombre del archivo para que coincida con los nombres del calendario.
    """
    # Eliminar extensión y normalizar
    name = Path(filename).stem
    
    # Manejar casos especiales
    special_cases = {
        '70th_Anniversary_Grand_Prix': '70th_Anniversary',
        'Mexico_City_Grand_Prix': 'Mexico_City',
        'São_Paulo_Grand_Prix': 'São_Paulo',
        'Saudi_Arabian_Grand_Prix': 'Saudi_Arabian',
        'Las_Vegas_Grand_Prix': 'Las_Vegas',
        'Styrian_Grand_Prix': 'Styrian',
        'Tuscan_Grand_Prix': 'Tuscan',
        'Eifel_Grand_Prix': 'Eifel',
        'Emilia-Romagna_Grand_Prix': 'Emilia-Romagna',
        'Dutch_Grand_Prix': 'Dutch',
        '70th_Anniversary_Grand_Prix': '70th_Anniversary',
        'Sakhir_Grand_Prix': 'Sakhir'
    }
    
    # Verificar casos especiales primero
    for special_name, normalized in special_cases.items():
        if special_name in name:
            return normalized
    
    # Patrón general: Extraer el nombre principal antes de "_Grand_Prix"
    match = re.match(r'(.+)_Grand_Prix', name)
    if match:
        return match.group(1)
    
    return name

def find_race_number(season, race_name, race_order):
    """
    Encuentra el número de carrera (round) basado en el orden de la temporada.
    """
    normalized_name = normalize_race_name(race_name)
    
    # Buscar en el orden de carreras
    for i, race in enumerate(race_order, 1):
        if race.lower() in normalized_name.lower() or normalized_name.lower() in race.lower():
            return i
    
    # Si no se encuentra, intentar con aproximaciones
    for i, race in enumerate(race_order, 1):
        # Eliminar guiones y underscores para comparación
        race_simple = race.replace('-', '').replace('_', '').lower()
        name_simple = normalized_name.replace('-', '').replace('_', '').lower()
        
        if race_simple in name_simple or name_simple in race_simple:
            return i
    
    print(f"    No se pudo encontrar round para: {race_name} (normalizado: {normalized_name})")
    return None

def merge_race_data(season, results_dir="data", pitstops_dir="data/pitstops"):
    """
    Fusiona los datos de resultados y pitstops para una temporada específica.
    """
    # Obtener orden de carreras para esta temporada
    race_order = create_season_race_order(season)
    
    if not race_order:
        print(f"  No hay calendario definido para la temporada {season}")
        return pd.DataFrame()
    
    # Lista para almacenar todos los DataFrames fusionados
    all_merged_dfs = []
    
    # Directorio de resultados para esta temporada
    results_season_dir = os.path.join(results_dir, str(season))
    
    if not os.path.exists(results_season_dir):
        print(f"⚠️  No existe directorio de resultados para {season}")
        return pd.DataFrame()
    
    # Obtener todos los archivos CSV de resultados
    result_files = sorted(glob.glob(os.path.join(results_season_dir, "*.csv")))
    
    print(f"🔍 Procesando temporada {season} ({len(result_files)} carreras encontradas)")
    
    for result_file in result_files:
        # Extraer nombre de la carrera del archivo
        race_filename = os.path.basename(result_file)
        
        # Determinar round number
        round_num = find_race_number(season, race_filename, race_order)
        
        if round_num is None:
            print(f"  ⏭️  Saltando {race_filename} - no se pudo determinar round")
            continue
        
        # Cargar datos de resultados
        try:
            results_df = pd.read_csv(result_file)
            
            if results_df.empty:
                print(f"  ⚠️  Archivo vacío: {race_filename}")
                continue
                
            # Añadir columnas de identificación
            results_df['Season'] = season
            results_df['RaceNumber'] = round_num
            results_df['RaceName'] = race_filename.replace('.csv', '')
            
            # Verificar columnas existentes
            print(f"  📊 {race_filename}: {len(results_df)} filas, {len(results_df.columns)} columnas")
            
        except Exception as e:
            print(f"  ❌ Error cargando {race_filename}: {e}")
            continue
        
        # Columnas base para pitstops (todas como NaN inicialmente)
        pitstop_columns = ['DriverId', 'DriverNumber', 'NPitstops', 'MedianPitStopDuration']
        
        # Verificar si tenemos datos de pitstops para esta temporada
        if season >= 2019:
            # Para 2019-2024: cargar datos reales de pitstops
            pitstop_file = os.path.join(pitstops_dir, str(season), f"{season}_round{round_num:02d}_pitstops.csv")
            
            if os.path.exists(pitstop_file):
                try:
                    pitstops_df = pd.read_csv(pitstop_file)
                    
                    # Asegurar que tenga las columnas necesarias
                    for col in pitstop_columns:
                        if col not in pitstops_df.columns:
                            pitstops_df[col] = pd.NA
                    
                    print(f"    ✅ Pitstops encontrados: {len(pitstops_df)} registros")
                    
                except Exception as e:
                    print(f"    ❌ Error cargando pitstops: {e}")
                    pitstops_df = pd.DataFrame(columns=pitstop_columns)
            else:
                print(f"    ⚠️  No hay archivo de pitstops para round {round_num}")
                pitstops_df = pd.DataFrame(columns=pitstop_columns)
        else:
            # Para 2012-2018: no hay datos de pitstops, crear DataFrame vacío
            print(f"    📝 Sin datos de pitstops (año {season} < 2019)")
            pitstops_df = pd.DataFrame(columns=pitstop_columns)
        
        # Encontrar columna de número de piloto en resultados
        driver_number_col = None
        possible_cols = ['No', 'Driver Number', 'Number', 'Car number', 'Num', 'Car', 'Driver']
        
        for col in possible_cols:
            if col in results_df.columns:
                driver_number_col = col
                break
        
        if driver_number_col is None:
            print(f"  ⚠️  No se encontró columna de número de piloto en {race_filename}")
            # Listar columnas disponibles para depuración
            print(f"    Columnas disponibles: {list(results_df.columns)}")
            
            # Crear columna temporal si no existe
            results_df['Temp_Driver_Number'] = range(1, len(results_df) + 1)
            driver_number_col = 'Temp_Driver_Number'
        
        # Convertir a string para facilitar el merge
        results_df[driver_number_col] = results_df[driver_number_col].astype(str)
        
        if not pitstops_df.empty and 'DriverNumber' in pitstops_df.columns:
            pitstops_df['DriverNumber'] = pitstops_df['DriverNumber'].astype(str)
            
            # Realizar el merge
            merged_df = pd.merge(
                results_df,
                pitstops_df,
                left_on=driver_number_col,
                right_on='DriverNumber',
                how='left'  # LEFT JOIN: mantener todos los resultados
            )
        else:
            # Si no hay pitstops, añadir columnas vacías
            merged_df = results_df.copy()
            for col in pitstop_columns:
                if col not in merged_df.columns:
                    merged_df[col] = pd.NA
        
        # Limpiar columnas temporales
        if 'Temp_Driver_Number' in merged_df.columns:
            merged_df = merged_df.drop(columns=['Temp_Driver_Number'])
        
        all_merged_dfs.append(merged_df)
    
    if all_merged_dfs:
        final_df = pd.concat(all_merged_dfs, ignore_index=True)
        print(f"  ✅ Temporada {season}: {len(final_df)} filas fusionadas")
        return final_df
    else:
        print(f"  ⚠️  Temporada {season}: No se pudieron fusionar datos")
        return pd.DataFrame()

def merge_all_seasons(start_year=2012, end_year=2024):
    """
    Fusiona datos de todas las temporadas desde start_year hasta end_year.
    """
    all_seasons_data = []
    
    print("=" * 60)
    print(" INICIANDO FUSIÓN DE DATOS F1")
    print(f" Rango: {start_year} - {end_year}")
    print("=" * 60)
    
    for year in range(start_year, end_year + 1):
        season_data = merge_race_data(year)
        
        if not season_data.empty:
            all_seasons_data.append(season_data)
        else:
            print(f"  Saltando temporada {year} - sin datos")
    
    if all_seasons_data:
        # Combinar todos los DataFrames
        final_df = pd.concat(all_seasons_data, ignore_index=True)
        
        # Reordenar columnas para mejor presentación
        column_order = ['Season', 'RaceNumber', 'RaceName'] + \
                      [col for col in final_df.columns if col not in ['Season', 'RaceNumber', 'RaceName']]
        final_df = final_df[column_order]
        
        # Crear directorio para datos fusionados
        os.makedirs("merged_data", exist_ok=True)
        
        # Guardar el DataFrame completo
        output_file = f"merged_data/f1_merged_{start_year}_{end_year}.csv"
        final_df.to_csv(output_file, index=False)
        
        # También guardar por separado por si acaso
        for year in range(start_year, end_year + 1):
            year_data = final_df[final_df['Season'] == year]
            if not year_data.empty:
                year_data.to_csv(f"merged_data/f1_{year}.csv", index=False)
        
        print("\n" + "=" * 60)
        print(" FUSIÓN COMPLETADA")
        print("=" * 60)
        
        # Mostrar estadísticas
        print(f"\n ESTADÍSTICAS DEL DATASET FUSIONADO:")
        print(f"   Total de filas: {len(final_df):,}")
        print(f"   Total de columnas: {len(final_df.columns)}")
        print(f"   Temporadas incluidas: {sorted(final_df['Season'].unique())}")
        
        # Contar datos de pitstops
        has_pitstops = final_df['NPitstops'].notna().sum()
        print(f"   Filas con datos de pitstops: {has_pitstops:,} ({has_pitstops/len(final_df)*100:.1f}%)")
        
        # Distribución por año
        print(f"\n DISTRIBUCIÓN POR AÑO:")
        year_counts = final_df['Season'].value_counts().sort_index()
        for year, count in year_counts.items():
            pitstops_count = final_df[final_df['Season'] == year]['NPitstops'].notna().sum()
            print(f"   {year}: {count:>4} filas | Pitstops: {pitstops_count:>4} ({pitstops_count/count*100:>5.1f}%)")
        
        print(f"\n Archivo guardado en: {output_file}")
        print(f"   Tamaño aproximado: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
        
        return final_df
    else:
        print(" No se pudieron fusionar datos para ninguna temporada")
        return pd.DataFrame()

def generate_report():
    """
    Genera un reporte de los datos fusionados.
    """
    merged_file = "merged_data/f1_merged_2012_2024.csv"
    
    if os.path.exists(merged_file):
        df = pd.read_csv(merged_file)
        
        print("\n REPORTE DE DATOS FUSIONADOS")
        print("=" * 50)
        
        print("\n1. ESTRUCTURA DEL DATASET:")
        print(f"   • Filas totales: {len(df)}")
        print(f"   • Columnas totales: {len(df.columns)}")
        
        print("\n2. COLUMNAS DISPONIBLES:")
        for i, col in enumerate(df.columns, 1):
            non_null = df[col].notna().sum()
            null_pct = (1 - non_null/len(df)) * 100
            print(f"   {i:2}. {col:<25} ({non_null:>5} no nulos, {null_pct:>5.1f}% nulos)")
        
        print("\n3. RESUMEN POR COLUMNA:")
        for col in ['NPitstops', 'MedianPitStopDuration']:
            if col in df.columns:
                print(f"\n   {col}:")
                print(f"      • Valores no nulos: {df[col].notna().sum()}")
                print(f"      • Promedio: {df[col].mean():.2f}")
                print(f"      • Mínimo: {df[col].min():.2f}")
                print(f"      • Máximo: {df[col].max():.2f}")
        
        # Guardar reporte
        with open("merged_data/report.txt", "w") as f:
            f.write("REPORTE DE DATOS FUSIONADOS F1\n")
            f.write("="*50 + "\n\n")
            f.write(f"Total filas: {len(df)}\n")
            f.write(f"Total columnas: {len(df.columns)}\n\n")
            f.write("Columnas disponibles:\n")
            for col in df.columns:
                f.write(f"  - {col}\n")
        
        print(f"\n Reporte guardado en: merged_data/report.txt")

if __name__ == "__main__":
    # Fusionar datos de 2012 a 2024
    merged_data = merge_all_seasons(2012, 2024)
    
    if not merged_data.empty:
        # Generar reporte
        generate_report()
        
        # Mostrar primeras filas como ejemplo
        print("\n EJEMPLO DE DATOS (primeras 5 filas):")
        print(merged_data.head())
        
        print("\n COLUMNAS DE PITSTOPS (ejemplo):")
        pitstop_cols = ['DriverId', 'DriverNumber', 'NPitstops', 'MedianPitStopDuration']
        if all(col in merged_data.columns for col in pitstop_cols):
            sample = merged_data[['Season', 'RaceName'] + pitstop_cols].head(10)
            print(sample.to_string())