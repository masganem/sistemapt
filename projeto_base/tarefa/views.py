import os
import re
from flask import render_template, Blueprint, request, redirect, url_for, flash, current_app
from projeto_base.tarefa.models import Tarefa, TarefaTrainee
from projeto_base.usuario.models import Usuario, usuario_urole_roles
from projeto_base import db, login_required
from flask_login import LoginManager, current_user, login_user, logout_user
from projeto_base.tarefa.utils import data_format_in, data_format_out, define_solo_in, define_solo_out

tarefa = Blueprint('tarefa', __name__, template_folder='templates')

@tarefa.route('/cadastrar_tarefa', methods=['POST', 'GET'])
@login_required(role=[usuario_urole_roles['ADMIN']])
def cadastra_tarefa():
    if request.method == 'POST':
        form = request.form

        titulo = form['titulo']
        descricao = form['descricao']
        icone = request.files['icone']
        prazo = form['data']
        solo = form['ehSolo']

        #tratando data 
        prazo = data_format_in(prazo)

        #tratando ehSolo
        ehSolo = define_solo_in(solo)

        filename = icone.filename
        print("++++++++++++++++" + filename)
        filepath = os.path.join(current_app.root_path, 'static', 'fotos_tarefa', filename)
        icone.save(filepath)

        tarefa = Tarefa(titulo, descricao, filename, prazo, ehSolo)

        db.session.add(tarefa)
        db.session.commit() 
    
        flash("Tarefa cadastrada!")

        return redirect(url_for('principal.index'))

    return render_template('cadastro_tarefa.html')


@tarefa.route('/listar_tarefas')
@login_required(role=[usuario_urole_roles['ADMIN']])
def lista_tarefas():
    tarefas = Tarefa.query.all()
    if not tarefas:
        flash("Não há tarefas cadastradas no sistema.")
        return redirect(url_for('principal.index'))
    
    return render_template('listar_tarefas.html', tarefas=tarefas)

@tarefa.route('/deletar_tarefa/<id>')
@login_required(role=[usuario_urole_roles['ADMIN']])
def deleta_tarefa(id):
    tarefa = Tarefa.query.filter_by(id=id).first_or_404()
    
    filepath = os.path.join(current_app.root_path, 'static', 'fotos_tarefa', tarefa.icone)
    os.remove(filepath)

    db.session.delete(tarefa)
    db.session.commit()

    return redirect(url_for('tarefa.lista_tarefas'))

@tarefa.route('/editar_tarefa/<id>', methods=['GET'])
@login_required(role=[usuario_urole_roles['ADMIN']])
def pagina_edicao_tarefa(id):
    tarefa = Tarefa.query.filter_by(id=id).first_or_404()

    #tratando data
    prazo = data_format_out(tarefa.prazo)

    #tratando ehSolo
    solo = define_solo_out(tarefa.ehSolo)

    print(tarefa.id)
    return render_template('edicao_tarefa.html', titulo=tarefa.titulo, descricao=tarefa.descricao, prazo=prazo, solo=solo, id=tarefa.id)

@tarefa.route('/editar_tarefa', methods=['POST'])
@login_required(role=[usuario_urole_roles['ADMIN']])
def edita_tarefa():
    form = request.form

    _id = form['id']
    tarefa = Tarefa.query.filter_by(id=_id).first_or_404()

    titulo = form['titulo']
    descricao = form['descricao']
    prazo = form['data']
    solo = form['ehSolo']

    icone = request.files['icone']
    if icone.content_type != 'application/octet-stream':
        filename = icone.filename
        print("++++++++++++++++" + filename)
        filepath_novo = os.path.join(current_app.root_path, 'static', 'fotos_tarefa', filename)
        icone.save(filepath_novo)
        
        tarefa.icone = filename
        
        filepath_antigo = os.path.join(current_app.root_path, 'static', 'fotos_tarefa', tarefa.icone)
        os.remove(filepath_antigo)

    #tratando data 
    prazo = data_format_in(prazo)

    #tratando ehSolo
    ehSolo = define_solo_in(solo)
    
    tarefa.titulo = titulo
    tarefa.descricao = descricao
    tarefa.prazo = prazo
    tarefa.ehSolo = ehSolo

    db.session.commit()

    return redirect(url_for('tarefa.lista_tarefas'))