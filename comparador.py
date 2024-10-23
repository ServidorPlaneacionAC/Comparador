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

    # Crear un DataFrame solo con las diferencias
    diferencias = {}
    for col in df_base.columns:
        if col == clave:
            continue
        
        col_comparar = col + '_comparar'
        col_base = col + '_base'
        
        # Comparar y almacenar las diferencias
        diferencias[col] = df_diferencias.apply(
            lambda x: x[col_comparar] if pd.notna(x[col_base]) and (
                (pd.api.types.is_numeric_dtype(df_base[col]) and abs(x[col_comparar] - x[col_base]) > TOLERANCIA_DECIMAL) or
                (str(x[col_comparar]).strip() != str(x[col_base]).strip())
            ) else None, axis=1
        )
    
    # Crear un DataFrame solo con la columna clave y las diferencias
    df_resultado = pd.DataFrame({clave: df_diferencias[clave]})
    for col, dif in diferencias.items():
        df_resultado[col] = dif
    
    # Filtrar las filas donde hay diferencias
    df_resultado = df_resultado.dropna(how='all', subset=df_resultado.columns[1:])
    
    return df_resultado

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
            st.dataframe(df_diferencias)  # Muestra el DataFrame de diferencias

# Botón para descargar la información en un archivo Excel
if st.button("Descargar información en Excel"):
    # Crear un objeto ExcelWriter para escribir en un solo archivo Excel
    with pd.ExcelWriter("informacion_comparada.xlsx", engine='openpyxl') as writer:
        # Escribir cada DataFrame en una pestaña diferente
        df_diferencias.to_excel(writer, sheet_name='Diferencias', index=True)

    # Enlace para descargar el archivo Excel
    st.markdown(
        get_binary_file_downloader_html("informacion_comparada.xlsx", 'Archivo Excel con diferencias'),
        unsafe_allow_html=True
    )
