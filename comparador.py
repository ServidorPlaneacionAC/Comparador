import pandas as pd
import streamlit as st

# Cargar archivos
def cargar_y_preparar_dataframe(archivo):
    """Carga un archivo Excel."""
    df = pd.read_excel(archivo)
    # Opcional: podrías querer resetear el índice si vas a manipular los dataframes
    # df.reset_index(drop=True, inplace=True)
    return df

# Comparar contenido de columnas entre dos DataFrames
def comparar_contenido_columnas(df_base, df_comparar):
    # Asegurarse de que ambas DataFrames tengan las mismas columnas
    if not df_base.columns.equals(df_comparar.columns):
        raise ValueError("Los DataFrames no tienen las mismas columnas")
    
    diferencias = {}
    # Iterar sobre cada columna
    for col in df_base.columns:
        # Para cada elemento en la columna del DataFrame base, verificar si está presente en la columna correspondiente del DataFrame a comparar
        diferencias_col = df_base[col].apply(lambda x: x not in df_comparar[col].values)
        if diferencias_col.any():
            diferencias[col] = diferencias_col
    
    return diferencias

# Subir archivos mediante Streamlit
archivo_base = st.file_uploader("Cargar archivo base (base de datos)", type=["xlsx"])
archivo_comparar = st.file_uploader("Cargar archivo a comparar", type=["xlsx"])

if archivo_base and archivo_comparar:
    df_base = cargar_y_preparar_dataframe(archivo_base)
    df_comparar = cargar_y_preparar_dataframe(archivo_comparar)
    
    try:
        diferencias = comparar_contenido_columnas(df_base, df_comparar)
        if diferencias:
            st.write("Se encontraron diferencias en las siguientes columnas:")
            for col, diff in diferencias.items():
                st.write(f"- Columna: {col}, Cantidad de diferencias: {diff.sum()}")
                # Opcional: Mostrar índices de las diferencias
                # st.write(diff[diff].index.tolist())
        else:
            st.write("No se encontraron diferencias en el contenido de las columnas.")
    except ValueError as e:
        st.error(e)
