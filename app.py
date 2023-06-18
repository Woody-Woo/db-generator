import logging
from flask import Flask, render_template, request, jsonify
from config import load_config
from sql_utils import execute_sql_scripts, split_sql_script,get_databases
from gpt_utils import transform_input_to_sql, retry_transform_input_to_sql
from flask_httpauth import HTTPBasicAuth

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

auth = HTTPBasicAuth()

app = Flask(__name__)

config_data = load_config()

@auth.verify_password
def verify_password(username, password):
    if username and password:
        return username == config_data["SITE_AUTH"]["USERNAME"] and password == config_data["SITE_AUTH"]["PASSWORD"]
    return False

@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def execute_sql():
    if request.method == 'GET':
        try:
            default_db_type = 'MYSQL'
            config = load_config()
            databases = get_databases(default_db_type,config[default_db_type])
            logging.info(f'Successfully got databases for {default_db_type}: {databases}')
            return render_template('index.html', config=config[default_db_type], databases=databases)
        except Exception as e:
            logging.exception(e)
            return str(e)
    elif request.method == 'POST':
        user_input = request.form.get('user_input', '')
        db_type = request.form.get('db_type', '')
        sql = ""
        config = {
                "HOST": request.form.get('db_host', ''),
                "USER": request.form.get('db_user', ''),
                "PASSWORD": request.form.get('db_password', ''),
                "DB": request.form.get('db_name', '')
            }
        
        try:
            databases = get_databases(db_type, config)
            sql = transform_input_to_sql(db_type,user_input)
            result = execute_sql_scripts(db_type, config, split_sql_script(db_type,sql))
            logging.info(f'Successfully executed SQL scripts: {sql}. Result: {result}')
            
            return jsonify({'sql': sql, 'result': result, 'config' : config, 'databases' : databases})
        except Exception as e:
            logging.exception(e)
            return jsonify({'error': str(e), 'sql': sql})

@app.route('/get_default_values', methods=['POST'])
def get_default_values():
    db_type = request.form.get('db_type')
    config = load_config()  
    try:
        db_config = config[db_type]
        databases = get_databases(db_type, db_config)
        logging.info(f'Successfully got default values for {db_type}: {db_config}, databases: {databases}')
        
        return jsonify(config=db_config, databases=databases)
    except Exception as e:
        logging.exception(e)
        return jsonify(error= str(e))
    
@app.route('/retry', methods=['POST'])
@auth.login_required
def retry():
    user_input = request.form.get('user_input', '')
    ai_answer = request.form.get('ai_answer', '')
    db_error = request.form.get('error', '')

    db_type = request.form.get('db_type', '')

    sql = ""
    config = {
            "HOST": request.form.get('db_host', ''),
            "USER": request.form.get('db_user', ''),
            "PASSWORD": request.form.get('db_password', ''),
            "DB": request.form.get('db_name', '')
        }
    
    try:
        databases = get_databases(db_type, config)
        sql = retry_transform_input_to_sql(db_type,user_input,ai_answer,db_error)
        result = execute_sql_scripts(db_type, config, split_sql_script(db_type,sql))
        logging.info(f'Retried execution of SQL scripts: {sql}. Result: {result}')
        
        return jsonify({'sql': sql, 'result': result, 'config' : config, 'databases' : databases})
    except Exception as e:
        logging.exception(e)
        return jsonify({'error': str(e), 'sql': sql})

if __name__ == '__main__':
    app.run(debug=True)

