import pandas as pds
import sqlalchemy
import psycopg2
import ftfy

# Creacion de la conexion a la base de datos postgres
server = '127.0.0.1'
db_name='ETL'
user = 'postgres'
password= '12345'
port= '5432'
ft= 'cancer_de_mama'

# creacion del motor de la conexion

engine= sqlalchemy.create_engine(f'postgresql+psycopg2://{user}:{password}@{server}:{port}/{db_name}')

# Extraccion de los datos de el archivo csv

df = pds.read_csv (r'C:\Users\kn418\OneDrive\Escritorio\cancer_de_mama12.csv', delimiter=';', encoding='cp1252')
df.columns = df.columns.str.strip()

# Transformacion
# 1) eliminacion de datos erroneos con caracteres especiales

df['nombre_barrio'] = df['nombre_barrio'].apply(lambda x: ftfy.fix_text(x) if isinstance (x, str)else x)

patron = r'[�]'

df= df[~df['nombre_barrio'].str.contains(patron, regex=True, na=False)]

print(df['nombre_barrio'].iloc[120])

# 2) Corregir valores de formato de fechas

df['fec_con_'] = pds.to_datetime(df['fec_con_'], errors='coerce', format='%d/%m/%Y')
df['ini_sin_'] = pds.to_datetime(df['ini_sin_'], errors='coerce', format='%d/%m/%Y')

print(df[['fec_con_', 'ini_sin_']])

# 3) remplzamiento de valores nulos y fechas invalidas

df= df.replace('SIN INFORMACION' , pds.NA)
df['ini_sin_'] = df ['ini_sin_'].replace('1900-01-01', pds.NaT)

print(df[df['nombre_barrio'].isna() | df['comuna'].isna()][['nombre_barrio', 'comuna']])

print(df[df['ini_sin_'].isna()][['ini_sin_']])

# 4) Nueva columna de la diferencia entre consulta e inicio de sintomas

df['dias_entre_consulta_y_sintomas'] = (df['fec_con_'] - df['ini_sin_']).dt.days

print (df[['dias_entre_consulta_y_sintomas']])

# 5) Creacion de categorias de edades 

df['grupo_edad'] = pds.cut(df['edad_'], bins=[0, 30, 40, 50, 60, 100], labels=['Joven', 'Adulto joven', 'Adulto medio', 'Adulto mayor', 'Senior'])

print(df[['grupo_edad']])

# 6) modificacion de nombres de columnas

df['comuna'] = df ['comuna'].str.strip().replace({
 "SIN INFORMACION" : "Desconocido"
})

print(df['comuna'])

# 7) Detallar mas informacion de tip_cas_ a descripciones legibles
df['descipcion_tip_caso'] = df['tip_cas_'].map({
    1: 'Tipo 1',
    2: 'Tipo 2',
    3: 'Tipo 3',
    4: 'Tipo 4'
})

print(df[['tip_cas_', 'descipcion_tip_caso']])

# observamos los primeros 50 datos
print(df.head(50))

# guardamos todos los datos en la base de datos por medio del motor

df.to_sql(ft, engine, index=False, if_exists= 'replace')


