import psycopg2
import psycopg2.extras
import pymysql
import pyodbc
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def db_connect(db_type, config):
    try:
        if db_type == 'MYSQL':
            connection = pymysql.connect(host=config["HOST"],
                                         user=config["USER"],
                                         password=config["PASSWORD"],
                                         db=config["DB"],
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
            logging.info(f'Successfully connected to MYSQL database')
        elif db_type == 'POSTGRESQL':
            connection = psycopg2.connect(host=config["HOST"],
                                          user=config["USER"],
                                          password=config["PASSWORD"],
                                          dbname=config["DB"],
                                          cursor_factory=psycopg2.extras.RealDictCursor)
            logging.info(f'Successfully connected to POSTGRESQL database')
        elif db_type == 'SQLSERVER':
            connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                                        f'SERVER={config["HOST"]};'
                                        f'DATABASE={config["DB"]};'
                                        f'UID={config["USER"]};'
                                        f'PWD={config["PASSWORD"]}')
            logging.info(f'Successfully connected to SQLSERVER database')
        else:
            raise Exception(f"Not implemented for {db_type}")

        return connection
    except Exception as e:
        logging.exception(e)
        raise

def get_default_db(db_type):
    try:
        if db_type == 'MYSQL':
            return 'mysql'
        elif db_type == 'POSTGRESQL':
            return 'postgres'
        elif db_type == 'SQLSERVER':
            return 'master'
        else:
            raise Exception(f"Not implemented for {db_type}")
    except Exception as e:
        logging.exception(e)
        raise

def get_databases(db_type, config):
    try:
        if db_type == 'MYSQL':
            result = execute_sql_scripts(db_type, config, ['SHOW DATABASES'])
            return [x['Database'] for x in result[0]]
        elif db_type == 'POSTGRESQL':
            result = execute_sql_scripts(db_type, config, ['SELECT datname FROM pg_database'])
            return [x['datname'] for x in result[0]]
        elif db_type == 'SQLSERVER':
            result = execute_sql_scripts(db_type, config, ["SELECT name FROM sys.databases"])
            return  [x['name'] for x in result[0]] if len(result[0]) > 0 else []
    except Exception as e:
        logging.exception(e)
        raise Exception("Error while getting databases: " + str(e))

def get_default_db(db_type):
    try:
        if db_type == 'MYSQL':
            return 'mysql'
        elif db_type == 'POSTGRESQL':
            return 'postgres'
        else:
            raise Exception(f"Not implemented for {db_type}")
    except Exception as e:
        logging.exception(e)
        raise

def execute_sql_scripts(db_type, config, sql_scripts):
    result = []
    connection = None
    db_name = None

    try:
        connection = db_connect(db_type, config)
        connection.autocommit = True

        cursor = connection.cursor()

        try:
            for script in sql_scripts:
                if script.strip() != '':
                    if script.strip().startswith("\\c") or script.strip().startswith("USE"):
                        db_name = script.strip().split()[1]
                        new_config = config.copy()
                        new_config["DB"] = db_name
                        cursor.close()
                        connection.close()

                        connection = db_connect(db_type, new_config)
                        connection.autocommit = True
                        cursor = connection.cursor()
                        logging.info(f'Successfully switched to database: {db_name}')
                        continue

                    if script.strip().lower().startswith("create database"):
                        db_name = script.strip().split()[2]

                    cursor.execute(script)
                    logging.info(f'Executed script: {script}')

                    if cursor.description:
                        if db_type == 'SQLSERVER':
                            temp_result = cursor.fetchall()
                            temp_result_2 = []  

                            for row in temp_result:
                                temp_row = {}
                                for index in range(len(row)):
                                    temp_row[cursor.description[index][0]] = str(row[index])

                                temp_result_2.append(temp_row)

                            result.append(temp_result_2)
                        else:
                            result.append(cursor.fetchall())

                    connection.commit()
                    logging.info(f'Successfully committed changes for script: {script}')

        finally:
            cursor.close()
    
    except Exception as e:
        logging.exception(e)
        if db_name is not None and 'create database' in sql_scripts[0].lower():
            try:
                drop_db_config = config.copy()
                drop_db_config["DB"] =  get_default_db(db_type)
                drop_connection = db_connect(db_type, drop_db_config)
                drop_connection.autocommit = True

                connection.close()

                with drop_connection.cursor() as cursor:
                    stripped_db_name = db_name.strip(';')
                    cursor.execute(f'DROP DATABASE {stripped_db_name}')
                    drop_connection.commit()
                logging.info(f'Successfully dropped the database: {db_name}')
            except Exception as drop_error:
                logging.exception(drop_error)
                print(f"Error while trying to drop the database '{db_name}': {str(drop_error)}")
                pass

        raise Exception("Error while executing SQL scripts: " + str(e)) from e

    finally:
        if connection is not None:
            connection.close()
            logging.info(f'Successfully closed the database connection')

    return result

def split_sql_server_script(script):
    try:
        delimiter = 'GO'
        lines = script.splitlines()
        commands = []
        current_command = []
        
        for line in lines:
            stripped_line = line.strip()
            
            if stripped_line.upper() == delimiter:
                if current_command:
                    commands.append('\n'.join(current_command))
                    current_command = []
                continue

            current_command.append(line)
        
        if current_command:
            commands.append('\n'.join(current_command)) 
        
        commands = [cmd for cmd in commands if cmd.strip()]

        return commands
    except Exception as e:
        logging.exception(e)
        raise

def split_mysql_and_postgre_script(script):
    try:
        delimiter = ';'
        lines = script.splitlines()
        commands = []
        current_command = []
        
        in_dollar_quotes = False
        
        for line in lines:
            if line.strip().lower().startswith('delimiter'):
                delimiter = line.strip().split(' ')[1]
                continue

            if line.strip().startswith('\\c'):
                if current_command:
                    commands.append('\n'.join(current_command).rstrip(';'))  
                    current_command = []
                commands.append(line.strip())
                continue

            if '$$' in line:
                in_dollar_quotes = not in_dollar_quotes
                current_command.append(line)
                if not in_dollar_quotes:
                    commands.append('\n'.join(current_command).rstrip(';'))
                    current_command = []
                continue

            if not in_dollar_quotes and delimiter in line:
                sublines = line.split(delimiter)
                current_command.append(sublines[0])
                commands.append('\n'.join(current_command).rstrip(';'))  
                current_command = sublines[1:]
            else:
                current_command.append(line)
        
        if current_command:
            commands.append('\n'.join(current_command).rstrip(';')) 
        
        commands = [cmd for cmd in commands if cmd.strip()]

        return commands
    except Exception as e:
        logging.exception(e)
        raise

def split_sql_script(db_type, script):
    try:
        if db_type == 'SQLSERVER':
            return split_sql_server_script(script)
        elif db_type == 'MYSQL' or db_type == 'POSTGRESQL':
            return split_mysql_and_postgre_script(script)
        else:
            raise Exception(f"Not implemented for {db_type}")
    except Exception as e:
        logging.exception(e)
        raise

