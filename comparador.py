import streamlit as st
import pandas as pd
import base64

# Tolerancia para la comparación de números decimales
TOLERANCIA_DECIMAL = 1e-9

# Función para encontrar filas con diferencias y marcar las celdas con un asterisco
def encontrar_filas_con_diferencias(df_base, df_comparar):
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

# Función para aplicar formato a las celdas con diferencias
def resaltar_diferencias(val):
    if '*' in str(val):
        return 'background-color: red'
    else:
        return ''

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

    # Verificar si los DataFrames son idénticos
    if df_base.equals(df_comparar):
        st.error("Los archivos son idénticos. No hay diferencias para resaltar.")
    elif df_base.columns.to_list() != df_comparar.columns.to_list():
        st.error("Los archivos no tienen las mismas columnas. Asegúrate de cargar archivos con las mismas columnas.")
    else:
        # Encontrar filas con diferencias y marcar celdas con un asterisco
        df_diferencias = encontrar_filas_con_diferencias(df_base, df_comparar)

        # Encontrar filas faltantes en comparación al archivo base
        df_faltantes = df_base.loc[~df_base.index.isin(df_comparar.index)]

        # Encontrar filas en el archivo a comparar que no están en el archivo base
        df_filas_en_comparar_no_en_base = df_comparar.loc[~df_comparar.index.isin(df_base.index)]

        # Mostrar el DataFrame con filas que tienen diferencias
        st.write("Informacion que tiene diferencias:")
        st.dataframe(df_diferencias.style.applymap(resaltar_diferencias))

        # ... (código existente)

        # Botón para descargar la información en un archivo Excel
        if st.button("Descargar información en Excel"):
            # Crear un objeto ExcelWriter para escribir en un solo archivo Excel
            with pd.ExcelWriter("informacion_comparada.xlsx", engine='openpyxl') as writer:
                # Escribir cada DataFrame en una pestaña diferente
                df_diferencias.to_excel(writer, sheet_name='Diferencias', index=True, na_rep='', float_format="%.2f", header=True, startrow=1, startcol=1, engine='openpyxl', freeze_panes=(2, 1))
                df_filas_en_comparar_no_en_base.to_excel(writer, sheet_name='Filas_en_comparar_no_en_base', index=True, na_rep='', float_format="%.2f", header=True, startrow=1, startcol=1, engine='openpyxl', freeze_panes=(2, 1))
                df_faltantes.to_excel(writer, sheet_name='Faltantes_en_base', index=True, na_rep='', float_format="%.2f", header=True, startrow=1, startcol=1, engine='openpyxl', freeze_panes=(2, 1))

            # Enlace para descargar el archivo Excel
            st.markdown(
                get_binary_file_downloader_html("informacion_comparada.xlsx", 'Archivo Excel'),
                unsafe_allow_html=True
            )
