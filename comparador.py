import streamlit as st
import pandas as pd
import base64
from openpyxl.styles import PatternFill

# Tolerancia para la comparación de números decimales
TOLERANCIA_DECIMAL = 1e-9

# Función para encontrar filas con diferencias y marcar las celdas con un asterisco
def encontrar_filas_con_diferencias(df_base, df_comparar, clave):
    # Convertir a cadenas para evitar problemas de tipo de datos
    df_base[clave] = df_base[clave].astype(str)
    df_comparar[clave] = df_comparar[clave].astype(str)

    # Identificar las filas que existen en el archivo a comparar pero no en la base de datos
    filas_nuevas = df_comparar.merge(df_base, how='outer', on=clave, indicator=True).loc[lambda x: x['_merge'] == 'left_only'].drop(
        columns=['_merge'])

    # Obtener el DataFrame con filas que tienen diferencias
    df_diferencias = df_comparar[df_comparar[clave].isin(filas_nuevas[clave])].copy()

    # Marcar las celdas con un asterisco solo donde la información no es igual al archivo base
    for col in df_comparar.columns:
        if col == clave:  # No comparar la columna clave
            continue
        if pd.api.types.is_numeric_dtype(df_comparar[col]) and pd.api.types.is_numeric_dtype(df_base[col]):
            df_diferencias[col] = df_diferencias.apply(
                lambda x: f"{x[col]}*" if x[clave] in df_base[clave].values and abs(x[col] - df_base.loc[df_base[clave] == x[clave], col].values[0]) > TOLERANCIA_DECIMAL else x[col], axis=1)
        else:
            # Comparar valores y manejar NaN
            df_diferencias[col] = df_diferencias.apply(
                lambda x: f"{x[col]}*" if x[clave] in df_base[clave].values and pd.notna(x[col]) and pd.notna(df_base.loc[df_base[clave] == x[clave], col].values[0]) and x[col] != df_base.loc[df_base[clave] == x[clave], col].values[0] else x[col], axis=1)

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
