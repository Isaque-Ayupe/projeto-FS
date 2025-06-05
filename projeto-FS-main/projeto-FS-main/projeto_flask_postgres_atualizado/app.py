# Importa os módulos necessários do Flask e PyMySQL
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql

# Cria a aplicação Flask
app = Flask(__name__)
app.secret_key = 'segredo_ultra_confidencial'  # Chave secreta para sessões

# Função para conectar ao banco de dados MySQL
def get_db_connection():
    return pymysql.connect(
        database="gerenciado_de_tarefas",  # Nome do banco
        user="root",                      # Usuário do banco
        password="1234",                  # Senha
        host="localhost",                 # Host local
        port=3306,                        # Porta padrão do MySQL
        cursorclass=pymysql.cursors.Cursor  # Tipo de cursor
    )

# Rota principal da aplicação ("/")
@app.route('/')
def inicio():
    return render_template('index.html')  # Renderiza a página de login

# Rota para cadastro de usuário
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Captura os dados do formulário
        username = request.form['username']
        birthdate = request.form['birthdate']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        try:
            # Conecta ao banco e insere novo usuário
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, birthdate, email, phone, password) 
                VALUES (%s, %s, %s, %s, %s)
            """, (username, birthdate, email, phone, password))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Usuário criado com sucesso!", "success")  # Mensagem de sucesso
            return redirect(url_for('index'))  # Redireciona para a tela de login
        except Exception as e:
            flash("Erro ao criar usuário. Nome de usuário pode já existir.", "danger")
            print(e)  # Exibe erro no console
    return render_template('cadastro.html')  # Renderiza página de cadastro

# Rota para login
@app.route('/login', methods=['POST'])
def login():
    # Captura dados do formulário
    username = request.form['username']
    password = request.form['password']

    # Consulta no banco se o usuário existe
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_user, username FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        # Se existir, salva dados na sessão
        session['user_id'] = user[0]
        session['username'] = user[1]
        return redirect(url_for('calendario'))  # Redireciona para o calendário
    else:
        flash("Login inválido!", "danger")  # Mensagem de erro
        return redirect(url_for('index'))  # Retorna para login

# Rota protegida de index
@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('index.html', username=session['username'])

# Rota de logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return render_template('index.html')

# Rota protegida da tela principal (calendário)
@app.route('/inicio')
def calendario():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('inicio.html', username=session['username'])

# Rota para renderizar o calendário
@app.route('/calendario')
def calendario_view():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('calendario.html', username=session['username'])

# Rota para renderizar o kanban
@app.route('/kanban')
def kanban_view():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('kanban.html', username=session['username'])

# Rota para renderizar o perfil do usuário
@app.route('/usuario')
def user_view():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('usuario.html', username=session['username'])

# Rota para obter dados do usuário (duplicada - causa conflito)
@app.route('/usuario')
def get_user():
    # Pega os dados enviados do formulário
    username= request.form['username']
    birthdate= request.form['birthdate']
    email= request.form['email']
    phone= request.form['phone']

    # Consulta os dados no banco
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_user, username FROM users WHERE username=%s AND birthdate=%s AND email=%s AND phone=%s" , (username,birthdate,email,phone))
    cursor.close()
    conn.close()

# Rota para editar dados do usuário
@app.route('/usuario', methods=['POST'])
def user_edit():
    if 'user_id' not in session:
        return "Unauthorized", 401

    data = request.get_json()
    user_id = session['user_id']
    username = data.get('nome')
    birthdate = data.get('aniversario')
    email = data.get('email')
    phone = data.get('telefone')
    senha = data.get('senha')  # Pega a nova senha, se foi enviada

    conn = get_db_connection()
    cursor = conn.cursor()

    # Atualiza os dados principais
    cursor.execute("""
        UPDATE users 
        SET username=%s, birthdate=%s, email=%s, phone=%s 
        WHERE id_user=%s
    """, (username, birthdate, email, phone, user_id))

    # Atualiza a senha se ela foi enviada
    if senha:
        cursor.execute("""
            UPDATE users 
            SET password=%s 
            WHERE id_user=%s
        """, (senha, user_id))  # Salva a senha diretamente (texto puro)

    conn.commit()
    cursor.close()
    conn.close()

    return "Dados atualizados com sucesso!", 200


# Rota para obter tarefas do calendário
@app.route('/calendario', methods=['GET'])
def get_tarefas():
    if 'user_id' not in session:
        return jsonify([])  # Retorna lista vazia se não logado

    date = request.args.get('data')  # Pega data por parâmetro GET
    user_id = session['user_id']

    # Consulta tarefas da data para o usuário
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT hour, task FROM tasks WHERE id_user=%s AND date=%s", (user_id, date))
    tarefas = cursor.fetchall()
    cursor.close()
    conn.close()

    # Retorna as tarefas em formato JSON (hora: tarefa)
    return jsonify({hora: texto for hora, texto in tarefas})

# Rota para criar ou atualizar tarefa no calendário
@app.route('/calendario', methods=['POST'])
def post_tarefa():
    if 'user_id' not in session:
        return "Unauthorized", 401

    data = request.get_json()  # Recebe dados em JSON
    user_id = session['user_id']
    date = data['date']
    hour = data['hour']
    task = data['task']

    # Insere nova tarefa ou atualiza se já existir
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (id_user, date, hour, task)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE task = VALUES(task)
    """, (user_id, date, hour, task))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Evento salvo com sucesso!"}), 200

# Rota para adicionar tarefa no kanban
@app.route('/kanban', methods=['POST'])
def adicionar_tarefa_kanban():
    if 'user_id' not in session:
        return "Unauthorized", 401

    data = request.get_json()
    task_text = data.get('task')

    if not task_text:
        return jsonify({"error": "Tarefa vazia"}), 400

    user_id = session['user_id']

    # Insere a tarefa no banco
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO kanban_task (task_kanban, id_user)
        VALUES (%s, %s)
    """, (task_text, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Tarefa salva com sucesso!"}), 200

# Rota para atualizar status da tarefa do kanban
@app.route('/kanban_status', methods=['POST'])
def atualizar_status_tarefa():
    if 'user_id' not in session:
        return "Unauthorized", 401

    data = request.get_json()
    task_id = data.get('id')
    status = data.get('status')

    # Atualiza status no banco
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE kanban_task SET status = %s WHERE id_kanban = %s AND id_user = %s
    """, (status, task_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Status atualizado com sucesso!"}), 200

# Rota para deletar tarefa do kanban
@app.route('/kanban_delete', methods=['POST'])
def deletar_tarefa_kanban():
    if 'user_id' not in session:
        return "Unauthorized", 401

    data = request.get_json()
    task_id = data.get('id')

    # Deleta tarefa do banco
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM kanban_task WHERE id_kanban = %s AND id_user = %s
    """, (task_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Tarefa excluída com sucesso!"}), 200

# Rota para carregar tarefas do kanban
@app.route('/carregar_kanban', methods=['GET'])
def carregar_tarefas_kanban():
    if 'user_id' not in session:
        return jsonify([])

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_kanban, task_kanban, status FROM kanban_task WHERE id_user=%s", (user_id,))
    tarefas = cursor.fetchall()
    cursor.close()
    conn.close()

    # Retorna tarefas no formato JSON com id, texto e status booleano
    return jsonify([
        {"id": t[0], "task": t[1], "status": bool(t[2])}
        for t in tarefas
    ])

# Rota para carregar eventos de um mês/ano específico
@app.route('/carregar_eventos')  # Define uma rota GET para /carregar_eventos
def carregar_eventos():
    # Verifica se o usuário está logado; se não estiver, retorna uma lista vazia
    if 'user_id' not in session:
        return jsonify([])

    # Obtém os parâmetros 'ano' e 'mes' da URL (query string)
    ano = request.args.get('ano')
    mes = request.args.get('mes')

    # Recupera o ID do usuário da sessão
    user_id = session['user_id']

    # Conecta ao banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()

    # Executa a consulta para buscar tarefas do usuário com o ano e mês especificados
    cursor.execute("""
        SELECT task, hour, date FROM tasks
        WHERE YEAR(date) = %s AND MONTH(date) = %s AND id_user = %s
    """, (ano, mes, user_id))

    # Recupera todos os resultados da consulta
    eventos = cursor.fetchall()

    # Fecha o cursor e a conexão com o banco de dados
    cursor.close()
    conn.close()

    # Cria uma lista de dicionários com os dados dos eventos formatados
    lista_eventos = []
    for task, hour, date in eventos:
        lista_eventos.append({
            'task': task,
            'hour': hour,
            'date': str(date)  # Converte a data para string
        })

    # Retorna a lista de eventos como resposta JSON
    return jsonify(lista_eventos)


# Executa o aplicativo Flask no modo debug e acessível por qualquer IP na porta 5000
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

