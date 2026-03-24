from flask import Flask, render_template, request, session
import math
import forms 
from flask_wtf.csrf import CSRFProtect

app= Flask(__name__)
app.secret_key='clave secreta'
csrf=CSRFProtect()

@app.route('/')
def index():
    return render_template('index.html')

if __name__=='__main__':
    #habilita la app solamente si se agrega la clave especificada (clave_secreta)
    csrf.init_app(app)
    #con el debug se puede actualizar el servidor conforma se guardan los cambios, si no se coloca, se debe reiniciar
    #el servidor para que se apliquen los cambios
    app.run(debug=True)