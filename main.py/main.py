from flask import Flask, render_template, request, redirect, flash, session, jsonify, url_for
from functools import wraps
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mercante'

def carregar_usuario():
    if os.path.exists('usuarios.json') and os.stat('usuarios.json').st_size != 0:
        with open('usuarios.json', 'r') as arquivo:
            return json.load(arquivo)
    else:
        return []

def carregar_dados():
    if os.path.exists('dados.json') and os.stat('dados.json').st_size != 0:
        with open('dados.json', 'r', encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            for d in dados:
                d['cod'] = int(d['cod'])
            return dados
    else:
        return []

def salvar_dados(dados):
    dados_ordenados = sorted(dados, key=lambda x: datetime.strptime(x['data'], '%d-%m-%Y'), reverse=True)
    
    with open('dados.json', 'w') as arquivo:
        json.dump(dados_ordenados, arquivo, indent=4)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'nome' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('nome', None)
    return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        
        usuarios = carregar_usuario()
        
        for usuario in usuarios:
            if usuario['nome'] == nome and usuario['senha'] == senha:
                session['nome'] = nome
                return redirect('/home')
            
        else:
            flash("Credenciais incorretas!! Verifique novamente")
            return redirect('/')
    return redirect('/')

@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    if 'nome' not in session:
        return redirect('/')  
    
    nome = session['nome']
    dados = carregar_dados()  
    
    if request.method == 'POST':
        data = request.form.get('data')
        data = datetime.strptime(data, '%Y-%m-%d').strftime('%d-%m-%Y')
        horaE = request.form.get('horaE')
        veic = request.form.get('veic')
        cor = request.form.get('cor')
        plac = request.form.get('placa')
        visit = request.form.get('visit')
        tipo_visitante = request.form.get('check')
        rg = request.form.get('Rg')
        empre = request.form.get('empresa')
        horaS = request.form.get('horaS')
        setor = request.form.get('setor')
        obs = request.form.get('obs')
        

        if rg == '':
            rg = None

        codigo = int(max([d['cod'] for d in dados], default=0)) + 1
        newD = {
            'cod': codigo,
            'nome': nome,
            'data': data,
            'horaE': horaE,
            'veic': veic,
            'cor': cor,
            'placa': plac,
            'visit': visit,
            'tipo_visitante': tipo_visitante,
            'rg': rg,
            'empresa': empre,
            'horaS': horaS,
            'setor': setor,
            'obs': obs,
        }

        dados.append(newD)
        salvar_dados(dados)

    return render_template('home.html', dados=dados)

@app.route('/relatorio')
@login_required
def relatorio():
    dados = carregar_dados()
    return render_template('relatorio.html', dados=dados)

@app.route('/atualizar_dados', methods=['POST'])
@login_required
def atualizar_dados():
    if request.method == 'POST':
        dados_atualizados = request.get_json() 

        if not dados_atualizados:
            return jsonify({'message': 'Nenhum dado enviado.'}), 400

        dados = carregar_dados()  
        for d in dados:  
            if int(d['cod']) == int(dados_atualizados['cod']):   
                d.update(dados_atualizados)
                salvar_dados(dados)
                return jsonify({'message': 'Dados atualizados com sucesso!'})

        return jsonify({'message': 'Erro: Não foi possível encontrar os dados para atualizar.'}), 400

    return jsonify({'message': 'Método não permitido.'}), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
