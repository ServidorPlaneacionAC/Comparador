import streamlit as st
import pandas as pd
import base64
from openpyxl.styles import PatternFill

# Tolerancia para la comparación de números decimales
TOLERANCIA_DECIMAL = 1e-9

# Función para encontrar filas con diferencias y marcar las celdas con un asterisco
def encontrar_filas_con_diferencias(df_base, df_comparar):
    # Identificar las filas que existen en el archivo a comparar pero no en la base de datos
    filas_nuevas = df_comparar.merge(df_base, how='outer', indicator=True).loc[lambda x: x['_merge'] == 'left_only'].drop(
        columns=['_merge'])

    # Obtener el DataFrame con filas que tienen diferencias
    df_diferencias = df_comparar[df_comparar.index.isin(filas_nuevas.index)].copy()

    # Marcar las celdas con un asterisco solo donde la información no es igual al archivo base
    for col in df_comparar.columns:
        # Comparar tipos de datos y manejar la igualdad numérica para tipos numéricos
        if pd.api.types.is_numeric_dtype(df_comparar[col]) and pd.api.types.is_numeric_dtype(df_base[col]):
            df_diferencias[col] = df_diferencias.apply(lambda x: f"{x[col]}*" if x.name in df_base.index and abs(x[col] - df_base.at[x.name, col]) > TOLERANCIA_DECIMAL else x[col], axis=1)
        else:
            df_diferencias[col] = df_diferencias.apply(lambda x: f"{x[col]}*" if x.name in df_base.index and x[col] != df_base.at[x.name, col] else x[col], axis=1)

    return df_diferencias

# Función para aplicar formato a las celdas con diferencias
def resaltar_diferencias(val):
    if '*' in str(val):
        return 'background-color: red'
    else:
        return ''

# Función para generar un enlace de descarga de un archivo binario
def get_binary_file_downloader_html(file_path, file_label='Archivo'):
    with open(file_path, 'rb') as f:
        data = f.read()
        base64_encoded = base64.b64encode(data).decode()
        return f'<a href="data:application/octet-stream;base64,{base64_encoded}" download="{file_path}">{file_label}</a>'

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

    # Imprimir los nombres de las columnas en ambos DataFrames
    st.write("Nombres de las columnas en el archivo base:", df_base.columns.tolist())
    st.write("Nombres de las columnas en el archivo a comparar:", df_comparar.columns.tolist())

    # Validar que alguna columna del archivo base contenga 'material'
    if any('material' in col.lower() for col in df_base.columns):
        # Validar que 'material' esté presente en las columnas del archivo a comparar
        if 'material' in df_comparar.columns:
            # Encontrar filas con diferencias y marcar celdas con un asterisco
            df_diferencias = encontrar_filas_con_diferencias(df_base, df_comparar)

            # Filtrar las filas en el archivo a comparar que tienen materiales nuevos
            df_filas_con_materiales_nuevos = df_comparar[
                ~df_comparar['material'].isin(df_base['material']) | (df_comparar['material'] != df_base['material'])
            ].copy()

            # Resto del código...

        else:
            st.warning(f"El archivo a comparar no tiene una columna llamada 'material'. Asegúrate de que la columna 'material' esté presente.")
    else:
        st.warning("Ninguna columna del archivo base contiene 'material'. Asegúrate de que la columna 'material' esté presente en alguno de los nombres de las columnas.")
else:
    st.warning("Por favor, carga ambos archivos para comenzar la comparación.")
