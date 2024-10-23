import streamlit as st
import pandas as pd
import base64

# Función para encontrar filas con diferencias y retornar las columnas relevantes
def encontrar_filas_con_diferencias(df_base, df_comparar, llave_primaria):
    # Comparar solo las columnas que no son la llave primaria
    columnas_a_comparar = df_comparar.columns.difference([llave_primaria])

    # Crear un DataFrame para almacenar las diferencias
    df_diferencias = df_comparar[[llave_primaria]].copy()

    for col in columnas_a_comparar:
        # Comparar solo si ambos valores no son None o espacios en blanco
        df_diferencias[col] = df_comparar.apply(
            lambda x: x[col] if pd.notna(x[col]) and x[col] != '' and (x[llave_primaria] not in df_base[llave_primaria].values or (x[col] != df_base.loc[df_base[llave_primaria] == x[llave_primaria], col].values[0] if x[llave_primaria] in df_base[llave_primaria].values else True)) else None,
            axis=1
        )
    
    # Filtrar para eliminar filas donde todas las comparaciones son None
    df_diferencias = df_diferencias.dropna(how='all', subset=columnas_a_comparar)
    
    return df_diferencias

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

    # Limpiar los nombres de las columnas
    df_base.columns = df_base.columns.str.strip()
    df_comparar.columns = df_comparar.columns.str.strip()

    # Mostrar información de los DataFrames
    st.write("DataFrame Base:")
    st.write(df_base)
    st.write("DataFrame a Comparar:")
    st.write(df_comparar)

    # Seleccionar la columna clave para comparación
    llave_primaria = st.selectbox("Selecciona la columna llave primaria:", df_comparar.columns)

    # Verificar si la llave primaria está en ambos DataFrames
    if llave_primaria not in df_base.columns:
        st.error(f"La columna '{llave_primaria}' no se encuentra en el archivo base.")
    elif llave_primaria not in df_comparar.columns:
        st.error(f"La columna '{llave_primaria}' no se encuentra en el archivo a comparar.")
    else:
        st.write(f"La llave primaria seleccionada es: {llave_primaria}")

        # Verificar si los DataFrames son idénticos
        if df_base.equals(df_comparar):
            st.error("Los archivos son idénticos. No hay diferencias para resaltar.")
        elif df_base.columns.to_list() != df_comparar.columns.to_list():
            st.error("Los archivos no tienen las mismas columnas. Asegúrate de cargar archivos con las mismas columnas.")
        else:
            # Encontrar filas con diferencias y omitir None y espacios en blanco
            df_diferencias = encontrar_filas_con_diferencias(df_base, df_comparar, llave_primaria)

            # Mostrar el DataFrame con filas que tienen diferencias
            if not df_diferencias.empty:
                st.write("Información con diferencias:")
                st.table(df_diferencias)
            else:
                st.write("No se encontraron diferencias significativas.")

# Función para generar un enlace de descarga de un archivo binario
def get_binary_file_downloader_html(file_path, file_label='Archivo'):
    with open(file_path, 'rb') as f:
        data = f.read()
        base64_encoded = base64.b64encode(data).decode()
        return f'<a href="data:application/octet-stream;base64,{base64_encoded}" download="{file_path}">{file_label}</a>'
