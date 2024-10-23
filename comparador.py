import streamlit as st
import pandas as pd
import numpy as np
import base64
from openpyxl.styles import PatternFill

# Función para encontrar diferencias y contar diferencias por columna
def encontrar_diferencias(df_base, df_comparar):
    diferencias = {}
    resumen = {}

    for col in df_base.columns:
        # Comparar cada columna
        diffs = df_comparar[col] != df_base[col]
        diferencias[col] = df_comparar[diffs].copy()
        # Contar el número de diferencias
        resumen[col] = diffs.sum()
        
        # Marcar diferencias en el DataFrame
        diferencias[col]['Diferencia'] = 'Diferente'
        diferencias[col].loc[differences[col].index, col] += '*'

    return diferencias, resumen

# Función para generar un enlace de descarga de un archivo binario
def get_binary_file_downloader_html(file_path, file_label='Archivo'):
    with open(file_path, 'rb') as f:
        data = f.read()
        base64_encoded = base64.b64encode(data).decode()
        return f'<a href="data:application/octet-stream;base64,{base64_encoded}" download="{file_path}">{file_label}</a>'

# Titulo
st.title("Comparador de Datos Maestros Mejorado")

# Para subir el archivo base en Excel
archivo_base = st.file_uploader("Cargar archivo base (base de datos)", type=["xlsx"])

# Para subir el archivo a comparar en Excel
archivo_comparar = st.file_uploader("Cargar archivo a comparar", type=["xlsx"])

if archivo_base and archivo_comparar:
    # Cargar los archivos
    df_base = pd.read_excel(archivo_base)
    df_comparar = pd.read_excel(archivo_comparar)

    # Verificar si los DataFrames tienen las mismas columnas
    if df_base.columns.to_list() != df_comparar.columns.to_list():
        st.error("Los archivos no tienen las mismas columnas. Asegúrate de cargar archivos con las mismas columnas.")
    else:
        # Encontrar diferencias
        diferencias, resumen = encontrar_diferencias(df_base, df_comparar)

        # Mostrar resumen de diferencias
        st.write("Resumen de diferencias por columna:")
        st.table(pd.DataFrame.from_dict(resumen, orient='index', columns=['Número de Diferencias']))

        # Mostrar detalles de las diferencias
        for col, df_diff in diferencias.items():
            if not df_diff.empty:
                st.write(f"Diferencias en la columna '{col}':")
                st.table(df_diff)

        # Botón para descargar un archivo Excel con las diferencias
        if st.button("Descargar información en Excel con diferencias"):
            with pd.ExcelWriter("informacion_diferencias.xlsx", engine='openpyxl') as writer:
                # Escribir el resumen de diferencias en una pestaña
                pd.DataFrame.from_dict(resumen, orient='index', columns=['Número de Diferencias']).to_excel(writer, sheet_name='Resumen', index=True)

                # Escribir cada columna con diferencias en su propia pestaña
                for col, df_diff in diferencias.items():
                    if not df_diff.empty:
                        df_diff.to_excel(writer, sheet_name=col, index=True)

            # Enlace para descargar el archivo Excel
            st.markdown(
                get_binary_file_downloader_html("informacion_diferencias.xlsx", 'Archivo Excel con diferencias'),
                unsafe_allow_html=True
            )
