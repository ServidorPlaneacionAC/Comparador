import streamlit as st
import pandas as pd
import base64

# Tolerancia para la comparación de números decimales
TOLERANCIA_DECIMAL = 1e-9

# Función para encontrar filas con diferencias
def encontrar_filas_con_diferencias(df_base, df_comparar, clave):
    if clave not in df_base.columns or clave not in df_comparar.columns:
        raise ValueError("La columna clave debe estar presente en ambos DataFrames.")
    
    df_base[clave] = df_base[clave].astype(str)
    df_comparar[clave] = df_comparar[clave].astype(str)

    # Unir los DataFrames en base a la clave
    df_merged = df_comparar.merge(df_base, on=clave, suffixes=('_comparar', '_base'), how='left', indicator=True)

    # Crear un DataFrame para las diferencias
    df_diferencias = df_merged[df_merged['_merge'] == 'both'].copy()

    # Comparar las columnas y marcar las diferencias
    for col in df_base.columns:
        if col == clave:
            continue
        
        col_comparar = col + '_comparar'
        col_base = col + '_base'
        
        # Crear una columna para las diferencias
        df_diferencias[col + '_diferencia'] = df_diferencias.apply(
            lambda x: f"{x[col_comparar]}*" if pd.notna(x[col_base]) and (
                (pd.api.types.is_numeric_dtype(df_base[col]) and abs(x[col_comparar] - x[col_base]) > TOLERANCIA_DECIMAL) or
                (str(x[col_comparar]).strip() != str(x[col_base]).strip())
            ) else x[col_comparar], axis=1
        )

    # Seleccionar solo las columnas que queremos mostrar
    columnas_a_mostrar = [clave] + [col + '_diferencia' for col in df_base.columns if col != clave]
    return df_diferencias[columnas_a_mostrar]

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

    # Mostrar el desplegable para seleccionar la columna clave
    clave = st.selectbox("Selecciona la columna que servirá como llave primaria para la comparación:", df_base.columns)

    if clave:
        # Verificar si los DataFrames son idénticos
        if df_base.equals(df_comparar):
            st.error("Los archivos son idénticos. No hay diferencias para resaltar.")
        elif df_base.columns.to_list() != df_comparar.columns.to_list():
            st.error("Los archivos no tienen las mismas columnas. Asegúrate de cargar archivos con las mismas columnas.")
        else:
            # Encontrar filas con diferencias
            df_diferencias = encontrar_filas_con_diferencias(df_base, df_comparar, clave)

            # Mostrar el DataFrame con filas que tienen diferencias
            st.write("Información que tiene diferencias:")
            # Modificar la visualización de las diferencias para mostrar un asterisco en rojo
            df_diferencias_display = df_diferencias.copy()
            for col in df_diferencias_display.columns[1:]:
                df_diferencias_display[col] = df_diferencias_display[col].str.replace('*', '', regex=False)
                df_diferencias_display[col] = df_diferencias_display[col].apply(lambda x: f"<span style='color: red;'>{x}*</span>" if '*' in x else x)

            # Mostrar el DataFrame con HTML
            st.markdown(df_diferencias_display.to_html(escape=False), unsafe_allow_html=True)

# Botón para descargar la información en un archivo Excel con resaltado
if st.button("Descargar información en Excel con resaltado"):
    # Crear un objeto ExcelWriter para escribir en un solo archivo Excel
    with pd.ExcelWriter("informacion_comparada.xlsx", engine='openpyxl') as writer:
        # Escribir cada DataFrame en una pestaña diferente
        df_diferencias.to_excel(writer, sheet_name='Diferencias', index=True)

    # Enlace para descargar el archivo Excel
    st.markdown(
        get_binary_file_downloader_html("informacion_comparada.xlsx", 'Archivo Excel con resaltado'),
        unsafe_allow_html=True
    )
