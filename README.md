
# SQL GPT-4 Assistant

This project is an SQL assistant powered by the GPT-4 model from OpenAI. It allows you to input your queries in natural language and receive SQL query results.

This utility is intended for testing purposes only and should not be used in production, as the result from ChatGPT is directly passed to the database without intermediate confirmation.

The model training is done using the files mysql_config.json, postgresql_config.json, and sqlserver_config.json. The training was conducted in Russian. To use the utility with other languages, it is recommended to translate the contents of these files.

## Installation and Setup

1. Clone the repository.
2. Install the necessary dependencies (specified in the `requirements.txt` file).
3. Create a `config.json` file in the project's root directory, using `config.json.sample` as a template. Insert your database connection details and OpenAI API key.
4. Run `app.py`.
5. Open `localhost:5000` in your web browser.

## Usage

Select the database type, and then enter what you want to do with the database in natural language. For example, "Create a database for an online store, populate it with test data, and then retrieve and display the data." SQL GPT-4 Assistant will generate the SQL query and execute it, displaying the results (if the query returns any).

## Note

You will need an OpenAI API key, which can be obtained from https://platform.openai.com/account/api-keys. Place the API key in the `config.json` file.

Enjoy using SQL GPT-4 Assistant!

