import streamlit as st
import pandas as pd
import base64

# Tolerancia para la comparación de números decimales
TOLERANCIA_DECIMAL = 1e-9

def encontrar_diferencias_por_columna(df_base, df_comparar):
    # Copiar df_comparar para marcar diferencias
    df_diferencias = df_comparar.copy()

    # Iterar sobre cada columna para comparar sus contenidos
    for col in df_comparar.columns:
        if pd.api.types.is_numeric_dtype(df_comparar[col]):
            # Para columnas numéricas, marcar diferencias considerando una tolerancia
            df_diferencias[col] = df_comparar.apply(
                lambda x: f"{x[col]}*" if not ((df_base[col] - x[col]).abs() <= TOLERANCIA_DECIMAL).any() else x[col], axis=1)
        else:
            # Para columnas no numéricas, marcar diferencias directamente
            df_diferencias[col] = df_comparar.apply(
                lambda x: f"{x[col]}*" if x[col] not in df_base[col].values else x[col], axis=1)

    return df_diferencias

def resaltar_diferencias(val):
    if '*' in str(val):
        return 'background-color: red'
    else:
        return ''

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}">{file_label}</a>'
    return href

# UI
st.title("Comparador de Datos Maestros")

archivo_base = st.file_uploader("Cargar archivo base (base de datos)", type=["xlsx"])
archivo_comparar = st.file_uploader("Cargar archivo a comparar", type=["xlsx"])

if archivo_base and archivo_comparar:
    df_base = pd.read_excel(archivo_base)
    df_comparar = pd.read_excel(archivo_comparar)

    if set(df_base.columns) != set(df_comparar.columns):
        st.error("Los archivos no tienen las mismas columnas. Asegúrate de cargar archivos con las mismas columnas.")
    else:
        df_diferencias = encontrar_diferencias_por_columna(df_base, df_comparar)
        st.write("Información que tiene diferencias:")
        st.dataframe(df_diferencias.style.applymap(resaltar_diferencias))

        # Botón para descargar la información en un archivo Excel con resaltado
        if st.button("Descargar información en Excel con resaltado"):
            df_diferencias.to_excel("informacion_comparada.xlsx", index=False)
            st.markdown(get_binary_file_downloader_html('informacion_comparada.xlsx', 'Descargar como Excel'), unsafe_allow_html=True)
