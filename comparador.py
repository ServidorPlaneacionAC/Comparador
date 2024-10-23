import streamlit as st
import pandas as pd
import base64
from openpyxl.styles import PatternFill

# Tolerancia para la comparación de números decimales
TOLERANCIA_DECIMAL = 1e-9

# Función para encontrar filas con diferencias y marcar las celdas con un asterisco
def encontrar_filas_con_diferencias(df_base, df_comparar, columna_llave):
    # Establecer la columna llave como índice
    df_base = df_base.set_index(columna_llave)
    df_comparar = df_comparar.set_index(columna_llave)

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

# Función para resaltar diferencias
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

# Título
st.title("Comparador de Datos Maestros")

# Para subir el archivo base en Excel
archivo_base = st.file_uploader("Cargar archivo base (base de datos)", type=["xlsx"])

# Para subir el archivo a comparar en Excel
archivo_comparar = st.file_uploader("Cargar archivo a comparar", type=["xlsx"])

columna_llave = None

if archivo_base and archivo_comparar:
    # Cargar los archivos
    df_base = pd.read_excel(archivo_base)
    df_comparar = pd.read_excel(archivo_comparar)

    # Verificar si los archivos tienen las mismas columnas
    if df_base.columns.to_list() != df_comparar.columns.to_list():
        st.error("Los archivos no tienen las mismas columnas. Asegúrate de cargar archivos con las mismas columnas.")
    else:
        # Selección de la columna llave
        columna_llave = st.selectbox("Seleccione la columna que se utilizará como llave primaria para la comparación:", df_base.columns)

        # Verificar que la columna llave haya sido seleccionada
        if columna_llave:
            # Verificar si los DataFrames son idénticos
            if df_base.equals(df_comparar):
                st.error("Los archivos son idénticos. No hay diferencias para resaltar.")
            else:
                # Encontrar filas con diferencias y marcarlas
                df_diferencias = encontrar_filas_con_diferencias(df_base, df_comparar, columna_llave)

                # Mostrar el DataFrame con filas que tienen diferencias
                st.write("Información que tiene diferencias:")
                st.table(df_diferencias.style.applymap(resaltar_diferencias))

                # Botón para descargar la información en un archivo Excel con resaltado
                if st.button("Descargar información en Excel con resaltado"):
                    # Crear un objeto ExcelWriter para escribir en un solo archivo Excel
                    with pd.ExcelWriter("informacion_comparada.xlsx", engine='openpyxl') as writer:
                        # Escribir el DataFrame de diferencias en una pestaña
                        df_diferencias.to_excel(writer, sheet_name='Diferencias', index=True)

                        # Obtener el objeto Workbook para aplicar el formato
                        workbook = writer.book
                        sheet = workbook['Diferencias']

                        # Aplicar formato de resaltado a las celdas con diferencias
                        for idx, row in enumerate(sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=2, max_col=sheet.max_column)):
                            for cell in row:
                                if '*' in str(cell.value):
                                    cell.fill = PatternFill(start_color='FFFF0000', end_color='FFFF0000', fill_type='solid')

                    # Enlace para descargar el archivo Excel
                    st.markdown(
                        get_binary_file_downloader_html("informacion_comparada.xlsx", 'Archivo Excel con resaltado'),
                        unsafe_allow_html=True
                    )
else:
    st.info("Por favor, cargue ambos archivos para comenzar la comparación.")
