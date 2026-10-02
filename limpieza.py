import os

# 1. Crear la estructura de directorios exigida por la guía
os.makedirs('datos', exist_ok=True)
os.makedirs('src', exist_ok=True)

# Generar datos sucios en la carpeta correcta (Temática: E-Sports)
with open('datos/esports_raw_data.csv', 'w', encoding='utf-8') as f:
    f.write("ID,Nickname,Earnings,Playtime,WinRate\n")
    f.write("201,Faker ,$1.5M,1200 hrs,65%\n")
    f.write("202, s1mple,$850K,950 hours,60%\n")
    f.write("202, s1mple,$850K,950 hours,60%\n") # Duplicado intencional
    f.write("203,TenZ ,$250K,400 hrs,58%\n")
    f.write("204, Bugha ,$3.2M,1500 hours,62%\n")

# 2. Archivo de Dependencias
with open('requirements.txt', 'w') as f:
    f.write("pandas\nnumpy\nsqlalchemy\npyarrow\nfastparquet\n")

# 3. Control de Versiones (Excluir archivos masivos)
with open('.gitignore', 'w') as f:
    f.write("datos/\n__pycache__/\n*.db\n")

# 4. Módulo de Transformación (src/transformacion.py)
with open('src/transformacion.py', 'w', encoding='utf-8') as f:
    f.write('''import pandas as pd
import re

def limpiar_datos(df):
    # Eliminar duplicados por ID
    df = df.drop_duplicates(subset=['ID'], keep='first').copy()
    
    # Quitar espacios en blanco de los nombres
    df['Nickname'] = df['Nickname'].str.strip()
    
    # Función para arreglar el dinero
    def parsear_ganancias(v):
        v = str(v).replace('$', '').strip()
        if 'M' in v: return float(v.replace('M', '')) * 1000000
        if 'K' in v: return float(v.replace('K', '')) * 1000
        return 0.0
        
    # Función para dejar solo los números en las horas jugadas
    def parsear_horas(v):
        v = str(v).replace('hrs', '').replace('hours', '').strip()
        try:
            return int(v)
        except:
            return 0
    
    # Aplicar las limpiezas
    df['Earnings_USD'] = df['Earnings'].apply(parsear_ganancias)
    df['Playtime_Hours'] = df['Playtime'].apply(parsear_horas)
    
    # Retornar solo las columnas limpias y útiles
    return df[['ID', 'Nickname', 'Earnings_USD', 'Playtime_Hours']]
''')

# 5. Módulo de Carga e Idempotencia (src/carga.py)
with open('src/carga.py', 'w', encoding='utf-8') as f:
    f.write('''import pandas as pd
import logging
from sqlalchemy import create_engine, text

# Nueva base de datos para E-Sports
motor_bd = create_engine('sqlite:///datos/almacen_esports.db')

def cargar_sqlite_idempotente(df_lote):
    with motor_bd.connect() as conexion:
        try:
            res = pd.read_sql(text("SELECT ID FROM jugadores_esports"), con=conexion)
            ids_existentes = res['ID'].tolist()
        except:
            ids_existentes = []
            
        df_nuevos = df_lote[~df_lote['ID'].isin(ids_existentes)]
        if not df_nuevos.empty:
            df_nuevos.to_sql('jugadores_esports', con=motor_bd, if_exists='append', index=False)
            logging.info(f"Cargados {len(df_nuevos)} registros nuevos en la base de datos.")
''')

# 6. Orquestador Principal (main.py)
with open('main.py', 'w', encoding='utf-8') as f:
    f.write('''import pandas as pd
import logging
from src.transformacion import limpiar_datos
from src.carga import cargar_sqlite_idempotente

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def ejecutar_pipeline():
    logging.info("Arrancando el procesador de datos de E-Sports...")
    ruta = 'datos/esports_raw_data.csv'
    
    # Lectura fraccionada para no saturar la memoria
    iterador_lotes = pd.read_csv(ruta, sep=',', encoding='utf-8', chunksize=2, low_memory=False)
    
    df_completo = []
    for num, lote in enumerate(iterador_lotes):
        logging.info(f"Procesando lote {num + 1}...")
        lote_limpio = limpiar_datos(lote)
        cargar_sqlite_idempotente(lote_limpio)
        df_completo.append(lote_limpio)
        
    # Exportacion final a Parquet analítico
    if df_completo:
        df_final = pd.concat(df_completo)
        df_final.to_parquet('datos/esports_analitica.parquet', index=False)
        logging.info("Pipeline completado exitosamente. Los datos están listos.")

if __name__ == "__main__":
    ejecutar_pipeline()
''')

print("¡Listo! El proyecto de E-Sports ha sido creado. Dile a tu compañero que ejecute 'py main.py'") 