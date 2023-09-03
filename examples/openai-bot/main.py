from textbase import bot, Message
from textbase.models import OpenAI
from typing import List
import json
import os
import subprocess
import datetime


# Load your OpenAI API key
OpenAI.api_key = "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"

# Prompt for GPT-3.5 Turbo
SYSTEM_PROMPT = """You are chatting with windows virtual assistant. There are no specific prefixes for responses, so you can ask or talk about anything you like.
The AI will respond in a natural, conversational manner. Feel free to start the conversation with any question or topic, and let's have a
pleasant chat!
"""


def get_date_time(args): # returns the current date and time
 return str(datetime.datetime.now())

def run_command(args): # Run a system command (usefull for changing system settings)
    command = args.get("command").split(" ")
    
    try:
        subprocess.run(command)
        return "success"
    except:
        return "some unexpected error occured"


def open_application(args): #Open an application or file located at the specified path
    path = args.get("path")

    try:
        os.startfile(path)
        return "success"
    except:
        return "some unexpected error occured"


functions = [
   
    {
        "name": "open_application",
        "description": "Open an application or file located at the specified path by calling python's os.startfile(path) function",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to the application or file you want to open",
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "run_command",
        "description": "Run a system command using python's subprocess.run() function and return 'success' if the command execution is successful, or 'some unexpected error occurred' if an error occurs.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The system command to be executed",
                }
            },
            "required": ["command"]
        }
    },
    {
    "name": "get_date_time",
    "description": "Get the current date and time as a string representation.",
    "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
}
]


@bot()
def on_message(message_history: List[Message], state: dict = None):


    response_message = OpenAI.generate_with_function_calling(
        system_prompt=SYSTEM_PROMPT,
        message_history=message_history,
        functions=functions,
        model="gpt-3.5-turbo"
    )


    if response_message.get("function_call"):
        
        available_functions = {
            "open_application": open_application,
            "run_command": run_command,
            "get_date_time": get_date_time
        }  

        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]

        function_args = json.loads(
            response_message["function_call"]["arguments"])

        function_response = fuction_to_call(function_args)

        
        response_message = OpenAI.generate_with_function_calling_2nd_time(  
            system_prompt=SYSTEM_PROMPT,
            message_history=message_history,
            functions=functions,
            function_response={
                "role": "function",
                "name": function_name,
                "content": function_response,
            },
            message_response=response_message,
            model="gpt-3.5-turbo"
        )


    response = {
        "data": {
            "messages": [
                {
                    "data_type": "STRING",
                    "value": response_message.content
                }
            ],
            "state": state
        },
        "errors": [
            {
                "message": ""
            }
        ]
    }

    return {
        "status_code": 200,
        "response": response
    }


# examples/openai-bot/main.py
