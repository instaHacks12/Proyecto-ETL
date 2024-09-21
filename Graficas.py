from flask import Flask, render_template, request, jsonify, make_response
import io
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import matplotlib

matplotlib.use('Agg')

app = Flask(__name__)


engine = create_engine('postgresql+psycopg2://postgres:12345@127.0.0.1:5432/ETL')

df = pd.read_sql('SELECT * FROM cancer_de_mama', engine)

@app.route('/')
def home():
    return render_template('index.html')

def generar_imagen(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    return img

@app.route('/grafica_grupo_edad')
def grafica_grupo_edad():
    df['grupo_edad'].fillna('Desconocido', inplace=True)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    df['grupo_edad'].value_counts().plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title('Distribución de Grupos de Edad')
    ax.set_xlabel('Grupo de Edad')
    ax.set_ylabel('Cantidad de Pacientes')
    img = generar_imagen(fig)
    plt.close(fig)
    
    response = make_response(img.read())
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', 'inline', filename='grafica_grupo_edad.png')
    return response

@app.route('/grafica_dias_consulta_sintomas')
def grafica_dias_consulta_sintomas():
    fig, ax = plt.subplots(figsize=(8, 6))
    df['dias_entre_consulta_y_sintomas'].hist(bins=30, color='orange', ax=ax)
    ax.set_title('Días entre Consulta e Inicio de Síntomas')
    ax.set_xlabel('Días')
    ax.set_ylabel('Cantidad de Pacientes')
    img = generar_imagen(fig)
    plt.close(fig)
    
    response = make_response(img.read())
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', 'inline', filename='grafica_dias_consulta_sintomas.png')
    return response


@app.route('/grafica_comuna')
def grafica_comuna():
    fig, ax = plt.subplots(figsize=(8, 6))
    
    df['comuna'].value_counts().plot(kind='bar', color='lightblue', ax=ax)
    
    ax.set_title('Número de Pacientes por Comuna')
    ax.set_xlabel('Comuna')
    ax.set_ylabel('Cantidad de Pacientes')
    
    img = generar_imagen(fig)
    plt.close(fig)
    
    response = make_response(img.read())
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', 'inline', filename='grafica_comuna.png')
    
    return response


@app.route('/grafica_evolucion_casos')
def grafica_evolucion_casos():
        
        df['fec_con_'] = pd.to_datetime(df['fec_con_'], errors='coerce')

        df_grouped = df.resample('M', on='fec_con_').size()

        fig, ax = plt.subplots(figsize=(10, 6))
        df_grouped.plot(ax=ax, color='purple')

        ax.set_title('Evolución de casos a lo largo del tiempo')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Cantidad de Casos')

        img = generar_imagen(fig)
        plt.close(fig)

        response = make_response(img.read())
        response.headers.set('Content-Type', 'image/png')
        response.headers.set('Content-Disposition', 'inline', filename='grafica_evolucion_casos.png')

        return response

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json['message'].lower()

    if 'pacientes por edad' in user_message:
        grupos_edad = df['grupo_edad'].value_counts().to_dict()
        response = f"La distribución de pacientes por grupo de edad es: {grupos_edad}"

    elif 'pacientes' in user_message:
        total_pacientes = df.shape[0]
        response = f"El número total de pacientes es: {total_pacientes}"

    elif 'sintomas' in user_message:
        promedio_dias = df['dias_entre_consulta_y_sintomas'].mean()
        response = f"El promedio de días entre consulta e inicio de síntomas es: {promedio_dias:.2f} días."

    elif 'promedio de edad' in user_message:
        promedio_edad = df['edad_'].mean()
        response = f"El promedio de edad de los pacientes es: {promedio_edad:.2f} años."


    elif 'grafico de edad' in user_message:
        response = 'Puedes ver el gráfico de distribución de edad haciendo <a href="/grafica_grupo_edad" target="_blank">clic aquí</a>.'

    else:
        response = 'Lo siento, no entiendo tu pregunta. Intenta preguntar sobre grupos de edad, pacientes o síntomas.'

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
