import pymysql.cursors

# Функция для подключения к базе данных
def db_connect(config):
    MYSQL_HOST = config["MYSQL"]["HOST"]
    MYSQL_USER = config["MYSQL"]["USER"]
    MYSQL_PASSWORD = config["MYSQL"]["PASSWORD"]
    MYSQL_DB = config["MYSQL"]["DB"]

    connection = pymysql.connect(host=MYSQL_HOST,
                                 user=MYSQL_USER,
                                 password=MYSQL_PASSWORD,
                                 db=MYSQL_DB,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def split_sql_script(script):
    # Варианты разделителей, которые могут быть использованы
    delimiters = [';', '//', '$$']
    # Изначальный разделитель
    delimiter = ';'
    # Команды разделенные на строки
    lines = script.splitlines()
    # Контейнер для отдельных команд
    commands = []
    # Контейнер для текущей команды
    current_command = []
    
    for line in lines:
        # Если строка содержит оператор DELIMITER, изменить текущий разделитель
        if line.strip().lower().startswith('delimiter'):
            delimiter = line.strip().split(' ')[1]
            continue
        
        # Если текущая строка содержит текущий разделитель
        if delimiter in line:
            # Разделить строку по разделителю
            sublines = line.split(delimiter)
            # Добавить первую часть в текущую команду
            current_command.append(sublines[0])
            # Добавить текущую команду в список команд
            commands.append('\n'.join(current_command))
            # Остаток строки после разделителя становится началом следующей команды
            current_command = sublines[1:]
        else:
            current_command.append(line)
    
    # Если в конце осталась команда без разделителя, добавить её в список команд
    if current_command:
        commands.append('\n'.join(current_command))
    
    # Удалить возможные пустые команды
    commands = [cmd for cmd in commands if cmd.strip()]

    return commands

