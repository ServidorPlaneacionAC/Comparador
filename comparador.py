import streamlit as st
import pandas as pd
import base64

# Función para encontrar filas con diferencias y retornar las columnas relevantes
def encontrar_filas_con_diferencias(df_base, df_comparar, llave_primaria):
    # Comparar solo las columnas que no son la llave primaria
    columnas_a_comparar = df_comparar.columns.difference([llave_primaria])
    
    # Crear un DataFrame para almacenar las diferencias
    df_diferencias = df_comparar[[llave_primaria]].copy()

    for col in columnas_a_comparar:
        # Comparar solo si ambos valores no son None o espacios en blanco
        df_diferencias[col] = df_comparar.apply(
            lambda x: x[col] if pd.notna(x[col]) and x[col] != '' and (x[llave_primaria] not in df_base.index or (x[col] != df_base.at[x[llave_primaria], col] if x[llave_primaria] in df_base.index else True)) else None,
            axis=1
        )
    
    # Filtrar para eliminar filas donde todas las comparaciones son None
    df_diferencias = df_diferencias.dropna(how='all', subset=columnas_a_comparar)
    
    return df_diferencias

# Titulo
st.title("Comparador de Datos Maestros")

# Para subir el archivo base en Excel
archivo_base = st.file_uploader("Cargar archivo base (base de datos)", type=["xlsx"])

# Para subir el archivo a comparar en Excel
archivo_comparar = st.file_uploader("Cargar archivo a comparar", type=["xlsx"])

if archivo_base and archivo_comparar:
    # Cargar los archivos
    df_base = pd.read_excel(archivo_base)
    df_comparar = pd.read_excel(archivo_comparar)

    # Seleccionar la columna clave para comparación
    llave_primaria = st.selectbox("Selecciona la columna llave primaria:", df_comparar.columns)

    # Verificar si los DataFrames son idénticos
    if df_base.equals(df_comparar):
        st.error("Los archivos son idénticos. No hay diferencias para resaltar.")
    elif df_base.columns.to_list() != df_comparar.columns.to_list():
        st.error("Los archivos no tienen las mismas columnas. Asegúrate de cargar archivos con las mismas columnas.")
    else:
        # Encontrar filas con diferencias y omitir None y espacios en blanco
        df_diferencias = encontrar_filas_con_diferencias(df_base.set_index(llave_primaria), df_comparar.set_index(llave_primaria), llave_primaria)

        # Mostrar el DataFrame con filas que tienen diferencias
        if not df_diferencias.empty:
            st.write("Información con diferencias:")
            st.table(df_diferencias)
        else:
            st.write("No se encontraron diferencias significativas.")

# Función para generar un enlace de descarga de un archivo binario
def get_binary_file_downloader_html(file_path, file_label='Archivo'):
    with open(file_path, 'rb') as f:
        data = f.read()
        base64_encoded = base64.b64encode(data).decode()
        return f'<a href="data:application/octet-stream;base64,{base64_encoded}" download="{file_path}">{file_label}</a>'
