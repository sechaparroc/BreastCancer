# -*- coding: utf-8 -*-
"""
Created on Sun May 15 12:38:05 2022

@author: sebchaparr
"""

#1. Leemos los archivos que necesitamos
import pandas as pd
import os
import re

#Registros de muertes dane

path = os.path.join(os.curdir, 'data', 'nofetal2020.csv')
raw_data = pd.read_csv(path, sep=',', encoding='ISO-8859-1',
                 dtype = {
                     #Leemos las siguientes variables como string
                     'SEXO' : str,
                     'GRU_ED2' : str,
                     'NIVEL_EDU' : str,
                     'IDPERTET' : str,
                     'CODPRES' : str,
                     'CODPTORE' : str,
                     'CODMUNRE' : str,
                     'AREA_RES' : str,
                     'SEG_SOCIAL' : str,
                 })

#Codigo de departamentos y municipios

path = os.path.join(os.curdir, 'data', 'listado_municipios.csv')
#Set proper encoding 
munic_codes = pd.read_csv(path, sep=',', encoding='ISO-8859-1', dtype = str)


#Codigo de los registros de las distintas muertes


path = os.path.join(os.curdir, 'data', 'lista_105.csv')
#Set proper encoding 
death_codes = pd.read_csv(path, sep=',', encoding='ISO-8859-1', dtype = str)



#CODPRES País de residencia habitual del fallecido - Solo Colombia - 170
"""
CODPRES País de residencia habitual del fallecido, cuando
residía en un país diferente a Colombia (para
muerte fetal o de menor de un año el de la
madre) Código, según listado de países ISO
3166/2
"""
filtered_data = raw_data[raw_data["CODPRES"] == "170"] # SOlo colombia
filtered_data = filtered_data.drop(columns=["CODPRES"])



#Elegimos solo las columnas que nos interesan
filtered_cols = [
    "SEXO", 
    "GRU_ED2",   #Grupo de edad por categorias 
    "NIVEL_EDU", #Ultimo nivel educativo
    "IDPERTET",  #Etnia a la que pertenece la persona 
    #De las variables de ubicacion solo dejamos el lugar de residencia
    "CODPRES",  #Pais de residencia (nos interesa colombia)
    "CODPTORE", #Departamento de residencia  
    "CODMUNRE", #Municipio de Residencia
    "AREA_RES", #Categoria de lugar de Residencia Ej. Rural
    "SEG_SOCIAL", #Quizas nos sirve para definir algo?
    "CAU_HOMOL" #Causa de muerte segun la lista 105 de colombia
    ]

filtered_data = raw_data[filtered_cols]

# Agrupamos por todas las categorias
#2. Agrupamos por muertes
filtered_data = filtered_data.groupby(
    filtered_data.columns.tolist()).size().reset_index().rename(columns={0:'Numero_Registros'})



#3. Convertimos los codigos en descripciones mas intuitivas

#3.1 SEXO Sexo del fallecido 1 = Masculino 2 = Femenino 3 = Indeterminado
filtered_data["SEXO"] = filtered_data["SEXO"].map({
        "1": "Masculino", "2": "Femenino", "3": "Indeterminado"
    }) 

#3.2 GRU_ED2 Agrupación de edades
"""
GRU_ED2 Agrupación de edades, según la edad del
fallecido 01 = Menor de 1 año 02 = De 1 a 4
años 03 = De 5 a 14 años 04 = De 15 a 44 años
05 = De 45 a 64 años 06 = De 65 y mas años 07
= Edad desconocida
"""

filtered_data["GRU_ED2"] = filtered_data["GRU_ED2"].map({
    "01" : "Menor de 1 año",
    "02" : "De 1 a 4 años", 
    "03" : "De 5 a 14 años", 
    "04" : "De 15 a 44 años",
    "05" : "De 45 a 64 años", 
    "06" : "De 65 y mas años", 
    "07" : "Edad desconocida"
}) 

#3.3 NIVEL_EDU Nivel de educacion
"""
Nivel de educacion
Último nivel de estudios que aprobó el fallecido 
1 = Preescolar 2 = Básica primaria 3 = Básica
secundaria 4 = Media académica o clásica 5 =
Media técnica 6 = Normalista 7 = Técnica
profesional 8 = Tecnológica 9 = Profesional 10 =
Especialización 11 = Maestría 12 = Doctorado 13
= Ninguno 99 = Sin información
"""
filtered_data["NIVEL_EDU"] = filtered_data["NIVEL_EDU"].map({
    "1" : "Preescolar", 
    "2" : "Básica primaria", 
    "3" : "Básica secundaria", 
    "4" : "Media académica o clásica", 
    "5" : "Media técnica", 
    "6" : "Normalista", 
    "7" : "Técnica profesional", 
    "8" : "Tecnológica",
    "9" : "Profesional", 
    "10" : "Especialización", 
    "11" : "Maestría",
    "12" : "Doctorado",
    "13" : "Ninguno", 
    "99" : "Sin información"
}) 

# 3.4 IDPERTET
"""
IDPERTET
De acuerdo con la cultura, pueblo o rasgos
físicos, el fallecido era o se reconocia como: 1 =
Indígena 2 = Rom (Gitano) 3 = Raizal del
archipielago de San Andres y Providencia 4 =
Palenquero de San Basilio 5 = Negro(a),
mulato(a), afrocolombiano(a) o afrodescendiente
6 = Ninguno de las anteriores 9 = Sin
infornmación
"""
filtered_data["IDPERTET"] = filtered_data["IDPERTET"].map({   
    "1" : "Indígena", 
    "2" : "Rom (Gitano)", 
    "3" : "Raizal del archipielago de San Andres y Providencia", 
    "4" : "Palenquero de San Basilio", 
    "5" : "Negro(a), mulato(a), afrocolombiano(a) o afrodescendiente",
    "6" : "Ninguno de las anteriores", 
    "9" : "Sin infornmación"    
}) 


#3.6 Dept y Municipio de residencia
"""
CODPTORE Departamento de residencia habitual del
fallecido (para muerte fetal o de menor de un
año el de la madre)

CODMUNRE Municipio de residencia habitual del fallecido
"""
filtered_data['CODMUNRE'] = filtered_data['CODPTORE'] + filtered_data['CODMUNRE']

filtered_data =filtered_data.merge(munic_codes, 
                                   left_on=['CODPTORE', 'CODMUNRE'], 
                                   right_on=['COD_DPTO', 'COD_MUNIC'])

filtered_data = filtered_data.drop(columns=["CODMUNRE", "CODPTORE"])

filtered_data = filtered_data.reset_index(drop = True) 


#3.7 Area de Residencia

"""
AREA_RES Área de residencia habitual del fallecido (para
muerte fetal o de menor de un año la de la
madre) 1 = Cabecera municipal 2 = Centro
poblado (Inspección, corregimiento o caserío) 3
= Rural disperso 9 = Sin información
"""

filtered_data["AREA_RES"] = filtered_data["AREA_RES"].map({   
    "1" : "Cabecera municipal", 
    "2" : "Centro poblado (Inspección, corregimiento o caserío)",
    "3" : "Rural disperso",
    "9" : "Sin información"
}) 

#3.8 Seguridad social

"""
SEG_SOCIAL Régimen de seguridad social del fallecido (para
muerte fetal, o de menor de un año el de la
madre ) 1= Contributivo 2= Subsidiado 3=
Excepción 4= Especial 5= No asegurado 9= Sin
información
"""

filtered_data["SEG_SOCIAL"] = filtered_data["SEG_SOCIAL"].map({   
    "1" : "Contributivo", 
    "2" : "Subsidiado", 
    "3" : "Excepción", 
    "4" : "Especial", 
    "5" : "No asegurado", 
    "9" : "Sin información"
}) 

#3.9 Causa Homologacion 

"""
CAU_HOMOL Causa básica agrupada con base en la Lista 105 Colombia
"""


filtered_data['CAU_HOMOL'] = filtered_data['CAU_HOMOL'].astype(str)
filtered_data =filtered_data.merge(death_codes[['Codigo', 'Causa']], left_on='CAU_HOMOL', right_on='Codigo')
filtered_data = filtered_data.drop(columns=["Codigo", "CAU_HOMOL"])
filtered_data = filtered_data.reset_index(drop = True) 

#4. Renombramos las columnas

processed_data = filtered_data.rename(
    columns = {
            'SEXO' : 'Sexo',
            'GRU_ED2' : 'Edad',
            'NIVEL_EDU' : 'Educacion',
            'IDPERTET' : 'Etnia',
            'AREA_RES' : 'Area_Residencia',
            'SEG_SOCIAL' : 'Seguridad_social',
        }, 
)





#5. Exportamos los datos a un formato CSV
processed_data.to_csv(os.path.join(os.curdir, 'data', 'muertes2020.csv'), encoding='ISO-8859-1')

cols = ['Sexo',
 'Edad',
 'Educacion',
 'Etnia',
 'Area_Residencia',
 'Seguridad_social',
]

for c in cols:
    print(c, list(processed_data[c].unique()))
    
    





