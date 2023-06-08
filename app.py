from flask import Flask, render_template, request, jsonify
import subprocess

from config import load_config
from sql_utils import db_connect, split_sql_script
from gpt_utils import transform_input_to_sql

# Инициализация Flask приложения
app = Flask(__name__)

config_data = load_config()

@app.route('/', methods=['GET', 'POST'])
def index():
    sql = ""
    result = []
    if request.method == 'POST':
        user_input = request.form['user_input']
        # TODO: Использовать GPT-4 API для преобразования ввода пользователя в SQL
        sql = split_sql_script(transform_input_to_sql(user_input))

        try:
            connection = db_connect(config_data)
            with connection.cursor() as cursor:
                # предположим, что sql - это список запросов, которые вы хотите выполнить
                for query in sql:
                    cursor.execute(query)
                    result.append(cursor.fetchall()) # Добавляем результат каждого запроса в result

        except Exception as e:
            result += [str(e)]
            # return str(e), 400

        return jsonify({'sql': sql, 'result': result})
    else:
        databases = get_databases()
        return render_template('index.html', databases=databases, sql=sql, result=str(result))

@app.route('/dump', methods=['POST'])
def dump():
    db_name = request.form['db_name']
    # TODO: добавить валидацию ввода пользователя
    dump_options = request.form['dump_options']

    try:
        process = subprocess.Popen(
            ['mysqldump', '-u', config_data["MYSQL"]["USER"], '-p' + config_data["MYSQL"]["PASSWORD"], db_name] + dump_options.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return stderr.decode(), 400

        return stdout.decode()
    except Exception as e:
        return str(e), 400

def get_databases():
    try:
        connection = db_connect(config_data)
        with connection.cursor() as cursor:
            cursor.execute('SHOW DATABASES')
            databases = [row['Database'] for row in cursor.fetchall()]
            return databases
    except Exception as e:
        print(e)
        return []

if __name__ == '__main__':
    app.run(debug=True)
