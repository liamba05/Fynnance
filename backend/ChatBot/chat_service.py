import json
from openai import OpenAI
from tools_list import function_registry 

from EncryptionKeyStorage.API_key_manager import APIKeyManager
from UserDataCollection.user_data_collection import UserDataCollection

class ChatService:
    def __init__(self):
        self.api_key_manager = APIKeyManager()
        self.client = OpenAI(api_key=self.api_key_manager.get_api_key('openai'))
        self.tools = self._build_tools()

    def _build_tools(self):
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
        return tools

    def execute_function(self, name, args):
        """Executes a function from the registry by name with JSON-decoded args."""
        if name not in function_registry:
            return {"error": f"Function '{name}' not found in registry."}
        func = function_registry[name]["function"]
        return func(**args)

    def get_user_context(self, user_data_collection):
        """Retrieve and format user context messages."""
        messages = []
        
        goals = user_data_collection.get_goals()
        if goals:
            messages.append({
                "role": "system",
                "content": f"The user has provided their financial goals: {goals}. These should be your overarching focuses. The user's goals are your top priority as their financial advisor. If the goals seem outdated or circumstances have changed significantly, you may suggest updating them."
            })
        
        preferences = user_data_collection.get_preferences()
        if preferences:
            messages.append({
                "role": "system",
                "content": f"The user has indicated these preferences about how they should be communicated with: {preferences}. Adapt your responses to match these preferences in terms of detail level, risk tolerance, and communication style."
            })
        
        memories = user_data_collection.get_memories()
        if memories:
            memory_list = "\n• " + "\n• ".join(memories)
            messages.append({
                "role": "system",
                "content": f"Based off your previous interactions with the user, here are some important points that we decided to remember: {memory_list}. Use these points to provide more personalized financial advice to better achieve the user's goals and give more personalized advice."
            })
        
        return messages

    def initialize_chat(self, user_id):
        """Initialize chat messages with system prompt and user context."""
        messages = []
        messages.append({
            "role": "system",
            "content": (
                "You are Fynn, an all-around financial analyst for the user's financing, budgeting, and investments. "
                "You will provide the user with financial advice and information. "
                "At any point, if you need more information to make a tools/function call, ask the user and make the call after. "
                "Do not make a call early, you can ask the user follow-up questions to get the necessary information. "
                "ONLY MAKE A CALL FOR A FUNCTION THAT EXISTS, do not offer to get data on information that you cannot access or will cause an API error."
            )
        })

        try:
            user_data = UserDataCollection(user_id)
            context_messages = self.get_user_context(user_data)
            messages.extend(context_messages)
        except Exception as e:
            print(f"Warning: Could not load user context: {str(e)}")
        
        return messages

    def get_response_stream(self, messages, prompt):
        """Get a streaming response from GPT with function calling."""
        messages.append({"role": "user", "content": prompt})
        
        completion = self.client.chat.completions.create(
            model="gpt-4o", 
            messages=messages,
            tools=self.tools,
            stream=True,
        )

        for chunk in completion:
            if 'choices' in chunk and len(chunk['choices']) > 0:
                choice = chunk['choices'][0]
                if 'delta' in choice and 'content' in choice['delta']:
                    content = choice['delta']['content']
                    if content:
                        yield f"data: {content}\n\n"
                elif 'finish_reason' in choice and choice['finish_reason'] == 'stop':
                    break 