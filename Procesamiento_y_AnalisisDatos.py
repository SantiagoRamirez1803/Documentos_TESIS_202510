
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
# estadísticas básicas de una variable categórica
data_bogota['Barrio'].describe()

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
#data_bogota['MES'].value_counts() #Verificar el cambio de tipo de dato
"""GRÁFICAS"""
import matplotlib.pyplot as plt
import seaborn as sns
# Contar la cantidad de delitos por mes
delitos_por_mes = data_bogota['MES'].value_counts().sort_index()


# Graficar
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


# Guardar el mapa en un archivo HTML
mapa_bogota.save('mapa_bogota.html')

# Crear un DataFrame a partir del JSON
df_barrios = pd.DataFrame(barrios_json)
df_barrios.head()
# Verificar si el campo 'barriocomu' existe en el DataFrame
if 'barriocomu' in df_barrios.columns:
    # Extraer los nombres de los barrios únicos y contar su frecuencia
    barrios_unicos = df_barrios['barriocomu'].value_counts().reset_index()
    
    # Renombrar las columnas del DataFrame resultante
    barrios_unicos.columns = ['Barrio', 'Cantidad']
    
    # Mostrar el DataFrame con los barrios únicos y su cantidad
    print(barrios_unicos)
else:
    print("El campo 'barriocomu' no existe en el archivo JSON.")


#-------------------- CRUCE DE CATEGORÍAS BARRIO PARA VERIFICAR SIMILITUDES --------------------------
# Función de levenshtein para distancia de caracteres. Si te genera un error correr (pip install python-Leveshtein)
from Levenshtein import distance as lev
# generar producto cruz de listas para matriz de levenshtein
import itertools


barrios_unicos["Barrio"].head()
# identificar todas las categorías
nombre_barrios_labUrbano=list(barrios_unicos['Barrio'].unique())
len(nombre_barrios_labUrbano)

nombre_barrios_hurto=list(data_bogota['Barrio'].unique())
len(nombre_barrios_hurto)

# crear cruce de las categorías
producto_cruz=list(itertools.product(nombre_barrios_labUrbano,nombre_barrios_hurto))
print(producto_cruz)

#FIN DEL CÓDIGO