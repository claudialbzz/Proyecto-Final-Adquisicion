# merge_data_part3.py
"""
Parte 3: Cruzado de los datos de ambas fuentes - VERSIÓN CORREGIDA
"""

import os
import pandas as pd
import glob
from pathlib import Path
import json

def clean_column_names(df):
    """Limpia los nombres de las columnas del DataFrame."""
    # Eliminar columnas sin nombre
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Eliminar columnas que son completamente nulas
    df = df.dropna(axis=1, how='all')
    
    # Renombrar columnas problemáticas
    column_renames = {
        'Pos.': 'Position',
        'No.': 'DriverNumber',
        'Grid[43]': 'Grid',
        'Pts.': 'Points',
        'Laps1': 'Laps',
        'Points1': 'Points',
        'Lapsa': 'Laps'
    }
    
    df = df.rename(columns={k: v for k, v in column_renames.items() if k in df.columns})
    
    return df

def remove_duplicate_columns(df):
    """Elimina columnas duplicadas."""
    # Identificar columnas duplicadas por contenido
    cols_to_drop = []
    cols_checked = set()
    
    for i, col1 in enumerate(df.columns):
        if col1 in cols_checked:
            continue
            
        for j, col2 in enumerate(df.columns[i+1:], i+1):
            if col2 in cols_checked:
                continue
                
            # Verificar si las columnas son iguales
            try:
                if df[col1].equals(df[col2]):
                    cols_to_drop.append(col2)
                    cols_checked.add(col2)
            except:
                pass
    
    # Eliminar columnas duplicadas
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
    
    # Eliminar columnas con sufijos _x o _y (mantener solo una versión)
    cols_with_suffix = [col for col in df.columns if col.endswith('_x') or col.endswith('_y')]
    
    for col in cols_with_suffix:
        base_name = col[:-2]  # Eliminar _x o _y
        if base_name in df.columns:
            # Si ya existe la base, eliminar la versión con sufijo
            df = df.drop(columns=[col])
        else:
            # Renombrar eliminando el sufijo
            df = df.rename(columns={col: base_name})
    
    return df

def get_season_calendar(season):
    """Devuelve el calendario de carreras para una temporada específica."""
    calendars = {
        2012: ['Australian', 'Malaysian', 'Chinese', 'Bahrain', 'Spanish', 'Monaco', 
               'Canadian', 'European', 'British', 'German', 'Hungarian', 'Belgian', 
               'Italian', 'Singapore', 'Japanese', 'Korean', 'Indian', 'Abu_Dhabi', 
               'United_States', 'Brazilian'],
        2013: ['Australian', 'Malaysian', 'Chinese', 'Bahrain', 'Spanish', 'Monaco', 
               'Canadian', 'British', 'German', 'Hungarian', 'Belgian', 'Italian', 
               'Singapore', 'Korean', 'Japanese', 'Indian', 'Abu_Dhabi', 'United_States', 
               'Brazilian'],
        2014: ['Australian', 'Malaysian', 'Bahrain', 'Chinese', 'Spanish', 'Monaco', 
               'Canadian', 'Austrian', 'British', 'German', 'Hungarian', 'Belgian', 
               'Italian', 'Singapore', 'Japanese', 'Russian', 'United_States', 
               'Brazilian', 'Abu_Dhabi'],
        2015: ['Australian', 'Malaysian', 'Chinese', 'Bahrain', 'Spanish', 'Monaco', 
               'Canadian', 'Austrian', 'British', 'Hungarian', 'Belgian', 'Italian', 
               'Singapore', 'Japanese', 'Russian', 'United_States', 'Mexican', 
               'Brazilian', 'Abu_Dhabi'],
        2016: ['Australian', 'Bahrain', 'Chinese', 'Russian', 'Spanish', 'Monaco', 
               'Canadian', 'European', 'Austrian', 'British', 'Hungarian', 'German', 
               'Belgian', 'Italian', 'Singapore', 'Malaysian', 'Japanese', 
               'United_States', 'Mexican', 'Brazilian', 'Abu_Dhabi'],
        2017: ['Australian', 'Chinese', 'Bahrain', 'Russian', 'Spanish', 'Monaco', 
               'Canadian', 'Azerbaijan', 'Austrian', 'British', 'Hungarian', 'Belgian', 
               'Italian', 'Singapore', 'Malaysian', 'Japanese', 'United_States', 
               'Mexican', 'Brazilian', 'Abu_Dhabi'],
        2018: ['Australian', 'Bahrain', 'Chinese', 'Azerbaijan', 'Spanish', 'Monaco', 
               'Canadian', 'French', 'Austrian', 'British', 'German', 'Hungarian', 
               'Belgian', 'Italian', 'Singapore', 'Russian', 'Japanese', 
               'United_States', 'Mexican', 'Brazilian', 'Abu_Dhabi'],
        2019: ['Australian', 'Bahrain', 'Chinese', 'Azerbaijan', 'Spanish', 'Monaco', 
               'Canadian', 'French', 'Austrian', 'British', 'German', 'Hungarian', 
               'Belgian', 'Italian', 'Singapore', 'Russian', 'Japanese', 'Mexican', 
               'United_States', 'Brazilian', 'Abu_Dhabi'],
        2020: ['Austrian', 'Styrian', 'Hungarian', 'British', '70th_Anniversary', 
               'Spanish', 'Belgian', 'Italian', 'Tuscan', 'Russian', 'Eifel', 
               'Portuguese', 'Emilia_Romagna', 'Turkish', 'Bahrain', 'Sakhir', 
               'Abu_Dhabi'],
        2021: ['Bahrain', 'Emilia_Romagna', 'Portuguese', 'Spanish', 'Monaco', 
               'Azerbaijan', 'French', 'Styrian', 'Austrian', 'British', 'Hungarian', 
               'Belgian', 'Dutch', 'Italian', 'Russian', 'Turkish', 'United_States', 
               'Mexico_City', 'São_Paulo', 'Qatar', 'Saudi_Arabian', 'Abu_Dhabi'],
        2022: ['Bahrain', 'Saudi_Arabian', 'Australian', 'Emilia_Romagna', 'Miami', 
               'Spanish', 'Monaco', 'Azerbaijan', 'Canadian', 'British', 'Austrian', 
               'French', 'Hungarian', 'Belgian', 'Dutch', 'Italian', 'Singapore', 
               'Japanese', 'United_States', 'Mexico_City', 'São_Paulo', 'Abu_Dhabi'],
        2023: ['Bahrain', 'Saudi_Arabian', 'Australian', 'Azerbaijan', 'Miami', 
               'Monaco', 'Spanish', 'Canadian', 'Austrian', 'British', 'Hungarian', 
               'Belgian', 'Dutch', 'Italian', 'Singapore', 'Japanese', 'Qatar', 
               'United_States', 'Mexico_City', 'São_Paulo', 'Las_Vegas', 'Abu_Dhabi'],
        2024: ['Bahrain', 'Saudi_Arabian', 'Australian', 'Japanese', 'Chinese', 
               'Miami', 'Emilia_Romagna', 'Monaco', 'Canadian', 'Spanish', 'Austrian', 
               'British', 'Hungarian', 'Belgian', 'Dutch', 'Italian', 'Azerbaijan', 
               'Singapore', 'United_States', 'Mexico_City', 'São_Paulo', 'Las_Vegas', 
               'Qatar', 'Abu_Dhabi']
    }
    
    return calendars.get(season, [])

def find_race_number(season, race_filename, calendar):
    """Encuentra el número de carrera basado en el calendario."""
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
        'Emilia_Romagna_Grand_Prix': 'Emilia_Romagna',
        'Dutch_Grand_Prix': 'Dutch',
        'Sakhir_Grand_Prix': 'Sakhir'
    }
    
    # Verificar casos especiales
    race_key = race_name
    for special, normalized in special_names.items():
        if special in race_name:
            race_key = normalized
            break
    else:
        race_key = race_name.replace('_Grand_Prix', '')
    
    # Buscar en calendario
    for i, calendar_race in enumerate(calendar, 1):
        if calendar_race.lower() in race_key.lower() or race_key.lower() in calendar_race.lower():
            return i
    
    return None

def get_driver_number_column(df):
    """Encuentra la columna con el número de piloto."""
    possible_cols = ['No', 'No.', 'Number', 'Driver Number', 'Num', 'Car number']
    
    for col in possible_cols:
        if col in df.columns:
            return col
    
    return None

def create_driver_mapping():
    """Crea mapeo para números de piloto."""
    return {
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

def merge_race_data_simple(season, race_number, race_filename):
    """
    Versión simplificada del merge que evita columnas duplicadas.
    """
    # Cargar resultados
    results_path = f"data/{season}/{race_filename}"
    
    if not os.path.exists(results_path):
        return None
    
    results_df = pd.read_csv(results_path)
    
    if results_df.empty:
        return None
    
    # Limpiar columnas de resultados
    results_df = clean_column_names(results_df)
    
    # Añadir columnas requeridas
    results_df = results_df.copy()
    results_df['Season'] = season
    results_df['RaceNumber'] = race_number
    results_df['RaceName'] = race_filename.replace('.csv', '')
    
    # Buscar columna de número de piloto en resultados
    driver_num_col = get_driver_number_column(results_df)
    
    # Inicializar columnas de pitstops
    pitstop_cols = ['DriverId', 'NPitstops', 'MedianPitStopDuration']
    for col in pitstop_cols:
        results_df[col] = pd.NA
    
    # Solo añadir DriverNumber si no existe
    if 'DriverNumber' not in results_df.columns and driver_num_col:
        results_df['DriverNumber'] = results_df[driver_num_col]
    
    # Cargar pitstops si existen (2019-2024)
    if season >= 2019:
        pitstop_path = f"data/pitstops/{season}/{season}_round{race_number:02d}_pitstops.csv"
        
        if os.path.exists(pitstop_path):
            pitstops_df = pd.read_csv(pitstop_path)
            
            if not pitstops_df.empty:
                # Limpiar pitstops
                pitstops_df = clean_column_names(pitstops_df)
                
                # Asegurar columnas necesarias
                required_pitstop_cols = ['DriverId', 'DriverNumber', 'NPitstops', 'MedianPitStopDuration']
                for col in required_pitstop_cols:
                    if col not in pitstops_df.columns:
                        pitstops_df[col] = pd.NA
                
                # Aplicar mapeo de corrección
                driver_mapping = create_driver_mapping()
                pitstops_df['MappedNumber'] = pitstops_df['DriverId'].map(
                    lambda x: driver_mapping.get(x, pd.NA)
                )
                
                # Usar número mapeado si existe, sino el original
                pitstops_df['MergeNumber'] = pitstops_df.apply(
                    lambda row: row['MappedNumber'] if pd.notna(row['MappedNumber']) else row['DriverNumber'],
                    axis=1
                )
                
                # Preparar DataFrame para merge
                pitstops_for_merge = pitstops_df[['MergeNumber', 'DriverId', 'NPitstops', 'MedianPitStopDuration']].copy()
                
                # Crear clave de merge en resultados
                if driver_num_col:
                    results_df['MergeNumber'] = results_df[driver_num_col].astype(str)
                else:
                    results_df['MergeNumber'] = pd.NA
                
                # Convertir a string
                results_df['MergeNumber'] = results_df['MergeNumber'].astype(str)
                pitstops_for_merge['MergeNumber'] = pitstops_for_merge['MergeNumber'].astype(str)
                
                # Realizar merge (LEFT JOIN)
                merged_df = pd.merge(
                    results_df,
                    pitstops_for_merge,
                    left_on='MergeNumber',
                    right_on='MergeNumber',
                    how='left',
                    suffixes=('', '_pitstop')
                )
                
                # Eliminar columnas temporales
                merged_df = merged_df.drop(columns=['MergeNumber'], errors='ignore')
                
                # Si hay columnas con sufijo _pitstop, renombrarlas
                for col in merged_df.columns:
                    if col.endswith('_pitstop'):
                        base_col = col.replace('_pitstop', '')
                        if base_col in merged_df.columns:
                            # Eliminar la original si existe
                            merged_df = merged_df.drop(columns=[base_col])
                        merged_df = merged_df.rename(columns={col: base_col})
                
                # Asegurar que DriverNumber existe
                if 'DriverNumber' not in merged_df.columns and driver_num_col:
                    merged_df['DriverNumber'] = merged_df[driver_num_col]
                
                return merged_df
    
    return results_df

def merge_all_data():
    """Función principal de fusión."""
    print("="*70)
    print("PARTE 3: CRUZADO DE DATOS - VERSIÓN LIMPIA")
    print("="*70)
    
    all_merged = []
    
    for season in range(2012, 2025):
        print(f"\n📅 Temporada {season}")
        
        # Obtener calendario
        calendar = get_season_calendar(season)
        if not calendar:
            print(f"  ⚠️  Sin calendario")
            continue
        
        # Buscar archivos de resultados
        results_dir = f"data/{season}"
        if not os.path.exists(results_dir):
            print(f"  ⚠️  Sin datos")
            continue
        
        result_files = sorted(glob.glob(os.path.join(results_dir, "*.csv")))
        print(f"  📊 {len(result_files)} carreras")
        
        for race_file in result_files:
            race_filename = os.path.basename(race_file)
            
            # Determinar número de carrera
            race_number = find_race_number(season, race_filename, calendar)
            
            if race_number is None:
                print(f"  ⚠️  No se pudo determinar RaceNumber para: {race_filename}")
                continue
            
            # Fusionar datos
            merged_df = merge_race_data_simple(season, race_number, race_filename)
            
            if merged_df is not None:
                # Limpiar columnas duplicadas
                merged_df = remove_duplicate_columns(merged_df)
                merged_df = clean_column_names(merged_df)
                
                all_merged.append(merged_df)
                print(f"    ✅ {race_filename}: {len(merged_df)} filas limpias")
    
    if not all_merged:
        print("\n❌ No hay datos para fusionar")
        return None
    
    print(f"\n{'='*70}")
    print("COMBINANDO TODOS LOS DATOS...")
    
    final_df = pd.concat(all_merged, ignore_index=True)
    
    # Limpieza final
    final_df = clean_column_names(final_df)
    final_df = remove_duplicate_columns(final_df)
    
    # Reordenar columnas
    preferred_order = ['Season', 'RaceNumber', 'RaceName', 'Position', 'Pos', 
                      'DriverNumber', 'Driver', 'Constructor', 'Laps', 
                      'Time/Retired', 'Grid', 'Points',
                      'DriverId', 'NPitstops', 'MedianPitStopDuration']
    
    # Mantener solo columnas existentes en el orden preferido
    existing_cols = [col for col in preferred_order if col in final_df.columns]
    other_cols = [col for col in final_df.columns if col not in existing_cols]
    
    final_df = final_df[existing_cols + other_cols]
    
    # Exportar
    os.makedirs("merged_data", exist_ok=True)
    output_file = "merged_data/f1_clean_dataset.csv"
    final_df.to_csv(output_file, index=False)
    
    # Crear metadatos
    create_metadata(final_df, output_file)
    
    # Mostrar estadísticas
    print_stats(final_df, output_file)
    
    return final_df

def create_metadata(df, output_path):
    """Crea archivo de metadatos."""
    metadata = {
        "dataset": "Formula 1 Clean Dataset 2012-2024",
        "description": "Dataset fusionado limpio sin columnas duplicadas",
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "season_range": f"{int(df['Season'].min())}-{int(df['Season'].max())}",
        "generated_date": pd.Timestamp.now().isoformat()
    }
    
    metadata_file = output_path.replace('.csv', '_metadata.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"  📄 Metadatos: {metadata_file}")

def print_stats(df, output_path):
    """Muestra estadísticas."""
    print(f"\n✅ DATASET LIMPIO CREADO:")
    print(f"   📁 {output_path}")
    print(f"   📊 {len(df):,} filas, {len(df.columns)} columnas")
    
    print(f"\n📋 COLUMNAS FINALES:")
    for i, col in enumerate(df.columns, 1):
        non_null = df[col].notna().sum()
        pct = non_null / len(df) * 100
        print(f"   {i:2}. {col:<25} {non_null:>6} ({pct:>5.1f}%)")
    
    print(f"\n📅 DATOS DE PITSTOPS:")
    if 'NPitstops' in df.columns:
        with_pitstops = df['NPitstops'].notna().sum()
        print(f"   Carreras con pitstops: {with_pitstops:,} ({with_pitstops/len(df)*100:.1f}%)")
        
        for season in range(2019, 2025):
            season_data = df[df['Season'] == season]
            if len(season_data) > 0:
                pitstops_count = season_data['NPitstops'].notna().sum()
                print(f"   {season}: {pitstops_count:>4}/{len(season_data):<4} ({pitstops_count/len(season_data)*100:>5.1f}%)")

def validate_dataset(df):
    """Valida el dataset final."""
    print(f"\n{'='*70}")
    print("VALIDACIÓN DEL DATASET")
    print(f"{'='*70}")
    
    checks = [
        ("Dataset no vacío", df is not None and len(df) > 0),
        ("Columnas Season y RaceNumber presentes", 
         all(col in df.columns for col in ['Season', 'RaceNumber'])),
        ("Sin columnas Unnamed", not any('Unnamed' in col for col in df.columns)),
        ("Sin columnas duplicadas _x/_y", 
         not any(col.endswith('_x') or col.endswith('_y') for col in df.columns)),
        ("DriverNumber presente", 'DriverNumber' in df.columns),
        ("Columnas de pitstops presentes", 
         all(col in df.columns for col in ['DriverId', 'NPitstops', 'MedianPitStopDuration'])),
    ]
    
    all_ok = True
    for check_name, condition in checks:
        status = "✅" if condition else "❌"
        print(f"  {status} {check_name}")
        if not condition:
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    print("🏎️  PARTE 3: FUSIÓN LIMPIA DE DATOS F1")
    print("Objetivo: Dataset sin columnas duplicadas o sin nombre")
    
    dataset = merge_all_data()
    
    if dataset is not None:
        valid = validate_dataset(dataset)
        
        print(f"\n{'='*70}")
        if valid:
            print("🎉 DATASET VÁLIDO Y LISTO PARA ANÁLISIS")
        else:
            print("⚠️  DATASET CON PROBLEMAS - REVISAR")
        
        print(f"\n🔍 EJEMPLO (5 filas aleatorias):")
        sample = dataset.sample(5, random_state=42)
        
        # Mostrar columnas clave
        key_cols = ['Season', 'RaceNumber', 'RaceName', 'Driver', 'DriverNumber', 
                   'NPitstops', 'MedianPitStopDuration']
        available_cols = [col for col in key_cols if col in sample.columns]
        
        if available_cols:
            print(sample[available_cols].to_string())
        
        print(f"\n💾 Archivo: merged_data/f1_clean_dataset.csv")
    else:
        print("\n❌ Error al crear el dataset")