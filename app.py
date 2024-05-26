import chainlit as cl
from openai import OpenAI, AzureOpenAI
from graphviz import Source
import os
import json
import time
import random
from types import SimpleNamespace

# Set your OpenAI API key here if you use OpenAI services
OPENAI_KEY = ""

# Set your API key, endpoint URL and API version here if you use Azure OpenAI services
AZURE_OPENAI_KEY = ""
AZURE_OPENAI_ENDPOINT = ""
AZURE_OPENAI_VERSION = ""

GPT_MODEL = "gpt-4o"
TEMPERATURE = 0.5
SYSTEM_PROMPT = '''You are an HR assistant who manage the employees database. 
You answer questions basing only on employees information in the database. 
Use function calling (tools call) if the user mentions attached file or document.''' 

DATABASE_FILE = "employees.csv"
TEMP_FILES_FOLDER = ".files"
WAITING_MESSAGE = "Please wait..."

if len(OPENAI_KEY) > 0:
    ai_client = OpenAI(api_key = OPENAI_KEY)
elif len(AZURE_OPENAI_KEY) > 0:
    ai_client = AzureOpenAI(api_key = AZURE_OPENAI_KEY, api_version=AZURE_OPENAI_VERSION, azure_endpoint=AZURE_OPENAI_ENDPOINT)
else:
    print("[ERROR] Need to set up API key for OpenAI or Azure OpenAI")
    exit(1)

tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_graph",
            "description": "Generate graph, diagram or chart from DOT language using Graphviz library",
            "parameters": {
                "type": "object",
                "properties": {
                    "graph_data": {
                        "type": "string",
                        "description": "Graph data in DOT language format",
                    }
                },
                "required": ["graph_data"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_employees_file",
            "description": "Save the attached CSV file that contain the list of employees",
            "parameters": {
                "type": "object",
                "properties": {
                }
            }
        }
    }
]

@cl.on_message
async def main(message: cl.Message):
    # Create folder for temporary files for current user if not exist
    user_temp_file_folder = f'{TEMP_FILES_FOLDER}/{cl.user_session.get("id")}'
    if not os.path.exists(user_temp_file_folder):
        os.makedirs(user_temp_file_folder)
    
    save_message_to_history(message)

    #Create an empty response to show loading icon
    response_msg = cl.Message(content="")
    await response_msg.send()
    
    #Call OpenAI
    conversation_history = get_conversation_history()
    result = await cl.make_async(get_gpt_response)(ai_client, GPT_MODEL, TEMPERATURE, SYSTEM_PROMPT, conversation_history, tools)
    if result.content:
        response = result.content
    elif result.tool_calls:
        function_name = result.tool_calls[0].function.name
        arguments = json.loads(result.tool_calls[0].function.arguments)
        if function_name == "generate_graph":
            try:
                graph_data = arguments["graph_data"]
                output_file_name = f'{TEMP_FILES_FOLDER}/{cl.user_session.get("id")}/{generate_random_file_name()}'
                generated_file_path = await cl.make_async(create_graph_file)(graph_data, output_file_name)
                attached_image = cl.Image(path=generated_file_path, name=output_file_name, display="inline", size="large")
                response_msg.elements = [attached_image]
                response = f'[SUCCESS] Your org chart has been generated successfully'
            except Exception as e:             
                response = f'[ERROR] Problem generating org chart:\n {e}'
        elif function_name == "save_employees_file":
            if message.elements:
                try:
                    attached_files = [file for file in message.elements]
                    employees_file_path = attached_files[0].path
                    save_database_file(employees_file_path, DATABASE_FILE)
                    response = f'[SUCCESS] Employees file have been saved successfully.'
                except Exception as e:             
                    response = f'[ERROR] Problem saving employees file:\n {e}'
            else:
                response = f'[ERROR] No attachment found in your message'
        else:
            response = f"[ERROR] Invalid function"
    else:
        response = f"[ERROR] Invalid response from OpenAI"
    
    response_msg.content = response
    await response_msg.update()
    save_message_to_history(response_msg)


#============================================#

def save_message_to_history(message):
    if cl.user_session.get("chat_history"):
        chat_history = cl.user_session.get("chat_history")
    else:
        chat_history = []
    chat_history.append(message)
    cl.user_session.set("chat_history", chat_history)

def get_conversation_history():
    result = []
    if cl.user_session.get("chat_history"):
        for message in cl.user_session.get("chat_history"):
            if message.author == "User":
                result.append({"role": "user", "content": message.content})
            else:
                result.append({"role": "assistant", "content": message.content})
    return result

def generate_random_file_name():
    return f'{int(time.time_ns())}_{random.randint(0,10000)}'

def create_graph_file(graph_data, output_file_name):
    graph = Source(graph_data)
    graph.render(output_file_name, format='png', cleanup=True)
    return (output_file_name + ".png")

def read_all_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        result = file.read()
    return result

def save_database_file(input_file_path, database_file_path):
    with open(input_file_path, 'r') as src_file:
        content = src_file.read()
    with open(database_file_path, 'w') as dest_file:
        dest_file.write(content)

def get_gpt_response(ai_client, gpt_model, temperature, system_prompt, conversation_history, tools):
    system_prompt = f'{system_prompt} Here is the employees database in CSV format:\n{read_all_text_from_file(DATABASE_FILE)}'
    prompt_structure = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history:
        prompt_structure.append(msg) 
    try:
        response = ai_client.chat.completions.create(
            model = gpt_model,
            messages = prompt_structure,
            temperature = temperature,
            tools = tools,
            tool_choice = "auto"
        )
        return response.choices[0].message
    except Exception as e:
        return SimpleNamespace(content=f"[ERROR] Problem calling OpenAI API:\n {e}")