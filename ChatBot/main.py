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

def main():
    user_input = input("Enter your input: ")
    messages = [{"role": "system", "content": "You are Fynn, an all-around financial analyst for the user's financing, budgeting, and investments. You will provide the user with financial advice and information."}]
    messages = [{"role": "user", "content": user_input}]
    
    # 1) Call the model with your tools
    completion = client.chat.completions.create(
        model="gpt-4o",  # or gpt-4-0613, if you have access
        messages=messages,
        tools=tools,
    )
    
    # 2) Check if the model decided to call any tools
    tool_calls = completion.choices[0].message.tool_calls
    
    if not tool_calls:
        # No function calls => just print the model's text response
        print(completion.choices[0].message.content)
        return
    
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
    
    # Finally, print the model’s integrated answer
    print(completion_2.choices[0].message.content)

if __name__ == "__main__":
    main()