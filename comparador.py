import streamlit as st
import pandas as pd
import base64

# Tolerancia para la comparación de números decimales
TOLERANCIA_DECIMAL = 1e-9

# Función para encontrar filas con diferencias y marcar las celdas con un asterisco
def encontrar_filas_con_diferencias(df_base, df_comparar, clave):
    # Asegurarse de que la columna clave esté en ambos DataFrames
    if clave not in df_base.columns or clave not in df_comparar.columns:
        raise ValueError("La columna clave debe estar presente en ambos DataFrames.")
    
    # Convertir la columna clave a tipo string para evitar problemas de tipo
    df_base[clave] = df_base[clave].astype(str)
    df_comparar[clave] = df_comparar[clave].astype(str)

    # Unir los DataFrames en base a la clave
    df_merged = df_comparar.merge(df_base, on=clave, suffixes=('_comparar', '_base'), how='left', indicator=True)

    # Crear un DataFrame para las diferencias
    df_diferencias = df_merged[df_merged['_merge'] == 'both'].copy()

    # Comparar las columnas
    for col in df_base.columns:
        if col == clave:  # No comparar la columna clave
            continue
        
        col_comparar = col + '_comparar'
        col_base = col + '_base'
        
        # Comparar columnas según el tipo
        if pd.api.types.is_numeric_dtype(df_base[col]):
            # Comparar numéricamente con tolerancia
            df_diferencias[col_comparar] = df_diferencias.apply(
                lambda x: f"{x[col_comparar]}*" if pd.notna(x[col_base]) and abs(x[col_comparar] - x[col_base]) > TOLERANCIA_DECIMAL else x[col_comparar], axis=1
            )
        else:
            # Comparar como cadenas, considerando NaN
            df_diferencias[col_comparar] = df_diferencias.apply(
                lambda x: f"{x[col_comparar]}*" if pd.notna(x[col_base]) and str(x[col_comparar]).strip() != str(x[col_base]).strip() else x[col_comparar], axis=1
            )

    # Seleccionar solo las columnas que queremos mostrar
    columnas_a_mostrar = [clave] + [col + '_comparar' for col in df_base.columns if col != clave]
    return df_diferencias[columnas_a_mostrar]

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

    # Mostrar el desplegable para seleccionar la columna clave
    clave = st.selectbox("Selecciona la columna que servirá como llave primaria para la comparación:", df_base.columns)

    if clave:
        # Verificar si los DataFrames son idénticos
        if df_base.equals(df_comparar):
            st.error("Los archivos son idénticos. No hay diferencias para resaltar.")
        elif df_base.columns.to_list() != df_comparar.columns.to_list():
            st.error("Los archivos no tienen las mismas columnas. Asegúrate de cargar archivos con las mismas columnas.")
        else:
            # Encontrar filas con diferencias y marcar celdas con un asterisco
            df_diferencias = encontrar_filas_con_diferencias(df_base, df_comparar, clave)

            # Mostrar el DataFrame con filas que tienen diferencias
            st.write("Información que tiene diferencias:")
            st.table(df_diferencias.style.applymap(resaltar_diferencias))

            # Resto del código para mostrar información y descargar resultados...
            # ...

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
