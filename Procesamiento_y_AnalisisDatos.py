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

for barrio in barrios_json:
    if barrio.get('geo_shape') is not None:
        geo_shape = barrio['geo_shape']
        if geo_shape.get('geometry') is not None:
            geojson_feature = {
                "type": "Feature",
                "geometry": geo_shape['geometry'],
                "properties": {
                    "barrio": barrio.get('barriocomu', 'Desconocido'),  # Ahora usa los nombres corregidos
                    "localidad": barrio.get('localidad', 'Desconocido'),
                    "estado": barrio.get('estado', 'Desconocido')
                }
            }
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

# Diccionario de localidades según el código E- (puedes ajustarlo si tienes más localidades)
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
    "17": "LA CANDELARIA",
    "18": "RAFAEL URIBE URIBE",
    "19": "CIUDAD BOLÍVAR",
    "20": "SUMAPAZ"
}

# Mapear los códigos de localidad a su nombre
data_bogota['Localidad'] = data_bogota['Localidad'].map(localidades_dict).fillna('DESCONOCIDO')  # Rellena NaN con 'DESCONOCIDO'
# Agrupar por barrio y localidad
barrios_unicos_hurto = data_bogota.groupby(['Barrio', 'Localidad']).size().reset_index(name='Cantidad')
barrios_unicos_hurto["Barrio"].head()
barrios_unicos["Barrio"].head()
# identificar todas las categorías
nombre_barrios_labUrbano=list(barrios_unicos['Barrio'])
len(nombre_barrios_labUrbano)

nombre_barrios_hurto=list(barrios_unicos_hurto['Barrio'])
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
promedio_levenshtein=matriz_leven['Levenshtein'].mean()
minimo_levenshtein=matriz_leven['Levenshtein'].min()
cantidad_ceros=(matriz_leven['Levenshtein']==0).sum()
cantidad_numeros_bajos=(matriz_leven['Levenshtein']<=1).sum()


# Crear un subconjunto con los barrios que están en ambas bases
barrios_coincidentes = set(barrios_unicos["Barrio"]).intersection(set(barrios_unicos_hurto["Barrio"]))

# Filtrar los datos de hurto para que solo contengan barrios que están en el mapa
data_bogota_filtrado = data_bogota[data_bogota['Barrio'].isin(barrios_coincidentes)]

# Agrupar hurtos por barrio y localidad
hurtos_por_barrio = data_bogota_filtrado.groupby(['Barrio', 'Localidad']).size().reset_index(name='Cantidad')

# Crear un mapa centrado en Bogotá
mapa_hurtos = folium.Map(location=[4.7110, -74.0721], zoom_start=12)

# Diccionario para acceder rápido a los datos de hurtos
dict_hurtos = hurtos_por_barrio.set_index('Barrio')['Cantidad'].to_dict()

# Cargar el JSON actualizado con los barrios
with open('barrios_prueba.json', 'r', encoding='utf-8') as f:
    barrios_json = json.load(f)

# Función para determinar el color según la cantidad de hurtos
def color_por_hurtos(cantidad):
    if cantidad is None:
        return "gray"  # Barrios sin información
    elif cantidad < 50:
        return "green"
    elif cantidad < 200:
        return "orange"
    else:
        return "red"

# Agregar barrios al mapa con color según la cantidad de hurtos
for barrio in barrios_json:
    if barrio.get('geo_shape') and barrio['geo_shape'].get('geometry'):
        nombre_barrio = barrio.get('barriocomu', 'Desconocido').upper()
        cantidad_hurtos = dict_hurtos.get(nombre_barrio, None)  # Obtener cantidad de hurtos

        # Crear GeoJSON
        folium.GeoJson(
            barrio['geo_shape']['geometry'],
            name=f"Barrio: {nombre_barrio}",
            tooltip=f"{nombre_barrio} ({barrio.get('localidad', 'Desconocido')})<br> Hurtos: {cantidad_hurtos if cantidad_hurtos else 'No disponible'}",
            style_function=lambda x, cant=cantidad_hurtos: {
                "fillColor": color_por_hurtos(cant),
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.6
            }
        ).add_to(mapa_hurtos)

# Guardar el mapa
mapa_hurtos.save("mapa_hurtos.html")
#FIN DEL CÓDIGO
