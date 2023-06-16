import openai
from config import load_config

openai.api_key = load_config()["OPENAI"]["API_KEY"]

import json

def load_db_config(db_type):
    with open(f"{db_type.lower()}_config.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def create_ai_response(db_type, text, previous_qusetion=None, previous_answer=None):
    config = load_db_config(db_type)
    messages = []

    system_message = '\n'.join(config['system_message'])
    messages.append({"role": "system", "content": system_message})

    for sample in config['samples']:
        input = sample['input']
        output = '\n'.join(sample['output'])
        messages.append({"role": "user", "content": input})
        messages.append({"role": "assistant", "content": output})

    if previous_answer and previous_qusetion:
        messages.append({"role": "user", "content": previous_qusetion})
        messages.append({"role": "assistant", "content": previous_answer})

    messages.append({"role": "user", "content": text})

    master_ai_response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=messages,
        max_tokens=6000,
        n=1,
        stop=None,
        temperature=0.5,
    ).choices[0]['message'].content.strip()

    return master_ai_response

def transform_input_to_sql(db_type, user_input): 
    result = create_ai_response(db_type, user_input)

    if "UNRESOLVABLE_QUERY" in result:
        raise Exception("{0}".format(result.split('UNRESOLVABLE_QUERY')[1]))
    
    return result

def retry_transform_input_to_sql(db_type, user_input, ai_answe, db_error):
    result = create_ai_response(db_type, db_error, user_input, ai_answe)

    if "UNRESOLVABLE_QUERY" in result:
        raise Exception("{0}".format(result.split('UNRESOLVABLE_QUERY')[1]))
    
    return result   

 


    