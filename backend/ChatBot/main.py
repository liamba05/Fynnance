from openai import OpenAI
import json
from tools_list import function_registry 
import os
import sys

# add to path so we can import other functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import the API key manager
from EncryptionKeyStorage.API_key_manager import APIKeyManager
os.environ['GOOGLE_CLOUD_PROJECT'] = '258766016727'
api_key_manager = APIKeyManager()

client = OpenAI(api_key=api_key_manager.get_api_key('openai'))

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

def get_user_context(user_data_collection):
    """Get user's GPT data and format it into context messages for the chat.
    
    This function retrieves the user's goals, preferences, memories, and conclusions
    from Firebase and formats them into appropriate context messages that help guide
    the conversation and maintain context across chat sessions.
    """
    messages = []
    
    # Get goals if they exist
    goals = user_data_collection.get_goals()
    if goals:
        messages.append({
            "role": "developer",
            "content": f"The user has provided their financial goals: {goals}. These should be your overarching focuses. The user's goals are your top priority as their financial advisor. If the goals seem outdated or circumstances have changed significantly, you may suggest updating them."
        })
    
    # Get preferences if they exist
    preferences = user_data_collection.get_preferences()
    if preferences:
        messages.append({
            "role": "developer",
            "content": f"The user has indicated these preferences about how they should be communicated with: {preferences}. Adapt your responses to match these preferences in terms of detail level, risk tolerance, and communication style."
        })
    
    # Get memories if they exist (for internal context)
    memories = user_data_collection.get_memories()
    if memories:
        # Format memories as a bulleted list
        memory_list = "\n• " + "\n• ".join(memories)
        messages.append({
            "role": "developer",
            "content": f"Based off your previous interactions with the user, here are some important points that we decided to remember: {memory_list}. Use these points to provide more personalized financial advice to better achieve the user's goals and give more personalized advice."
        })
    
    # Get conclusions if they exist (for internal context)
    conclusions = user_data_collection.get_conclusions()
    if conclusions:
        messages.append({
            "role": "developer",
            "content": f"Based on previous interactions, these conclusions have been drawn about the user's financial situation: {conclusions}. Consider these insights when providing advice, but be ready to update them if new information suggests otherwise."
        })
    
    return messages

def initialize_chat():
    """Return the initial messages object for the start of the chat."""
    messages = []
    
    # Add the initial system prompt
    messages.append({
        "role": "system",
        "content": "You are Fynn, an all-around financial analyst for the user's financing, budgeting, and investments. You will provide the user with financial advice and information. \
             At any point, if you need more information to make a tools/function call, ask the user and make the call after. Do not make a call early, you can ask the user follow-up questions to get the necessary information.\
             ONLY MAKE A CALL FOR A FUNCTION THAT EXISTS, do not offer to get data on information that you cannot access or will cause an API error."
    })
    
    # Get user context from Firebase and add it at initialization
    try:
        from UserDataCollection.user_data_collection import UserDataCollection
        user_data = UserDataCollection()
        context_messages = get_user_context(user_data)
        messages.extend(context_messages)
    except Exception as e:
        print(f"Warning: Could not load user context: {str(e)}")
    
    return messages

def get_response(messages):
    """Get a response from GPT with function calling skills.
    It uses the most recent user_input in messages as the question.
    
    Returns: response, messages (updated)
    """
    # Call the model with the tools (functions) available
    completion = client.chat.completions.create(
        model="gpt-4o", 
        messages=messages,
        tools=tools,
    )
    
    # Check if the model decided to call any tools
    tool_calls = completion.choices[0].message.tool_calls
    
    # if it didn't call any tools, just return the text response
    if not tool_calls:
        return completion.choices[0].message.content, messages

    # If there are tool calls:
    # Append the entire assistant message (with the function call info)
    messages.append(completion.choices[0].message)
    
    # Execute each tool call from this message
    for tc in tool_calls:
        fn_name = tc.function.name
        fn_args = json.loads(tc.function.arguments)
        
        result = execute_function(fn_name, fn_args)
        
        # Append the tool's result message
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,   # must match the id from the model
            "content": json.dumps(result)  # always a string
        })
    
    # Call the model again with updated messages
    completion_2 = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )
    
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
