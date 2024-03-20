import streamlit as st
import pandas as pd
import base64

def comparar_por_material(df_base, df_comparar):
    # Establecer la columna "Material" como índice
    df_base = df_base.set_index("Material")
    df_comparar = df_comparar.set_index("Material")

    # Organizar la información en conjuntos basados en el material
    conjunto_base = set(df_base.index)
    conjunto_comparar = set(df_comparar.index)

    # Encontrar elementos en conjunto_comparar que no están en conjunto_base (nuevos materiales)
    nuevos_materiales = list(conjunto_comparar - conjunto_base)

    # Encontrar elementos en conjunto_base que no están en conjunto_comparar (materiales eliminados)
    materiales_eliminados = list(conjunto_base - conjunto_comparar)

    # Encontrar elementos en ambos conjuntos pero con diferencias en los datos
    materiales_con_diferencias = list(conjunto_base.intersection(conjunto_comparar))

    # Crear DataFrames para mostrar las diferencias
    df_nuevos = df_comparar.loc[nuevos_materiales]
    df_eliminados = df_base.loc[materiales_eliminados]
    df_diferencias = pd.concat([df_base.loc[materiales_con_diferencias], df_comparar.loc[materiales_con_diferencias]], keys=['Base', 'Comparar'])

    return df_nuevos, df_eliminados, df_diferencias

# Función para mostrar enlaces de descarga de archivos binarios
def get_binary_file_downloader_html(bin_data, file_label='File'):
    bin_str = base64.b64encode(bin_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}">{file_label}</a>'
    return href

# Función para resaltar diferencias en rojo
def resaltar_diferencias(val):
    color = 'red' if '*' in str(val) else 'black'
    return f'color: {color}'

# UI
st.title("Comparador de Datos Maestros")

archivo_base = st.file_uploader("Cargar archivo base (base de datos)", type=["xlsx"])
archivo_comparar = st.file_uploader("Cargar archivo a comparar", type=["xlsx"])

if archivo_base and archivo_comparar:
    df_base = pd.read_excel(archivo_base)
    df_comparar = pd.read_excel(archivo_comparar)

    # Comparar los conjuntos de datos basados en el material
    df_nuevos, df_eliminados, df_diferencias = comparar_por_material(df_base, df_comparar)

    # Mostrar resultados
    st.header("Nuevos Materiales:")
    st.dataframe(df_nuevos.style.applymap(resaltar_diferencias).render(), unsafe_allow_html=True)

    st.header("Materiales Eliminados:")
    st.dataframe(df_eliminados.style.applymap(resaltar_diferencias).render(), unsafe_allow_html=True)

    st.header("Materiales con Diferencias:")
    st.dataframe(df_diferencias.style.applymap(resaltar_diferencias).render(), unsafe_allow_html=True)

    # Descargar los resultados en archivos Excel
    if st.button("Descargar resultados en Excel"):
        with pd.ExcelWriter("resultados_comparacion.xlsx") as writer:
            df_nuevos.to_excel(writer, sheet_name="Nuevos Materiales")
            df_eliminados.to_excel(writer, sheet_name="Materiales Eliminados")
            df_diferencias.to_excel(writer, sheet_name="Materiales con Diferencias")

        with open("resultados_comparacion.xlsx", "rb") as f:
            bin_data = f.read()

        st.markdown(get_binary_file_downloader_html(bin_data, "resultados_comparacion.xlsx"), unsafe_allow_html=True)

    # Botones adicionales
    if st.button("Mostrar información del archivo base correspondiente a las diferencias"):
        st.write("Información del archivo base correspondiente a las diferencias:")
        st.dataframe(df_base.loc[df_diferencias.index].style.applymap(resaltar_diferencias).render(), unsafe_allow_html=True)

    if st.button("Mostrar informacion nueva en comparar "):
        st.write("Informacion en el archivo a comparar que no está en el archivo base:")
        st.dataframe(df_comparar.loc[df_nuevos.index].style.applymap(resaltar_diferencias).render(), unsafe_allow_html=True)

    if st.button("Mostrar información faltante en comparación al archivo base"):
        st.write("Información faltante en comparación al archivo base:")
        st.dataframe(df_base.loc[df_eliminados.index].style.applymap(resaltar_diferencias).render(), unsafe_allow_html=True)
