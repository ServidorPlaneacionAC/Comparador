import streamlit as st
import pandas as pd
import base64

# Tolerancia para la comparación de números decimales
TOLERANCIA_DECIMAL = 1e-9

# Función para encontrar diferencias entre los datos de dos DataFrames agrupados por material
def comparar_por_material(df_base, df_comparar):
    # Establecer la columna "Material" como índice
    df_base = df_base.set_index("Material")
    df_comparar = df_comparar.set_index("Material")

    # Agrupar los datos por material
    df_base_grouped = df_base.groupby(level=0).apply(lambda x: x.droplevel(0)).reset_index(drop=True)
    df_comparar_grouped = df_comparar.groupby(level=0).apply(lambda x: x.droplevel(0)).reset_index(drop=True)

    # Encontrar diferencias entre los DataFrames agrupados
    df_diferencias = df_comparar_grouped[df_comparar_grouped.ne(df_base_grouped).any(axis=1)]

    return df_diferencias

# Función para resaltar diferencias en rojo
def resaltar_diferencias(val):
    color = 'red' if '*' in str(val) else 'black'
    return f'color: {color}'

# Función para generar un enlace de descarga de un archivo binario
def get_binary_file_downloader_html(bin_data, file_label='File'):
    bin_str = base64.b64encode(bin_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}">{file_label}</a>'
    return href

# UI
st.title("Comparador de Datos Maestros")

archivo_base = st.file_uploader("Cargar archivo base (base de datos)", type=["xlsx"])
archivo_comparar = st.file_uploader("Cargar archivo a comparar", type=["xlsx"])

if archivo_base and archivo_comparar:
    df_base = pd.read_excel(archivo_base)
    df_comparar = pd.read_excel(archivo_comparar)

    # Comparar los datos agrupados por material
    df_diferencias = comparar_por_material(df_base, df_comparar)

    # Mostrar resultados
    if not df_diferencias.empty:
        st.header("Materiales con Diferencias:")
        st.table(df_diferencias.style.applymap(resaltar_diferencias))
    else:
        st.info("No se encontraron diferencias en los datos.")

    # Descargar los resultados en un archivo Excel
    if st.button("Descargar resultados en Excel"):
        with pd.ExcelWriter("resultados_comparacion.xlsx") as writer:
            df_diferencias.to_excel(writer, sheet_name="Materiales con Diferencias", index=False)

        with open("resultados_comparacion.xlsx", "rb") as f:
            bin_data = f.read()

        st.markdown(get_binary_file_downloader_html(bin_data, "resultados_comparacion.xlsx"), unsafe_allow_html=True)
