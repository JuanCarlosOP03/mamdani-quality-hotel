import os
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_difusa_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///encuesta_fuzzy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ADMIN_PASSWORD = "NdN6d.!d£5o6]NY" # Credencial de acceso administrativo
db = SQLAlchemy(app)

class RespuestaEncuesta(db.Model):
    """
    Representación tabular de las variables lingüísticas transformadas en datos numéricos.
    Incluye metadatos para la trazabilidad temporal [2].
    """
    id = db.Column(db.Integer, primary_key=True)
    correo_electronico = db.Column(db.String(120), nullable=False)
    fecha_respuesta = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Dimensiones de evaluación (Secciones A a E según el diseño del formulario [3])
    a1 = db.Column(db.Integer); a2 = db.Column(db.Integer); a3 = db.Column(db.Integer); a4 = db.Column(db.Integer)
    b1 = db.Column(db.Integer); b2 = db.Column(db.Integer); b3 = db.Column(db.Integer)
    c1 = db.Column(db.Integer); c2 = db.Column(db.Integer); c3 = db.Column(db.Integer)
    d1 = db.Column(db.Integer); d2 = db.Column(db.Integer)
    e1 = db.Column(db.Integer); e2 = db.Column(db.Integer)

# --- LÓGICA DEL MOTOR DE INFERENCIA DIFUSA (FIS) ---
def configurar_sistema_difuso():
    """
    Establece la base de conocimiento y las funciones de pertenencia para el cálculo de la calidad.
    La modularización de esta función permite ajustes independientes del modelo matemático.
    """
    universe = np.arange(1, 10.01, 0.01)

    # Definición de antecedentes (Entradas)
    desempeno = ctrl.Antecedent(universe, 'desempeno')
    eficiencia = ctrl.Antecedent(universe, 'eficiencia')
    eficacia = ctrl.Antecedent(universe, 'eficacia')
    estabilidad = ctrl.Antecedent(universe, 'estabilidad')
    prevencion = ctrl.Antecedent(universe, 'prevencion')
    
    # Definición del consecuente (Saída: Calidad)
    calidad = ctrl.Consequent(universe, 'hotel_calidad_servicio')

    # Fuzzificación: Definición de conjuntos difusos
    for var in [desempeno, eficiencia, eficacia, estabilidad, prevencion]:
        var['bajo'] = fuzz.trapmf(universe, [1, 1, 3, 4.5])
        var['medio'] = fuzz.trimf(universe, [3.5, 5.5, 7.5])
        var['alto'] = fuzz.trapmf(universe, [6.5, 8, 10, 10])

    calidad['muy_bajo'] = fuzz.trimf(universe, [1, 1, 3])
    calidad['bajo'] = fuzz.trimf(universe, [2, 4, 6])
    calidad['medio'] = fuzz.trimf(universe, [4, 6, 8])
    calidad['alto'] = fuzz.trimf(universe, [6, 8, 9])
    calidad['muy_alto'] = fuzz.trimf(universe, [8, 10, 10])

    # Base de Reglas Lingüísticas
    rules = [

        ctrl.Rule(desempeno['alto'] & eficiencia['alto'] & eficacia['alto'] & 
                estabilidad['alto'] & prevencion['alto'], calidad['muy_alto']),
        
        ctrl.Rule((desempeno['alto'] & eficiencia['alto'] & eficacia['alto']) & 
                (estabilidad['medio'] | prevencion['medio']), calidad['alto']),
        
        ctrl.Rule(estabilidad['medio'] | prevencion['medio'], calidad['medio']),
        
        ctrl.Rule(desempeno['medio'] & eficiencia['medio'] & eficacia['medio'], calidad['medio']),
        
        ctrl.Rule(prevencion['bajo'] | estabilidad['bajo'], calidad['bajo']),
        
        ctrl.Rule(desempeno['bajo'] | eficiencia['bajo'] | eficacia['bajo'], calidad['bajo']),

        ctrl.Rule(desempeno['bajo'] & eficiencia['bajo'] & prevencion['bajo'], calidad['muy_bajo'])
    ]

    sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))
    return sim, calidad

# Instanciación global del motor
simulador, consecuente_calidad = configurar_sistema_difuso()

# --- UTILIDADES DE CÁLCULO ---
def obtener_etiqueta_difusa(valor_crisp):
    """Categorización lingüística basada en el grado de pertenencia más alto."""
    labels = ['muy_bajo', 'bajo', 'medio', 'alto', 'muy_alto']
    puntuacions = {l: fuzz.interp_membership(consecuente_calidad.universe, consecuente_calidad[l].mf, valor_crisp) for l in labels}
    return max(puntuacions, key=puntuacions.get).replace('_', ' ').capitalize()

def procesar_calculo_fuzzy(r):
    """
    Calcula el índice escalar (Crisp), su interpretación difusa y los valores de entrada.
    Se retorna un tercer elemento: un diccionario con los promedios de cada sección.
    """
    try:
        # Cálculo de promedios para las variables de entrada
        entradas = {
            'desempeno': round((r.a1 + r.a2 + r.a3 + r.a4) / 4, 2),
            'eficiencia': round((r.b1 + r.b2 + r.b3) / 3, 2),
            'eficacia': round((r.c1 + r.c2 + r.c3) / 3, 2),
            'estabilidad': round((r.d1 + r.d2) / 2, 2),
            'prevencion': round((r.e1 + r.e2) / 2, 2)
        }
        
        # Asignación al simulador
        for clave, valor in entradas.items():
            simulador.input[clave] = valor
            
        simulador.compute()
        crisp = round(simulador.output['hotel_calidad_servicio'], 2)
        return crisp, obtener_etiqueta_difusa(crisp), entradas
    except Exception as e:
        # Valores por defecto en caso de error
        return 5.0, "Medio", {k: 0.0 for k in ['desempeno', 'eficiencia', 'eficacia', 'estabilidad', 'prevencion']}

# --- MÓDULO DE SEGURIDAD ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# --- RUTAS DE LA APLICACIÓN ---
@app.route('/')
def index():
    # Estructura basada en las dimensiones de calidad del servicio [3].
    sections = [
        
        ('Sección A. Desempeño', [
            ('a1', 'A.1. Limpieza de la habitación'), 
            ('a2', 'A.2. Confort de la estancia'),
            ('a3', 'A.3. Agilidad en el check-in/out'), 
            ('a4', 'A.4. Estado de instalaciones')
        ]),
        
        ('Sección B. Eficiencia', [
            ('b1', 'B.1. Rapidez en la atención'), 
            ('b2', 'B.2. Tiempo de respuesta'), 
            ('b3', 'B.3. Ausencia de retrasos')
        ]),
        
        ('Sección C. Eficacia', [
            ('c1', 'C.1. Correspondencia con oferta'), 
            ('c2', 'C.2. Cumplimiento de expectativas'), 
            ('c3', 'C.3. Ejecución de servicios')
        ]),
        
        ('Sección D y E. Estabilidad y Riesgos', [
            ('d1', 'D.1. Constancia en calidad'), 
            ('d2', 'D.2. Estabilidad del servicio'),
            ('e1', 'E.1. Ausencia de inconvenientes'), 
            ('e2', 'E.2. Resolución de situaciones')
        ])
    ]
    content = render_template('form.html', sections=sections)
    return render_template('base.html', body=content)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        form_data = {k: int(v) for k, v in request.form.items() if k != 'email'}
        nuevo = RespuestaEncuesta(correo_electronico=request.form.get('email'), **form_data)
        db.session.add(nuevo); db.session.commit()
        
        # Se capturan los tres valores retornados
        crisp, etiqueta, entradas = procesar_calculo_fuzzy(nuevo)
        
        # Se pasan 'entradas' a la plantilla
        content = render_template('result.html', crisp=crisp, etiqueta=etiqueta, inputs=entradas)
        return render_template('base.html', body=content)
    except Exception as e:
        flash(f"Error en el procesamiento: {e}", "danger"); return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True; return redirect(url_for('resultados'))
        flash("Contraseña incorrecta", "danger")

    return render_template('base.html', body=render_template('login.html'))

@app.route('/resultados')
@login_required
def resultados():
    registros = RespuestaEncuesta.query.all()
    data = []
    for r in registros:
        c, e, i = procesar_calculo_fuzzy(r)
        data.append({
            'email': r.correo_electronico, 
            'fecha': r.fecha_respuesta.strftime('%d/%m/%y'), 
            'crisp': c, 
            'etiqueta': e,
            'inputs': i
        })

    return render_template('base.html', body=render_template('results_global.html', data=data))

@app.route('/logout')
def logout():
    session.pop('logged_in', None); return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True, port=5003)