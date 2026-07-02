import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        port=os.environ.get('DB_PORT', 5432)
    )

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Cria a tabela com a coluna completed caso não exista
        cur.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                task VARCHAR(255) NOT NULL,
                completed BOOLEAN DEFAULT FALSE
            );
        ''')
        # Garante a atualização caso a tabela já existisse sem a coluna completed
        cur.execute('''
            ALTER TABLE todos ADD COLUMN IF NOT EXISTS completed BOOLEAN DEFAULT FALSE;
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Aviso: Falha ao conectar no banco durante a inicialização:", e)

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Agora buscamos também o status 'completed'
        cur.execute('SELECT id, task, completed FROM todos ORDER BY id DESC;')
        todos = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        todos = []
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    if task:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO todos (task) VALUES (%s)', (task,))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/complete/<int:todo_id>', methods=['POST'])
def complete(todo_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Alterna o status (se for True vira False, se for False vira True)
    cur.execute('UPDATE todos SET completed = NOT completed WHERE id = %s', (todo_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete(todo_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM todos WHERE id = %s', (todo_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80)