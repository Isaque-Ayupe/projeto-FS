from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql

app = Flask(__name__)
app.secret_key = 'segredo_ultra_confidencial'

def get_db_connection():
    return pymysql.connect(
        database="gerenciado_de_tarefas",
        user="root",
        password="1234",
        host="localhost",
        port=3306,
        cursorclass=pymysql.cursors.Cursor
    )

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        birthdate = request.form['birthdate']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, birthdate, email, phone, password) 
                VALUES (%s, %s, %s, %s, %s)
            """, (username, birthdate, email, phone, password))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Usuário criado com sucesso!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash("Erro ao criar usuário. Nome de usuário pode já existir.", "danger")
            print(e)
    return render_template('cadastro.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_user, username FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        return redirect(url_for('calendario')) 
    else:
        flash("Login inválido!", "danger")
        return redirect(url_for('index'))

@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Rota para a página inicial após o login (calendário)
@app.route('/inicio')
def calendario():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('inicio.html', username=session['username'])

# Rota para exibir o calendário
@app.route('/calendario')
def calendario_view():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('calendario.html', username=session['username'])


#Rota para o kanban.html
@app.route('/kanban')
def kanban_view():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('kanban.html', username=session['username'])

#Rota para o usuario.html
@app.route('/usuario')
def user_view():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('usuario.html', username=session['username'])

#Coletar os dados do usuario no banco
@app.route('/usuario')
def get_user():
    #variaveis do banco
    username= request.form['username']
    birthdate= request.form['birthdate']
    email= request.form['email']
    phone= request.form['phone']

    #conexao com o banco
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_user, username FROM users WHERE username=%s AND birthdate=%s AND email=%s AND phone=%s" , (username,birthdate,email,phone))
    cursor.close()
    conn.close()

#Edição dos dados 
@app.route('/usuario', methods=['POST'])  # mesma URL usada no JavaScript
def user_edit():
    if 'user_id' not in session:
        return "Unauthorized", 401

    data = request.get_json()
    user_id = session['user_id']
    username = data.get('nome')
    birthdate = data.get('aniversario')
    email = data.get('email')
    phone = data.get('telefone')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET username=%s, birthdate=%s, email=%s, phone=%s 
        WHERE id_user=%s
    """, (username, birthdate, email, phone, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return "Dados atualizados com sucesso!", 200

#Higor

# Rota para buscar tarefas (GET)
@app.route('/calendario', methods=['GET'])
def get_tarefas():
    if 'user_id' not in session:
        return jsonify([])

    date = request.args.get('data')
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT hour, task FROM tasks WHERE id_user=%s AND date=%s", (user_id, date))
    tarefas = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({hora: texto for hora, texto in tarefas})

# Rota para criar ou atualizar uma tarefa (POST)
@app.route('/calendario', methods=['POST'])
def post_tarefa():
    if 'user_id' not in session:
        return "Unauthorized", 401

    data = request.get_json()
    user_id = session['user_id']
    date = data['date']
    hour = data['hour']
    task = data['task']

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




#ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp


#Rota para adicionar uma tarefa no kanban 
@app.route('/kanban', methods=['POST'])
def adicionar_tarefa_kanban():
    if 'user_id' not in session:
        return "Unauthorized", 401

    data = request.get_json()
    task_text = data.get('task')

    if not task_text:
        return jsonify({"error": "Tarefa vazia"}), 400

    user_id = session['user_id']
    
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

#rota para atualizar status das tarefas do kanban
@app.route('/kanban/status', methods=['POST'])
def atualizar_status_tarefa():
    if 'user_id' not in session:
        return "Unauthorized", 401

    data = request.get_json()
    task_id = data.get('id')
    status = data.get('status')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE kanban_task SET status = %s WHERE id_kanban = %s AND id_user = %s
    """, (status, task_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Status atualizado com sucesso!"}), 200


#Deletar tarefas do kanban
@app.route('/kanban/delete', methods=['POST'])
def deletar_tarefa_kanban():
    if 'user_id' not in session:
        return "Unauthorized", 401

    data = request.get_json()
    task_id = data.get('id')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM kanban_task WHERE id_kanban = %s AND id_user = %s
    """, (task_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Tarefa excluída com sucesso!"}), 200


#carrega os dados para o kanban 
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

    return jsonify([
        {"id": t[0], "task": t[1], "status": bool(t[2])}
        for t in tarefas
    ])



#pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp




# Rota para carregar eventos de um mês/ano específico
@app.route('/carregar_eventos')
def carregar_eventos():
    if 'user_id' not in session:
        return jsonify([])

    ano = request.args.get('ano')
    mes = request.args.get('mes')
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT task, hour, date FROM tasks
        WHERE YEAR(date) = %s AND MONTH(date) = %s AND id_user = %s
    """, (ano, mes, user_id))

    eventos = cursor.fetchall()
    cursor.close()
    conn.close()

    lista_eventos = []
    for task, hour, date in eventos:
        lista_eventos.append({
            'task': task,
            'hour': hour,
            'date': str(date)
        })

    return jsonify(lista_eventos)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
