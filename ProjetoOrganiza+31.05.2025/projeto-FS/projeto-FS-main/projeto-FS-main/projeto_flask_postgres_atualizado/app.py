from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql

app = Flask(__name__)
app.secret_key = 'segredo_ultra_confidencial'

#conexao do banco de dados
def get_db_connection():
    return pymysql.connect(
        database="gerenciado_de_tarefas",
        user="root",
        password="1234",
        host="localhost",
        port=3306,
        cursorclass=pymysql.cursors.Cursor
    )
#rota inicial
@app.route('/')
def entrada():
    return render_template('index.html')
#rota de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        birthdate = request.form['birthdate']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        try: #tenta conexao com banco de dados
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, birthdate, email, phone, password) 
                VALUES (%s, %s, %s, %s, %s)
            """, (username, birthdate, email, phone, password))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Usuário criado com sucesso!", "success")#funcionou
            return redirect(url_for('index'))
        except Exception as e:
            flash("Erro ao criar usuário. Nome de usuário pode já existir.", "danger")#nao funcionou
            print(e)
    return render_template('cadastro.html')
#rota de login
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

    #login com sucesso
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        return redirect(url_for('calendario' \
        '')) 
    #login invalido
    else: 
        flash("Login inválido!", "danger")
        return redirect(url_for('index'))
#redireciona pro inicio se a sessao bugar
@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('index.html', username=session['username'])
#rota de log_out
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#higor: Rota para o inicio apos o login, Já exite uma rota chamada inicio, por isso eu mantive calendario...
@app.route('/inicio')
def inicio():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('inicio.html', username=session['username'])

#higor: Adicionei esta rota para o calendario...
@app.route('/calendario')
def calendario_view():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('calendario.html', username=session['username'])
#pega os eventos existentes
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
#adiciona tarefas
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

    return "OK", 200
#inicia o app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
