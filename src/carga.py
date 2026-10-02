import pandas as pd
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
