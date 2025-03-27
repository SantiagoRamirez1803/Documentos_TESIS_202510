import pandas as pd
# Cargar el dataset ORGINAL de hurto a personas 2022
data_hurto_personas_2022= pd.read_excel('HURTO A PERSONAS.xlsx', usecols="A:V", skiprows=10, nrows=351717)
data_hurto_personas_2022.head()

# Dimensión del dataset ORGINAL
data_hurto_personas_2022.shape
data_hurto_personas_2022.columns

# Filtrar por la ciudad de Bogotá D.C. INTERÉS
data_bogota = data_hurto_personas_2022.loc[data_hurto_personas_2022['Municipio'] == 'BOGOTÁ D.C. (CT)']

# Dimensión del dataset INTERÉS
data_bogota.shape

# conteo de los datos vacíos por atributo (COMPLETITUD)
data_bogota.isna().sum()

#Características variables
print(data_bogota.dtypes)

# conteos de una variable categórica para identificar anomalías (CONSISTENCIA)
data_bogota['Barrio'].value_counts()

# Eliminar filas donde Barrio sea "-" o esté vacío
data_bogota = data_bogota[~data_bogota["Barrio"].str.strip().isin(["", "-","NA"])]

# estadísticas básicas de una variable categórica
data_bogota['Barrio'].describe()

# ------------------------CAMBIOS DE TIPO DE DATOS (0:inicio)--------------------------)

#Cambiar el tipo de dato de una variable (fecha) obj to datetime
data_bogota['Fecha'] = pd.to_datetime(data_bogota['Fecha'], errors='coerce')
data_bogota['Fecha'].head()


""" NO CAMBIA EL FORMATO DE LA HORA """
#Cambiar el tipo de dato de una variable (hora) obj to datetime
data_bogota['Hora'] = pd.to_datetime(data_bogota['Hora'], format='%H:%M:%S', errors='coerce').dt.hour
data_bogota['Hora'].head(10)


# Crear la nueva columna de franjas horarias
def clasificar_hora(hora):
    if 6 <= hora < 12:
        return 'Mañana'
    elif 12 <= hora < 18:
        return 'Tarde'
    else:
        return 'Noche'

data_bogota['Franja_Horaria'] = data_bogota['Hora'].apply(clasificar_hora)

# Mostrar las primeras filas con la nueva categoría
print(data_bogota[['Hora', 'Franja_Horaria']].head())

data_bogota['Franja_Horaria'].value_counts() #Verificar el cambio de tipo de dato


# función para pasar el mes que están en letras a números
def mes_a_numero(mes):
    if mes=='ene.':
        numero='01'
    if mes=='feb.':
        numero='02'
    if mes=='mar.':
        numero='03'
    if mes=='abr.':
        numero='04'
    if mes=='may.':
        numero='05'
    if mes=='jun.':
        numero='06'
    if mes=='jul.':
        numero='07'
    if mes=='ago.':
        numero='08'
    if mes=='sep.':
        numero='09'
    if mes=='oct.':
        numero='10'
    if mes=='nov.':
        numero='11'
    if mes=='dic.':
        numero='12'
    return numero

data_bogota['MES'] = data_bogota['MES'].apply(mes_a_numero)
# Remove specific columns from data_bogota
columns_to_remove = ['Departamento', 'Profesión', 'Código DANE', 'DESCRIPCION_CONDUCTA']
data_bogota = data_bogota.drop(columns=columns_to_remove)
#data_bogota['MES'].value_counts() #Verificar el cambio de tipo de dato
# ------------------------CAMBIOS DE TIPO DE DATOS (1:fin)--------------------------)


#----------------------------------------------- Graficas--------------------------

import matplotlib.pyplot as plt
import seaborn as sns
# Contar la cantidad de delitos por mes
delitos_por_mes = data_bogota['MES'].value_counts().sort_index()

plt.figure(figsize=(10,5))
sns.barplot(x=delitos_por_mes.index, y=delitos_por_mes.values, palette="viridis")
plt.xlabel("Mes")
plt.ylabel("Cantidad de delitos")
plt.title("Distribución de delitos por mes")
plt.xticks(rotation=45)
plt.show()


# Contar el uso de cada tipo de arma
uso_armas = data_bogota['Arma empleada'].value_counts()
#data_bogota['Arma empleada'].describe()
# Graficar
plt.figure(figsize=(10,5))
sns.barplot(y=uso_armas.index, x=uso_armas.values, palette="cubehelix")
plt.xlabel("Cantidad de delitos")
plt.ylabel("Tipo de arma")
plt.title("Uso de armas en los delitos")
plt.show()

# Crear tabla de frecuencia
heatmap_data = data_bogota.pivot_table(index='Día', columns='Franja_Horaria', aggfunc='size', fill_value=0)
dias_ordenados = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
heatmap_data = heatmap_data.reindex(dias_ordenados)
# Graficar mapa de calor
plt.figure(figsize=(12,6))
sns.heatmap(heatmap_data, cmap="coolwarm", linewidths=0.5)
plt.xlabel("Franja horaria")
plt.ylabel("Día de la semana")
plt.title("Mapa de calor: delitos por hora y día de la semana")
plt.show()

#--------------------------------MAPA BOGOTÁ CON BARRIOS--------------------------------

import folium
import json
#Importar archivo de barrios json
# Cargar el archivo JSON
with open('barrios_prueba.json', 'r', encoding='utf-8') as f:
    barrios_json = json.load(f)

# Crear un mapa centrado en Bogotá
mapa_bogota = folium.Map(location=[4.7110, -74.0721], zoom_start=12)

# Añadir cada barrio al mapa
for barrio in barrios_json:
    # Verificar si el campo 'geo_shape' existe y no es None
    if barrio.get('geo_shape') is not None:
        geo_shape = barrio['geo_shape']
        
        # Verificar si el campo 'geometry' existe y no es None
        if geo_shape.get('geometry') is not None:
            # Asignar "Suba" a los valores desconocidos
            localidad_nombre = barrio.get('localidad', 'DESCONOCIDO')
            if localidad_nombre == 'DESCONOCIDO':
                localidad_nombre = 'SUBA'

            # Crear un GeoJSON temporal para cada barrio
            geojson_feature = {
                "type": "Feature",
                "geometry": geo_shape['geometry'],
                "properties": {
                    "barrio": barrio.get('barriocomu', 'Desconocido'),
                    "localidad": localidad_nombre,
                    "estado": barrio.get('estado', 'Desconocido')
                }
            }
            
            # Añadir el GeoJSON al mapa
            folium.GeoJson(
                geojson_feature,
                name=f"Barrio: {barrio.get('barriocomu', 'Desconocido')}",
                tooltip=folium.GeoJsonTooltip(fields=["barrio", "localidad", "estado"], aliases=["Barrio", "Localidad", "Estado"]),
                style_function=lambda x: {"fillColor": "blue", "color": "black", "weight": 1, "fillOpacity": 0.3}
            ).add_to(mapa_bogota)


# Guardar el mapa en un archivo HTML
mapa_bogota.save('mapa_bogota.html')

# Crear un DataFrame a partir del JSON
df_barrios = pd.DataFrame(barrios_json)
df_barrios['localidad'] = (df_barrios['localidad']
                           .replace('DESCONOCIDO', 'SUBA'))
df_barrios.head()


# SOLO SE CORRE EL SIGUIENTE CÓDIGO UNA VEZ (LA PRIMERA VEZ) PARA CORREGIR LOS NOMBRES DE LOS BARRIOS
"""
df_barrios['barriocomu'] = (df_barrios['barriocomu']
    .str.upper()    # Convertir a mayúsculas   
    .str.replace('_', ' ')   # Quitar guiones bajos
    .str.replace('[ÁÉÍÓÚ]', lambda x: x.group(0).translate(str.maketrans("ÁÉÍÓÚ", "AEIOU")), regex=True)  # Quitar tildes   
    .str.replace(r'^S\.C\.\s*', '', regex=True)  # Quitar iniciales "S.C."
    .str.replace(r'^S\.C\s*', '', regex=True)  # Quitar iniciales "S.C"
    .str.strip() # Quitar espacios extra
)
df_barrios['localidad'] = (df_barrios['localidad']
    .str.upper()    # Convertir a mayúsculas
)
# Convertir DataFrame a una lista de diccionarios
barrios_json_actualizado = df_barrios.to_dict(orient="records")

# Guardar el JSON corregido
with open("barrios_prueba.json", "w", encoding="utf-8") as f:
    json.dump(barrios_json_actualizado, f, ensure_ascii=False, indent=4)

with open('barrios_prueba.json', 'r', encoding='utf-8') as f:
    barrios_json = json.load(f)

# Crear el mapa y agregar los barrios (sin modificar nada más)
mapa_bogota = folium.Map(location=[4.7110, -74.0721], zoom_start=12)

# Añadir cada barrio al mapa
for barrio in barrios_json:
    # Verificar si el campo 'geo_shape' existe y no es None
    if barrio.get('geo_shape') is not None:
        geo_shape = barrio['geo_shape']
        
        # Verificar si el campo 'geometry' existe y no es None
        if geo_shape.get('geometry') is not None:
            # Crear un GeoJSON temporal para cada barrio
            geojson_feature = {
                "type": "Feature",
                "geometry": geo_shape['geometry'],
                "properties": {
                    "barrio": barrio.get('barriocomu', 'Desconocido'),
                    "localidad": barrio.get('localidad', 'Desconocido'),
                    "estado": barrio.get('estado', 'Desconocido')
                }
            }

            # Añadir el GeoJSON al mapa
            folium.GeoJson(
                geojson_feature,
                name=f"Barrio: {barrio.get('barriocomu', 'Desconocido')}",
                tooltip=folium.GeoJsonTooltip(fields=["barrio", "localidad", "estado"], aliases=["Barrio", "Localidad", "Estado"]),
                style_function=lambda x: {"fillColor": "blue", "color": "black", "weight": 1, "fillOpacity": 0.3}
            ).add_to(mapa_bogota)

mapa_bogota.save('mapa_bogota.html')
"""


# Verificar si las columnas existen en el DataFrame
if 'barriocomu' in df_barrios.columns and 'localidad' in df_barrios.columns:
    
    # Reemplazar valores NaN en la columna 'localidad'
    df_barrios['localidad'] = df_barrios['localidad'].fillna('DESCONOCIDO')
    
    # Agrupar por barrio y localidad
    barrios_unicos = df_barrios[['barriocomu', 'localidad']].drop_duplicates()
    
    # Renombrar columnas para claridad
    barrios_unicos.columns = ['Barrio', 'Localidad']
    
    # Mostrar el resultado
    print(barrios_unicos)
else:
    print("Las columnas 'barriocomu' o 'localidad' no existen en el archivo JSON.")


#-------------------- CRUCE DE CATEGORÍAS BARRIO PARA VERIFICAR SIMILITUDES --------------------------
# Función de levenshtein para distancia de caracteres. Si te genera un error correr (pip install python-Leveshtein)
from Levenshtein import distance as lev
# generar producto cruz de listas para matriz de levenshtein
import itertools

# Expresión regular para separar el nombre del barrio y el código de localidad
data_bogota['Localidad'] = data_bogota['Barrio'].str.extract(r'E-(\d{1,2})$', expand=True)  # Extrae el número
data_bogota['Barrio'] = data_bogota['Barrio'].str.replace(r'\s*E-\d{1,2}$', '', regex=True).str.strip()  # Quita el código del barrio

# Diccionario de localidades según el código E-
localidades_dict = {
    "1": "USAQUÉN",
    "2": "CHAPINERO",
    "3": "SANTA FE",
    "4": "SAN CRISTÓBAL",
    "5": "USME",
    "6": "TUNJUELITO",
    "7": "BOSA",
    "8": "KENNEDY",
    "9": "FONTIBÓN",
    "10": "ENGATIVÁ",
    "11": "SUBA",
    "12": "BARRIOS UNIDOS",
    "13": "TEUSAQUILLO",
    "14": "LOS MÁRTIRES",
    "15": "ANTONIO NARIÑO",
    "16": "PUENTE ARANDA",
    "17": "CANDELARIA",
    "18": "RAFAEL URIBE",
    "19": "CIUDAD BOLÍVAR",
    "20": "SUMAPAZ"
}

# Mapear los códigos de localidad a su nombre
data_bogota['Localidad'] = data_bogota['Localidad'].map(localidades_dict).fillna('DESCONOCIDO')  # Rellena NaN con 'DESCONOCIDO'
# Agrupar por barrio y localidad
barrios_unicos_hurto = data_bogota.groupby(['Barrio', 'Localidad']).size().reset_index(name='Cantidad')
barrios_unicos_hurto["Barrio"].head()
barrios_unicos["Barrio"].head()
# Crear una nueva columna combinada en ambos DataFrames:
barrios_unicos['Barrio_Localidad'] = barrios_unicos['Barrio'].str.strip() + "-" + barrios_unicos['Localidad'].str.strip()
barrios_unicos_hurto['Barrio_Localidad'] = barrios_unicos_hurto['Barrio'].str.strip() + "-" + barrios_unicos_hurto['Localidad'].str.strip()
barrios_unicos_hurto["Barrio_Localidad"].head()
barrios_unicos["Barrio_Localidad"].head()
# identificar todas las categorías
nombre_barrios_labUrbano=list(barrios_unicos['Barrio_Localidad'].unique())
len(nombre_barrios_labUrbano)

nombre_barrios_hurto=list(barrios_unicos_hurto['Barrio_Localidad'].unique())
len(nombre_barrios_hurto)

# crear cruce de las categorías
producto_cruz=list(itertools.product(nombre_barrios_labUrbano,nombre_barrios_hurto))
#producto_cruz[0:5]
# dataframe con los cruces
matriz_leven = pd.DataFrame(producto_cruz, columns =['nombre_barrios_labUrb', 'nombre_barrios_hurto'])
matriz_leven.head()

# Transformaciones
matriz_leven['nombre_barrios_hurto'] = (matriz_leven['nombre_barrios_hurto']
    .str.upper()    # Convertir a mayúsculas   
    .str.replace('_', ' ')   # Quitar guiones bajos
    .str.strip() # Quitar espacios al inicio y final
    #.str.replace(r'^S\.C\.\s*', '', regex=True)  # Quitar iniciales "S.C."
    #.str.replace(r'^S\.C\s*', '', regex=True)  # Quitar iniciales "S.C"
)
matriz_leven.head()
#matriz_leven.shape
#aplicar función de levenshtein
for i in range(len(matriz_leven)):
    matriz_leven.at[i,'Levenshtein']=lev(str(matriz_leven.at[i,'nombre_barrios_labUrb']),str(matriz_leven.at[i,'nombre_barrios_hurto']))
#pd.crosstab(matriz_leven['nombre_barrios_labUrb'],matriz_leven['nombre_barrios_hurto'],values=matriz_leven['Levenshtein'], aggfunc='sum')

#Comprobaciones
cantidad_ceros=(matriz_leven['Levenshtein']==0).sum()
cantidad_numeros_bajos=(matriz_leven['Levenshtein']<=1).sum()

data_bogota["Barrio_Localidad"] = data_bogota["Barrio"] + "-" + data_bogota["Localidad"]
# Crear un subconjunto con los barrios que están en ambas bases
barrios_coincidentes = set(barrios_unicos["Barrio_Localidad"]).intersection(set(barrios_unicos_hurto["Barrio_Localidad"]))

# Filtrar los datos de hurto para que solo contengan barrios que están en el mapa
data_bogota_filtrado = data_bogota[data_bogota['Barrio_Localidad'].isin(barrios_coincidentes)]

# --------------------------------PROCESO DE RECUPERACIÓN DE DATOS (PARETO) PARA NO PERDER TANTOS----------------------------------
# Obtener los barrios únicos de la base de hurtos (labUrbano ya se encuentra en barrios_unicos_hurto)
barrios_hurto_set = set(barrios_unicos_hurto["Barrio_Localidad"])
# Obtener los barrios que sí están en data_bogota_filtrado
barrios_filtrados_set = set(data_bogota_filtrado["Barrio_Localidad"].unique())

# Los barrios perdidos son aquellos que están en hurtos pero no en el DataFrame filtrado
barrios_no_coincidentes_set = barrios_hurto_set - barrios_filtrados_set

# Filtrar la base de hurtos para los barrios perdidos
barrios_no_coincidentes_hurto = barrios_unicos_hurto[~barrios_unicos_hurto['Barrio_Localidad'].isin(data_bogota_filtrado['Barrio_Localidad'])]

# Ordenar de mayor a menor cantidad de robos
barrios_no_coincidentes_hurto = barrios_no_coincidentes_hurto.sort_values(by="Cantidad", ascending=False)

# Seleccionar los top 150 barrios
top150_no_coincidentes = barrios_no_coincidentes_hurto.head(150)

# Crear una lista con los nombres de los barrios perdidos seleccionados
top150_no_coincidentes_list = top150_no_coincidentes['Barrio_Localidad'].tolist()

# Filtrar la matriz de Levenshtein para que solo incluya filas en que el barrio de la base de hurtos esté en el top 150 de los perdidos
matriz_no_coincidentes = matriz_leven[matriz_leven['nombre_barrios_hurto'].isin(top150_no_coincidentes_list)].copy()
# Ordenar la matriz (opcional, para tener un orden visual)
matriz_no_coincidentes = matriz_no_coincidentes.sort_values(by='Levenshtein', ascending=True)

# Para cada 'nombre_barrios_hurto', obtener la fila con menor distancia de Levenshtein
mejor_coincidencia_no_coincidentes = matriz_no_coincidentes.loc[
    matriz_no_coincidentes.groupby('nombre_barrios_hurto')['Levenshtein'].idxmin()
].reset_index(drop=True)

# Excluir aquellas coincidencias exactas (donde la distancia es 0)
mejor_coincidencia_no_coincidentes = mejor_coincidencia_no_coincidentes[mejor_coincidencia_no_coincidentes['Levenshtein'] > 0]
# Exportar a CSV para revisión manual
mejor_coincidencia_no_coincidentes.to_csv("comparacion_top150_no_coincidentes.csv", index=False)

# Diccionario de corrección de nombres de barrios
correccion_barrios = {
    "ABRAHAM LINCON-TUNJUELITO": "ABRAHAM LINCOLN-TUNJUELITO",
    "AEROPUERTO EL DORADO-DESCONOCIDO": "AEROPUERTO EL DORADO-FONTIBÓN",
    "ALAMEDA-SANTA FE": "LA ALAMEDA-SANTA FE",
    "ALCAZARES NORTE-BARRIOS UNIDOS": "LOS ALCAZARES NORTE-BARRIOS UNIDOS",
    "ALHAMBRA SECTOR NORTE-SUBA": "LA ALHAMBRA SECTOR NORTE-SUBA",
    "ALQUERIAS DE LA FRAGUA-KENNEDY": "ALQUERIA DE LA FRAGUA-KENNEDY",
    "ANTIGUO COUNTRY CLUB-CHAPINERO": "ANTIGUO COUNTRY-CHAPINERO",
    "CASABLANCA-KENNEDY": "CASABLANCA I-KENNEDY",
    "CEDRITOS LOS CAOBOS-USAQUÉN": "LOS CAOBOS-USAQUÉN",
    "CENTRO ADMINISTRATIVO-LA CANDELARIA": "CENTRO ADMINISTRATIVO-CANDELARIA",
    "CHAPINERO SUR OCC.-TEUSAQUILLO": "CHAPINERO OCCIDENTAL-TEUSAQUILLO",
    "CHAPINERO SUR OCCIDENTAL-TEUSAQUILLO": "CHAPINERO OCCIDENTAL-TEUSAQUILLO",
    "CIUDAD JARDIN SUR-ANTONIO NARIÑO": "CIUDAD JARDIN DEL SUR-ANTONIO NARIÑO",
    "CIUDAD JARDIN-SUBA": "CIUDAD JARDIN NORTE-SUBA",
    "CLARET-RAFAEL URIBE URIBE": "CLARET-RAFAEL URIBE",
    "DIANA TURBAY-RAFAEL URIBE URIBE": "DIANA TURBAY-RAFAEL URIBE",
    "DOCE DE OCTUBRE-BARRIOS UNIDOS": "12 DE OCTUBRE-BARRIOS UNIDOS",
    "EL CAMPIN (ESTADIO)-TEUSAQUILLO": "EL CAMPIN-TEUSAQUILLO",
    "EL ESPARTILLAL-CHAPINERO": "ESPARTILLAL-CHAPINERO",
    "EL MUELLE-ENGATIVÁ": "EL MUELLE I-ENGATIVÁ",
    "EL PINAR DE SUBA II SECTOR-SUBA": "EL PINAR DE SUBA II-SUBA",
    "EL REMANSO-PUENTE ARANDA": "REMANSO-PUENTE ARANDA",
    "EL RESTREPO-ANTONIO NARIÑO": "RESTREPO-ANTONIO NARIÑO",
    "EL RINCON DE SUBA-SUBA": "RINCON DE SUBA-SUBA",
    "EL TEJAR-PUENTE ARANDA": "TEJAR-PUENTE ARANDA",
    "FERIAS-ENGATIVÁ": "LAS FERIAS-ENGATIVÁ",
    "INDUSTRIAL PUENTE ARANDA-PUENTE ARANDA": "INDUSTRIAL CENTENARIO-PUENTE ARANDA",
    "JIMENEZ DE QUEZADA-BOSA":"JIMENEZ DE QUESADA-BOSA",
    "LA PORCIUNCULA-CHAPINERO":"PORCIUNCULA-CHAPINERO",
    "LA VERACRUZ-SANTA FE":"VERACRUZ-SANTA FE",
    "LOS MOLINOS DEL SUR-RAFAEL URIBE":"MOLINOS DEL SUR-RAFAEL URIBE",
    "MINUTO DE DIOS-ENGATIVÁ":"EL MINUTO DE DIOS-ENGATIVÁ",
    "ONCE DE NOVIEMBRE-BARRIOS UNIDOS":"11 DE NOVIEMBRE-BARRIOS UNIDOS",
    "PATIO BONITO I-KENNEDY":"PATIO BONITO I SECTOR-KENNEDY",
    "ROSALES-CHAPINERO":"LOS ROSALES-CHAPINERO",
    "SAN BLAS-SAN CRISTÓBAL":"SAN BLASS-SAN CRISTÓBAL",
    "SAN CRISTOBAL-SAN CRISTÓBAL":"SAN CRISTOBAL SUR-SAN CRISTÓBAL",
    "SOCIEGO SUR-RAFAEL URIBE":"SOSIEGO SUR-RAFAEL URIBE",
    "URB. TOBERIN-USAQUÉN":"TOBERIN-USAQUÉN",
    "VEINTE DE JULIO-SAN CRISTÓBAL":"20 DE JULIO-SAN CRISTÓBAL",
    "VILLA LUZ-ENGATIVÁ":"VILLALUZ-ENGATIVÁ",
    "ZONA INDUSTRIAL MONTEVIDEO-FONTIBÓN":"URB. INDUSTRIAL MONTEVIDEO-FONTIBÓN"
}

# Aplicar las correcciones de nombres en la base de datos de hurtos
data_bogota['Barrio_Localidad'] = data_bogota['Barrio_Localidad'].replace(correccion_barrios)
# Calcular los barrios coincidentes actualizados
barrios_coincidentes_actualizados = set(data_bogota["Barrio_Localidad"]).intersection(set(barrios_unicos["Barrio_Localidad"]))

data_bogota_filtrado= data_bogota[data_bogota["Barrio_Localidad"].isin(barrios_coincidentes_actualizados)]
# ------------------------------------- FIN PROCESO DE RECUPERACIÓN--------------------------------------------------------

# ------------------------------------- PARETO DE BARRIOS PERDIDOS--------------------------------------------------------
# Total de robos (en todas las categorías: coincidentes y no coincidentes)
total_robos = barrios_unicos_hurto["Cantidad"].sum()
print("Total de robos:", total_robos)
# Calcular el porcentaje que representa cada barrio del total de robos
top150_no_coincidentes["Porcentaje"] = top150_no_coincidentes["Cantidad"] / total_robos * 100

# Calcular el porcentaje acumulado (ordenados de mayor a menor cantidad)
top150_no_coincidentes = top150_no_coincidentes.sort_values(by="Cantidad", ascending=False)
top150_no_coincidentes["Porcentaje_acumulado"] = top150_no_coincidentes["Porcentaje"].cumsum()

import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(12,6))
ax1 = plt.gca()

# Gráfico de barras para la cantidad de robos por barrio no coincidente
sns.barplot(data=top150_no_coincidentes, x="Barrio_Localidad", y="Cantidad", color="C0", ax=ax1)
ax1.set_xlabel("Barrio - Localidad")
ax1.set_ylabel("Número de Robos", color="C0")
ax1.tick_params(axis="x", rotation=90)
ax1.tick_params(axis="y", labelcolor="C0")

# Eje secundario para el porcentaje acumulado
ax2 = ax1.twinx()
ax2.plot(top150_no_coincidentes["Barrio_Localidad"], top150_no_coincidentes["Porcentaje_acumulado"],
         color="C1", marker="D", ms=7)
ax2.set_ylabel("Porcentaje Acumulado (%)", color="C1")
ax2.tick_params(axis="y", labelcolor="C1")

# Línea horizontal de referencia al 80% (u otro umbral)
ax2.axhline(80, color="gray", linestyle="--", linewidth=1)

plt.title("Análisis de Pareto: Robos en Barrios No Coincidentes (Top 150) sobre Total de Robos")
plt.tight_layout()
plt.show()
#------------------------------------ FIN PARETO ---------------------------------------
data_bogota_filtrado=data_bogota_filtrado.drop(columns=['Municipio', "Hora", "Barrio", "Fecha", "Estado civil", "Clase de empleado", "Escolaridad"])

## -- CANTIDAD HURTOS POR BARRIO Y POR DÍA DE LA SEMANA --
# Crear columnas dummy para cada día de la semana
dias_dummies = pd.get_dummies(data_bogota_filtrado['Día'])
# Agregar la columna de Barrio_Localidad para agrupar
data_bogota_filtrado_dias = pd.concat([data_bogota_filtrado[['Barrio_Localidad']], dias_dummies], axis=1)
# Agrupar por Barrio_Localidad y contar hurtos por día de la semana
data_hurtos_por_dia = data_bogota_filtrado_dias.groupby('Barrio_Localidad').sum().reset_index()


data_hurtos_por_barrio = data_bogota_filtrado.groupby(['Barrio_Localidad']).size().reset_index(name='Cantidad')
# Unir con el dataframe principal de hurtos por barrio
data_hurtos_por_barrio = pd.merge(data_hurtos_por_barrio, data_hurtos_por_dia, on="Barrio_Localidad", how="left")



# Crear columna combinada para el cruce
df_barrios["Barrio_Localidad"] = df_barrios["barriocomu"] + "-" + df_barrios["localidad"]
# Extraer las coordenadas de los polígonos
df_barrios["Coordenadas"] = df_barrios["geo_shape"].apply(lambda x: x["geometry"]["coordinates"] if x and "geometry" in x else None)
# Eliminar duplicados en df_barrios, conservando solo una fila por barrio-localidad
df_barrios = df_barrios.drop_duplicates(subset=["Barrio_Localidad"])

# Unir DataFrames para obtener las coordenadas solo de los barrios presentes en los robos
data_hurtos_por_barrio = pd.merge(data_hurtos_por_barrio, df_barrios[["Barrio_Localidad", "Coordenadas"]], on="Barrio_Localidad", how="left")
data_hurtos_por_barrio.to_csv("HURTOS POR BARRIO 2022.csv", index=False)
#FIN DEL CÓDIGO
