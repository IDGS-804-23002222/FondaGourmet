from . import categorias

from flask import Flask, render_template, request, redirect, url_for, flash
from config import DevelopmentConfig
from flask import g
import forms
from categorias.routes import categorias
from flask_migrate import Migrate #referencia de migrate
from models import Categorias, db
# todo lo referente a la carpeta de maestros empieza con 'maestros' segun lo definido en el modulo con blueprint
@maestros.route('/perfil/<nombre>')
def perfil(nombre):
    return f"Perfil de {nombre}"

@maestros.route('/', methods=['GET','POST'])
@maestros.route('/index')
def index():
    create_form = forms.MaestrosForm(request.form)
    maestros = Maestros.query.all()
      
    return render_template('maestros/listadoMaes.html', form=create_form, maestros=maestros)

@maestros.route('/registrar', methods=['GET', 'POST'])
def registrar():
    create_form = forms.MaestrosForm(request.form)

    if request.method == "POST" and create_form.validate():
        maes = Maestros(
            matricula=create_form.matricula.data,
            nombre=create_form.nombre.data,
            apellido=create_form.apellido.data,
            especialidad=create_form.especialidad.data,
            correo=create_form.correo.data
        )
        db.session.add(maes)
        db.session.commit()
        return redirect(url_for("maestros.index"))

    return render_template("maestros/registrar.html", form=create_form)

@maestros.route("/detalles", methods=["GET", "POST"])
def detalles():
    create_form = forms.MaestrosForm(request.form)
    if request.method == "GET":
        id = request.args.get("id")
        maes1 = db.session.query(Maestros).filter(Maestros.id == id).first()

        matricula = maes1.matricula
        nombre = maes1.nombre
        apellido = maes1.apellido
        especialidad = maes1.especialidad
        correo = maes1.correo
        
    return render_template("maestros/detalles.html", matricula=matricula, nombre=nombre, apellido=apellido, especialidad=especialidad, correo=correo)

@maestros.route("/modificar", methods=["GET", "POST"])
def modificar():
    create_form = forms.MaestrosForm(request.form)
    id = request.args.get("id")
    maes1 = db.session.query(Maestros).filter(Maestros.id == id).first()
    if request.method == "GET":
        create_form.matricula.data=maes1.matricula
        create_form.nombre.data = maes1.nombre
        create_form.apellido.data = maes1.apellido
        create_form.especialidad.data = maes1.especialidad
        create_form.correo.data=maes1.correo

    if request.method == "POST":
        maes1.id=id
        maes1.matricula=create_form.matricula.data
        maes1.nombre=create_form.nombre.data
        maes1.apellido=create_form.apellido.data
        maes1.especialidad=create_form.especialidad.data
        maes1.correo=create_form.correo.data
        db.session.add(maes1)
        db.session.commit()
        return redirect(url_for("maestros.index"))

    return render_template("maestros/modificar.html", form=create_form)

@maestros.route("/eliminar", methods=["GET", "POST"])
def eliminar():
    create_form = forms.MaestrosForm(request.form)
    id = request.args.get("id")
    maes1 = db.session.query(Maestros).filter(Maestros.id == id).first()
    if request.method == "GET":
        create_form.matricula.data=maes1.matricula
        create_form.nombre.data = maes1.nombre
        create_form.apellido.data = maes1.apellido
        create_form.especialidad.data = maes1.especialidad
        create_form.correo.data=maes1.correo

    if request.method == "POST":
        db.session.delete(maes1)
        db.session.commit()
        return redirect(url_for("maestros.index"))

    return render_template("maestros/eliminar.html", form=create_form)





