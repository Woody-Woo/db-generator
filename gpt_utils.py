import openai
from config import load_config

openai.api_key = load_config()["OPENAI"]["API_KEY"]

def configuration_ai_message():
    return """Я хочу чтобы выполнил роль преобразования человеческого запроса, в SQL команды.

Ты будеш получать текстовое описание хотелки пользователя, а возвращать должен SQL запрос, который удволетворяет этой команде.

В ответ ты долежн возвращать всегда SQL запрос или sql запросы разделённые точкой с запятой. .  Если ты хочеш добавить комментарий - то оберни его в SQL комментарий. И ничего кроме запроса, результат твоего ответа будет без изменений передан в базу данных.

Если пользователь не указывает явно имя БД, но просит создать БД, то создавай БД с учётом её содержания и можеш добавить случайных слов для уникальности

Для разделения команд между собой используй точку с запятой, также используй DELIMETER для временной смены разделителя.

"""

def create_ai_response(text):
    messages = []
    messages.append({"role": "system", "content": configuration_ai_message()})

    messages.append({"role": "user", "content": text})

    master_ai_response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    ).choices[0]['message'].content.strip()

    return master_ai_response

def transform_input_to_sql(user_input):
    try:
        return create_ai_response(user_input)
    except Exception as e:
        print(e)
        return None

