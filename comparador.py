import pandas as pd
import streamlit as st

def encontrar_filas_con_diferencias(df_base, df_comparar, columna_llave):
    # Filtrar los DataFrames con base en la columna llave
    df_base_filtrado = df_base.set_index(columna_llave)
    df_comparar_filtrado = df_comparar.set_index(columna_llave)

    # Crear un DataFrame vacío para almacenar las diferencias
    df_diferencias = pd.DataFrame(index=df_comparar_filtrado.index)

    # Comparar columna por columna
    for col in df_comparar_filtrado.columns:
        if col in df_base_filtrado.columns:  # Asegurarse de que la columna exista en ambos DataFrames
            df_diferencias[col] = df_comparar_filtrado.apply(
                lambda x: f"{x[col]}*" if pd.notna(x[col]) and pd.notna(df_base_filtrado.at[x.name, col]) and x[col] != df_base_filtrado.at[x.name, col] else x[col], 
                axis=1
            )

    return df_diferencias

def resaltar_diferencias(val):
    # Resaltar las diferencias con un fondo amarillo
    color = 'background-color: yellow' if isinstance(val, str) and val.endswith('*') else ''
    return color

# Función principal de la aplicación Streamlit
def main():
    # Cargar los DataFrames de ejemplo
    df_base = pd.DataFrame({
        'ID': [1, 2, 3],
        'Nombre': ['Juan', 'Ana', 'Pedro'],
        'Edad': [30, 25, 40]
    })

    df_comparar = pd.DataFrame({
        'ID': [1, 2, 3],
        'Nombre': ['Juan', 'Ana', 'Pablo'],
        'Edad': [30, 26, 40]
    })

    # Pedir al usuario que seleccione la columna llave
    columnas_disponibles = df_base.columns.tolist()
    columna_llave = st.selectbox("Seleccione la columna llave para la comparación:", columnas_disponibles)

    # Verificar que la columna llave seleccionada sea válida
    if columna_llave:
        # Encontrar las filas con diferencias
        df_diferencias = encontrar_filas_con_diferencias(df_base, df_comparar, columna_llave)

        # Mostrar el DataFrame de diferencias con estilo
        df_estilizado = df_diferencias.style.applymap(resaltar_diferencias)

        # Mostrar en la aplicación
        st.write("Resultado de la comparación:")
        st.dataframe(df_estilizado)

if __name__ == "__main__":
    main()
