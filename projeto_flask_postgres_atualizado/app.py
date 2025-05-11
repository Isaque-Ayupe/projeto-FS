
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import psycopg2

app = Flask(__name__)
app.secret_key = 'segredo_ultra_confidencial'

def get_db_connection():
    return psycopg2.connect(
        dbname="projeto_web",
        user="seu_usuario",
        password="sua_senha",
        host="localhost",
        port="5432"
    )

@app.route('/')
def index():
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
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, birthdate, email, phone, password) VALUES (%s, %s, %s, %s, %s)",
                               (username, birthdate, email, phone, password))
                conn.commit()
            flash("Usuário criado com sucesso!", "success")
            return redirect(url_for('index'))
        except:
            flash("Erro ao criar usuário. Nome de usuário pode já existir.", "danger")
    return render_template('cadastro.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = user[1]
            return redirect(url_for('calendario'))
        else:
            flash("Login inválido!", "danger")
            return redirect(url_for('index'))

@app.route('/calendario')
def calendario():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('calendario.html', username=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/tarefas', methods=['GET'])
def get_tarefas():
    if 'user' not in session:
        return jsonify([])

    date = request.args.get('data')
    username = session['user']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT hour, task FROM tasks WHERE username=%s AND date=%s", (username, date))
        tarefas = cursor.fetchall()

    return jsonify({hora: texto for hora, texto in tarefas})

@app.route('/tarefas', methods=['POST'])
def post_tarefa():
    if 'user' not in session:
        return "Unauthorized", 401

    data = request.get_json()
    username = session['user']
    date = data['date']
    hour = data['hour']
    task = data['task']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (username, date, hour, task)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (username, date, hour)
            DO UPDATE SET task = EXCLUDED.task
        """, (username, date, hour, task))
        conn.commit()

    return "OK", 200
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)


