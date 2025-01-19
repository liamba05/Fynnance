from openai import OpenAI
import os
import sys
# add to path so we can import other functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import the API key manager
from EncryptionKeyStorage.API_key_manager import APIKeyManager
os.environ['GOOGLE_CLOUD_PROJECT'] = '258766016727'
api_key_manager = APIKeyManager()

from UserDataCollection.user_data_collection import UserDataCollection
user_data = UserDataCollection()


def get_memory_from_conversation(messages):
    """Extracts memory items from the conversation messages.

    Loops through the users messages and extracts if anything would be
    helpful to remember for future messages.
    
    Parameters:
        messages (object): The conversation messages.
    Returns:
        list (str): The memory items.
    """

    # only look at messages that are from the user
    user_messages = [m for m in messages if m["role"] == "user"]

    # ask gpt to decide what of the user chats should be deemed memory
    client = OpenAI(api_key=api_key_manager.get_api_key('openai'))

    # RETREIVE THE CURRENT MEMORY SO WE DON'T OVERLAP
    current_memory = user_data.get_memories()
    # add current_memory into the prompts below to gpt

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"developer", "content": f"Of the given messages from a user's conversations, which should be remembered for future interactions? It may be nothing, but keep it short as possible,\
                   and DO NOT REPEAT INFORMATION. SHORT AS POSSIBLE. Specifically focus on little user details that will help you provide better advice in the future. Also, each memory should be freestanding, not relying on another memory peice. You may combine two memories if it will save space in the end. \
                   Remember not to overlap with memory that is already stored: {current_memory}. Return the new memory only in a '|' seperated string that the system will convert into a string list. \
                    User messages: {user_messages}"}],
    )
    new_memory = completion.choices[0].message.content.split("|")
    user_data.add_to_memories(new_memory)
    return new_memory


def save_credit_score(messages):
    """Analyzes the chats and saves the user's credit score
    if applicable.

    Parameters:
        messages (object): The conversation messages.

    Returns:
        int: The credit score if found.
    """
    # only look at messages that are from the user
    user_messages = [m for m in messages if m["role"] == "user"]

    # initialize gpt client
    client = OpenAI(api_key=api_key_manager.get_api_key('openai'))

    # see if the user's credit is stored already
    current_credit = user_data.get_credit_score()

    if current_credit:
        return current_credit

    # ask gpt to update the credit score
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"developer", "content": f"Of the given messages from a user's conversation, extract the user's credit score if it is mentioned, else return -1. Remember \
                   theat the credit score must be inbetween 300 and 850. If the credit score is not mentioned, return -1. If the credit score is mentioned, return the credit score as a string number and nothing else. \
                   "}],
    )
    new_credit = int(completion.choices[0].message.content)
    if new_credit != -1:
        user_data.set_credit_score(new_credit)
    return new_credit



if __name__ == "__main__":

    test_messages = [
        {
            "role": "user",
            "content": "Hi, I'm planning a trip to Italy next summer."
        },
        {
            "role": "assistant",
            "content": "That sounds amazing! Which cities or regions are you planning to visit?"
        },
        {
            "role": "user",
            "content": "I'm thinking of Rome, Florence, and Venice, but I might add more destinations later."
        },
        {
            "role": "assistant",
            "content": "Great choices! Let me know if you need help planning an itinerary or learning about attractions in those cities."
        },
        {
            "role": "user",
            "content": "Also, I love trying new foods, so I'd like to know the best places to eat in those cities."
        },
        {
            "role": "assistant",
            "content": "Italian cuisine is wonderful! I can recommend some must-try dishes and famous restaurants for each city. Do you prefer fine dining or casual eateries?"
        },
        {
            "role": "user",
            "content": "A mix of both would be perfect."
        },
        {
            "role": "assistant",
            "content": "Got it. I'll make sure to provide you with options for both fine dining and casual places in Rome, Florence, and Venice."
        },
        {
            "role": "user",
            "content": "Oh, one more thing: I really enjoy art and history, so museums and historic landmarks are a priority for me."
        },
        {
            "role": "assistant",
            "content": "Italy is rich in art and history! I'll help you find the best museums and landmarks to visit in each city. Let me know if you have specific interests, like Renaissance art or ancient Roman history."
        }
    ]

    print(get_memory_from_conversation(test_messages))

