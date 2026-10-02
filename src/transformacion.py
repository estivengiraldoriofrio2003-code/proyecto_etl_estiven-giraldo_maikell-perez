import pandas as pd
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
