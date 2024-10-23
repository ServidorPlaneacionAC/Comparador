import streamlit as st
import pandas as pd
import base64

# Función para encontrar diferencias basadas en una llave primaria
def encontrar_diferencias(df_base, df_comparar, llave_primaria):
    # Hacer merge de los DataFrames usando la llave primaria
    merged_df = df_base.merge(df_comparar, on=llave_primaria, suffixes=('_base', '_comparar'), how='outer')

    # Crear un DataFrame vacío para almacenar diferencias
    diferencias = pd.DataFrame()

    # Iterar sobre las columnas del DataFrame base
    for col in df_base.columns:
        if col != llave_primaria:  # Ignorar la llave primaria
            # Comparar las columnas correspondientes
            diffs = merged_df[f"{col}_base"] != merged_df[f"{col}_comparar"]
            # Filtrar y almacenar las diferencias en el DataFrame
            diffs_df = merged_df[diffs][[llave_primaria, f"{col}_base", f"{col}_comparar"]]
            diffs_df.columns = [llave_primaria, f"{col}_base", f"{col}_comparar"]
            diferencias = pd.concat([diferencias, diffs_df], ignore_index=True)

    return diferencias

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

    # Mostrar la lista de columnas para la selección de llave primaria
    llave_primaria = st.selectbox("Selecciona la llave primaria para la comparación", df_base.columns.tolist())

    # Encontrar diferencias
    diferencias = encontrar_diferencias(df_base, df_comparar, llave_primaria)

    # Mostrar diferencias si existen
    if not diferencias.empty:
        st.write("Diferencias encontradas:")
        st.table(diferencias)

        # Botón para descargar un archivo Excel con las diferencias
        if st.button("Descargar información en Excel con diferencias"):
            # Guardar diferencias en un archivo Excel
            diferencias.to_excel("diferencias.xlsx", index=False)

            # Enlace para descargar el archivo Excel
            st.markdown(
                get_binary_file_downloader_html("diferencias.xlsx", 'Archivo Excel con diferencias'),
                unsafe_allow_html=True
            )
    else:
        st.write("No se encontraron diferencias.")
