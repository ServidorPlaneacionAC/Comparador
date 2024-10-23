import pandas as pd
import streamlit as st

# Función para encontrar filas con diferencias
def encontrar_filas_con_diferencias(df_base, df_comparar, llave_primaria):
    # Inicializar un DataFrame para almacenar las diferencias
    df_diferencias = df_comparar[[llave_primaria]].copy()
    
    # Iterar sobre cada columna (excepto la llave primaria)
    for columna in df_comparar.columns:
        if columna == llave_primaria:
            continue  # Omite la llave primaria
        
        # Comparar valores y guardar en el DataFrame de diferencias
        df_diferencias[columna] = df_comparar[columna].where(
            (df_comparar[columna] != df_base[columna].reindex(df_comparar[llave_primaria]).values) &
            ((df_comparar[columna].notna()) | (df_base[columna].notna())),  # Asegúrate de omitir ambos NaN
            None  # Asigna None donde no hay diferencias
        )

    # Filtrar las filas donde al menos una columna tiene un valor diferente
    df_diferencias = df_diferencias.dropna(how='all', subset=df_diferencias.columns[1:])  # Elimina filas sin diferencias

    return df_diferencias

# Cargar los archivos Excel
df_base = pd.read_excel('archivo_base.xlsx')
df_comparar = pd.read_excel('archivo_a_comparar.xlsx')

# Configuración de Streamlit
st.title("Comparador de Archivos Excel")

# Seleccionar la columna de llave primaria
llave_primaria = st.selectbox("Selecciona la llave primaria", df_base.columns)

# Realizar la comparación
df_diferencias = encontrar_filas_con_diferencias(df_base.set_index(llave_primaria), df_comparar.set_index(llave_primaria), llave_primaria)

# Mostrar resultados
st.subheader("Diferencias encontradas:")
st.dataframe(df_diferencias)
