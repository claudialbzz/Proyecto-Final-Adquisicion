"""
Parte 3: Cruzado de los datos de ambas fuentes
=============================================
Requisitos según el enunciado:
1. Un único DataFrame donde cada fila = resultado de un piloto en una carrera
2. Todas las columnas de resultados (Parte 1) + todas las columnas de pitstops (Parte 2)
3. Columnas adicionales: "Season" y "RaceNumber"
4. Exportar a CSV
"""

import os
import pandas as pd
import glob
from pathlib import Path
import json

def get_season_calendar(season):
    """
    Devuelve el calendario de carreras para una temporada específica.
    Esto es necesario para asignar RaceNumber correctamente.
    Basado en calendarios reales de F1.
    """
    calendars = {
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
    
    return calendars.get(season, [])

def find_race_number(season, race_filename, calendar):
    """
    Encuentra el número de carrera (RaceNumber) basado en el calendario.
    """
    # Normalizar nombre de archivo
    race_name = Path(race_filename).stem
    
    # Casos especiales
    special_names = {
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
        'Sakhir_Grand_Prix': 'Sakhir'
    }
    
    # Verificar casos especiales primero
    for special, normalized in special_names.items():
        if special in race_name:
            race_key = normalized
            break
    else:
        # Extraer nombre base (sin _Grand_Prix)
        race_key = race_name.replace('_Grand_Prix', '')
    
    # Buscar en el calendario
    for i, calendar_race in enumerate(calendar, 1):
        if calendar_race.lower() in race_key.lower() or race_key.lower() in calendar_race.lower():
            return i
    
    # Si no se encuentra, devolver None
    return None

def get_driver_number_column(df):
    """
    Encuentra la columna que contiene el número de piloto.
    """
    possible_cols = ['No', 'No.', 'Number', 'Driver Number', 'Num', 'Car number']
    
    for col in possible_cols:
        if col in df.columns:
            return col
    
    return None

def create_driver_mapping():
    """
    Crea un mapeo para resolver inconsistencias en números de piloto.
    """
    return {
        # Mapeo por driverId
        'max_verstappen': '33',
        'lewis_hamilton': '44',
        'valtteri_bottas': '77',
        'carlos_sainz': '55',
        'charles_leclerc': '16',
        'lando_norris': '4',
        'george_russell': '63',
        'fernando_alonso': '14',
        'esteban_ocon': '31',
        'pierre_gasly': '10',
        'yuki_tsunoda': '22',
        'daniel_ricciardo': '3',
        'kevin_magnussen': '20',
        'mick_schumacher': '47',
        'sebastian_vettel': '5',
        'lance_stroll': '18',
        'nicholas_latifi': '6',
        'alexander_albon': '23',
        'sergio_perez': '11',
        'kimi_raikkonen': '7',
        'antonio_giovinazzi': '99',
        'nyck_de_vries': '21',
        'logan_sargeant': '2',
        'nico_hulkenberg': '27',
        'guanyu_zhou': '24',
        'oscar_piastri': '81',
    }

def merge_race_data(season, race_number, race_filename, calendar):
    """
    Fusiona datos de una carrera específica.
    """
    # Cargar resultados
    results_path = f"data/{season}/{race_filename}"
    
    if not os.path.exists(results_path):
        return None
    
    results_df = pd.read_csv(results_path)
    
    if results_df.empty:
        return None
    
    # Añadir columnas requeridas
    results_df = results_df.copy()
    results_df['Season'] = season
    results_df['RaceNumber'] = race_number
    results_df['RaceName'] = race_filename.replace('.csv', '')
    
    # Buscar columna de número de piloto
    driver_num_col = get_driver_number_column(results_df)
    
    # Inicializar columnas de pitstops
    pitstop_cols = ['DriverId', 'DriverNumber', 'NPitstops', 'MedianPitStopDuration']
    for col in pitstop_cols:
        results_df[col] = pd.NA
    
    # Cargar datos de pitstops si existen (solo para 2019-2024)
    if season >= 2019:
        pitstop_path = f"data/pitstops/{season}/{season}_round{race_number:02d}_pitstops.csv"
        
        if os.path.exists(pitstop_path):
            pitstops_df = pd.read_csv(pitstop_path)
            
            if not pitstops_df.empty and driver_num_col:
                # Aplicar mapeo de corrección si es necesario
                driver_mapping = create_driver_mapping()
                
                # Crear columna con número corregido
                pitstops_df['CorrectedNumber'] = pitstops_df['DriverId'].map(
                    lambda x: driver_mapping.get(x, str(pitstops_df.loc[pitstops_df['DriverId'] == x, 'DriverNumber'].iloc[0]))
                    if x in pitstops_df['DriverId'].values else pd.NA
                )
                
                # Convertir a string para comparación
                results_df[driver_num_col] = results_df[driver_num_col].astype(str)
                pitstops_df['CorrectedNumber'] = pitstops_df['CorrectedNumber'].astype(str)
                
                # Realizar merge
                merged_df = pd.merge(
                    results_df,
                    pitstops_df[['CorrectedNumber', 'DriverId', 'NPitstops', 'MedianPitStopDuration']],
                    left_on=driver_num_col,
                    right_on='CorrectedNumber',
                    how='left'
                )
                
                # Eliminar columna temporal
                merged_df = merged_df.drop(columns=['CorrectedNumber'], errors='ignore')
                
                return merged_df
    
    return results_df

def merge_all_data():
    """
    Función principal que fusiona todos los datos.
    """
    print("="*70)
    print("PARTE 3: CRUZADO DE DATOS DE RESULTADOS Y PITSTOPS")
    print("="*70)
    
    all_merged = []
    
    # Procesar cada temporada
    for season in range(2012, 2025):
        print(f"\n Procesando temporada {season}...")
        
        # Obtener calendario
        calendar = get_season_calendar(season)
        if not calendar:
            print(f"    No hay calendario definido para {season}")
            continue
        
        # Buscar archivos de resultados
        results_dir = f"data/{season}"
        if not os.path.exists(results_dir):
            print(f"    No hay datos de resultados para {season}")
            continue
        
        result_files = sorted(glob.glob(os.path.join(results_dir, "*.csv")))
        print(f"   {len(result_files)} carreras encontradas")
        
        # Procesar cada carrera
        for race_file in result_files:
            race_filename = os.path.basename(race_file)
            
            # Determinar número de carrera
            race_number = find_race_number(season, race_filename, calendar)
            
            if race_number is None:
                print(f"    No se pudo determinar RaceNumber para: {race_filename}")
                continue
            
            # Fusionar datos
            merged_df = merge_race_data(season, race_number, race_filename, calendar)
            
            if merged_df is not None:
                all_merged.append(merged_df)
                print(f"     {race_filename}: {len(merged_df)} filas")
    
    # Combinar todos los DataFrames
    if not all_merged:
        print("\n No se pudieron fusionar datos")
        return None
    
    print(f"\n{'='*70}")
    print("COMBINANDO DATOS DE TODAS LAS TEMPORADAS...")
    
    final_df = pd.concat(all_merged, ignore_index=True)
    
    # Reordenar columnas: Season y RaceNumber primero
    col_order = ['Season', 'RaceNumber', 'RaceName']
    remaining_cols = [col for col in final_df.columns if col not in col_order]
    final_df = final_df[col_order + remaining_cols]
    
    # Exportar a CSV
    os.makedirs("merged_data", exist_ok=True)
    output_file = "merged_data/f1_complete_dataset.csv"
    final_df.to_csv(output_file, index=False)
    
    # Crear metadatos
    create_metadata(final_df, output_file)
    
    # Mostrar estadísticas
    print_stats(final_df, output_file)
    
    return final_df

def create_metadata(df, output_path):
    """Crea archivo de metadatos."""
    metadata = {
        "dataset": "Formula 1 Complete Dataset 2012-2024",
        "description": "Dataset fusionado de resultados de carreras y pitstops",
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "season_range": f"{int(df['Season'].min())}-{int(df['Season'].max())}",
        "unique_seasons": sorted([int(s) for s in df['Season'].unique()]),
        "unique_races": int(df['RaceName'].nunique()),
        "columns": list(df.columns),
        "pitstops_available_from": 2019,
        "generated_date": pd.Timestamp.now().isoformat()
    }
    
    metadata_file = output_path.replace('.csv', '_metadata.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"   Metadatos guardados en: {metadata_file}")

def print_stats(df, output_path):
    """Muestra estadísticas del dataset."""
    print(f"\n DATASET FINAL CREADO:")
    print(f"    Archivo: {output_path}")
    print(f"    Total filas: {len(df):,}")
    print(f"    Total columnas: {len(df.columns)}")
    
    print(f"\n DISTRIBUCIÓN POR TEMPORADA:")
    season_counts = df['Season'].value_counts().sort_index()
    for season, count in season_counts.items():
        if season >= 2019:
            pitstops_count = df[df['Season'] == season]['NPitstops'].notna().sum()
            print(f"   {int(season)}: {count:>4} filas | Pitstops: {pitstops_count:>4} ({pitstops_count/count*100:>5.1f}%)")
        else:
            print(f"   {int(season)}: {count:>4} filas | Sin datos de pitstops")
    
    print(f"\n COLUMNAS DE PITSTOPS:")
    pitstop_cols = ['DriverId', 'DriverNumber', 'NPitstops', 'MedianPitStopDuration']
    for col in pitstop_cols:
        if col in df.columns:
            non_null = df[col].notna().sum()
            print(f"   {col}: {non_null:>6} no nulos ({non_null/len(df)*100:>5.1f}%)")

def validate_requirements(df):
    """Valida que se cumplan los requisitos del punto 3."""
    print(f"\n{'='*70}")
    print("VALIDACIÓN DE REQUISITOS (Punto 3)")
    print(f"{'='*70}")
    
    requirements = [
        ("1. DataFrame único creado", df is not None),
        ("2. Columnas Season y RaceNumber presentes", 
         all(col in df.columns for col in ['Season', 'RaceNumber'])),
        ("3. Season no contiene valores nulos", df['Season'].notna().all()),
        ("4. RaceNumber no contiene valores nulos", df['RaceNumber'].notna().all()),
        ("5. Contiene columnas de resultados", any(col in df.columns for col in ['Driver', 'Constructor', 'Laps'])),
        ("6. Contiene columnas de pitstops", all(col in df.columns for col in ['DriverId', 'DriverNumber', 'NPitstops', 'MedianPitStopDuration'])),
        ("7. Exportado a CSV", os.path.exists("merged_data/f1_complete_dataset.csv")),
    ]
    
    all_passed = True
    for req_name, condition in requirements:
        status = "OK" if condition else "ERROR"
        print(f"  {status} {req_name}")
        if not condition:
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    # Ejecutar la fusión
    dataset = merge_all_data()
    
    if dataset is not None:
        # Validar requisitos
        requirements_met = validate_requirements(dataset)
        
        # Mostrar ejemplo
        print(f"\n{'='*70}")
        print("EJEMPLO DEL DATASET (primeras 5 filas):")
        print(f"{'='*70}")
        
        # Seleccionar columnas representativas
        sample_cols = ['Season', 'RaceNumber', 'RaceName', 'Driver', 'Constructor', 
                      'NPitstops', 'MedianPitStopDuration']
        available_cols = [col for col in sample_cols if col in dataset.columns]
        
        if available_cols:
            print(dataset[available_cols].head().to_string())
        
        
        if requirements_met:
            print(" Todos los requisitos del punto 3 cumplidos")
        else:
            print("  Algunos requisitos no se cumplen completamente")
        
        print(f"\n El dataset está listo para el análisis de la Parte 4")
        print(f" Ubicación: merged_data/f1_complete_dataset.csv")
    else:
        print("\n Error: No se pudo crear el dataset")