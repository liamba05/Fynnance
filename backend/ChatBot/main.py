from openai import OpenAI
import json
from functions import function_registry 

client = OpenAI(api_key="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")

# Build the tools list from function registry
tools = []
for func_name, func_def in function_registry.items():
    tools.append(
        {
            "type": "function",
            "function": {
                "name": func_name,
                "description": func_def["description"],
                "parameters": func_def["parameters"],
                "strict": True,
            },
        }
    )

def execute_function(name, args):
    """Executes a function from the registry by name with JSON-decoded args."""
    if name not in function_registry:
        return {"error": f"Function '{name}' not found in registry."}
    # the actual callable
    func = function_registry[name]["function"]
    return func(**args)

def initialize_chat():
    """Return the initial messages object for the start of the chat. """
    return [{"role": "developer", "content": "You are Fynn, an all-around financial analyst for the user's financing, budgeting, and investments. You will provide the user with financial advice and information. \
             At any point, if you need more information to make a tools/function call, ask the user and make the call after. Do not make a call early, you can ask the user follow-up questions to get the necessary information.\
             ONLY MAKE A CALL FOR A FUNCTION THAT EXISTS, do not offer to get data on information that you cannot access or will cause an API error."}]

def get_response(messages):
    """Get a response from GPT with function calling skills.
    It uses the most recen user_input in messages as the question.
    
    Returns: reponse, messages (updated)
    """

    # 1) Call the model with the tools (functions) availible
    completion = client.chat.completions.create(
        model="gpt-4o", 
        messages=messages,
        tools=tools,
    )
    
    # 2) Check if the model decided to call any tools
    tool_calls = completion.choices[0].message.tool_calls
    
    # if it didn't call any tools, just return the text response
    if not tool_calls:
        return completion.choices[0].message.content, messages

    # If there are tool calls:
    # Append the entire assistant message (with the function call info)
    # so the model will “see” that it already asked for a function
    messages.append(completion.choices[0].message)
    
    # 3) Execute each tool call from this message
    for tc in tool_calls:
        fn_name = tc.function.name
        fn_args = json.loads(tc.function.arguments)
        
        result = execute_function(fn_name, fn_args)
        
        # 4) Append the tool’s result message
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,   # must match the id from the model
            "content": json.dumps(result)  # always a string
        })
    
    # 5) Call the model again with updated messages
    completion_2 = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )
    
    # Finally, return the model’s integrated answer
    return completion_2.choices[0].message.content, messages


def ask_question(messages, question):
    """Ask a question to the model and return the response AND the messages object."""
    messages.append({"role": "user", "content": question})
    response, messages =  get_response(messages)
    return response, messages


def main():
    messages = initialize_chat()
    print("Welcome to Fynn, your financial analyst assistant. Ask me anything about finance, budgeting, and investments.")
    while True:
        question = input("You: ")
        response, messages = ask_question(messages, question)
        print("Fynn:", response)

if __name__ == "__main__":
    main()
