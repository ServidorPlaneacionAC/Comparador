import streamlit as st
import pandas as pd
import os

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

# Titulo
st.title("Comparador de Datos Maestros")

# Para subir el archivo base en Excel
archivo_base = st.file_uploader("Cargar archivo base (base de datos)", type=["xlsx"])

# Para subir el archivo a comparar en Excel
archivo_comparar = st.file_uploader("Cargar archivo a comparar", type=["xlsx"])

if archivo_base and archivo_comparar:
    # Cargar los archivos
    df_base = pd.read_excel(archivo_base)  # Deja que pandas elija el motor automáticamente
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
        st.dataframe(df_diferencias.style.applymap(lambda x: 'background-color: red' if '*' in str(x) else ''))

        # Botón para mostrar las filas en el archivo base correspondientes a las diferencias
        if st.button("Mostrar información del archivo base correspondiente a las diferencias"):
            st.write("Información del archivo base correspondiente a las diferencias:")
            # Filtrar el DataFrame base solo para las filas que tienen diferencias en el archivo a comparar
            df_base_diferencias = df_base[df_base.index.isin(df_diferencias.index)].copy()

            # Marcar las celdas con un asterisco solo donde la información no es igual al archivo a comparar
            for col in df_base.columns:
                if pd.api.types.is_numeric_dtype(df_base[col]) and pd.api.types.is_numeric_dtype(df_comparar[col]):
                    df_base_diferencias[col] = df_base_diferencias.apply(lambda x: f"{x[col]}*" if x.name in df_comparar.index and abs(x[col] - df_comparar.at[x.name, col]) > TOLERANCIA_DECIMAL else x[col], axis=1)
                else:
                    df_base_diferencias[col] = df_base_diferencias.apply(lambda x: f"{x[col]}*" if x.name in df_comparar.index and x[col] != df_comparar.at[x.name, col] else x[col], axis=1)

            st.dataframe(df_base_diferencias)

        # Botón para mostrar las filas en el archivo a comparar que no están en el archivo base
        if st.button("Mostrar informacion nueva en comparar "):
            st.write("Informacion en el archivo a comparar que no está en el archivo base:")
            st.dataframe(df_filas_en_comparar_no_en_base)

        # Botón para mostrar la información faltante en comparación al archivo base
        if st.button("Mostrar información faltante en comparación al archivo base"):
            st.write("Información faltante en comparación al archivo base:")
            st.dataframe(df_faltantes)

        # Botón para descargar toda la información en un solo archivo Excel
        if st.button("Descargar información"):
            # Cambiar la ruta de descargas a D:\acwagavilan\Desktop\Joy
            ruta_descargas = os.path.join("D:", "acwagavilan", "Desktop", "Joy")

            # Asegurarse de que la carpeta de descargas exista, si no, crearla
            if not os.path.exists(ruta_descargas):
                os.makedirs(ruta_descargas)

            ruta_completa = os.path.join(ruta_descargas, "comparacion_datos_maestros.xlsx")

            with pd.ExcelWriter(ruta_completa, engine='xlsxwriter') as writer:
                # Escribir cada DataFrame en una pestaña diferente
                df_diferencias.to_excel(writer, sheet_name='Con Diferencias', index=False)
                df_faltantes.to_excel(writer, sheet_name='Faltantes en Base', index=False)
                df_filas_en_comparar_no_en_base.to_excel(writer, sheet_name='Nuevas en Comparar', index=False)
                df_base[df_base.index.isin(df_diferencias.index)].to_excel(writer, sheet_name='Archivo Base', index=False)  # Agregar hoja con el archivo base

            # Abrir el libro de trabajo y obtener la hoja de trabajo 'Con Diferencias'
            libro_trabajo = pd.ExcelFile(ruta_completa)
            hoja_diferencias = libro_trabajo.parse('Con Diferencias')

            # Crear un formato de resaltado para las celdas que contienen un asterisco
            formato_resaltado = libro_trabajo.book.add_format({'bg_color': 'red'})

            # Obtener el objeto de la hoja de trabajo
            hoja_objeto = libro_trabajo.book.sheet_by_name('Con Diferencias')

            # Obtener el objeto de la hoja de trabajo para la primera hoja
            hoja_objeto = libro_trabajo.book.sheet_by_index(0)

            # Obtener el índice de la columna que contiene diferencias
            col_index = hoja_objeto.row(0).index(b'*'.encode())

            # Obtener el número de filas en la hoja
            num_filas = hoja_objeto.nrows

            # Iterar sobre las filas y resaltar las celdas que contienen un asterisco
            for fila_index in range(1, num_filas):
                hoja_diferencias.iloc[fila_index - 1:fila_index, :].style.applymap(lambda x: 'background-color: red' if '*' in str(x) else '')

            # Guardar el formato
            libro_trabajo.save()

            # Mostrar en Streamlit el enlace para descargar el archivo Excel
            st.success(f"La comparación se ha guardado en un archivo Excel. Puedes descargarlo [aquí]({ruta_completa}).")
