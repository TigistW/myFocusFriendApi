import os
from dotenv import load_dotenv
import openai
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import json
from cachetools import TTLCache


# # load_dotenv()
# load_dotenv(override=True, default_values={"CACHE_SIZE": "1000", "CACHE_TIME": "3600"})
if not os.getenv("CACHE_SIZE"):
    os.environ["CACHE_SIZE"] = "1000"

if not os.getenv("CACHE_TIME"):
    os.environ["CACHE_TIME"] = "3600"
    
    
openai.api_key = os.getenv("OPENAI_API_KEY")
CACHE_SIZE, CACHE_TIME = int(os.getenv("CACHE_SIZE")), int(os.getenv("CACHE_TIME"))

current_dir = os.path.dirname(__file__)
cache = TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TIME)

def load_instruction(filename):
    f = open(filename)
    return f.read()

def load_chat(address, is_new_chat):
    if is_new_chat:
        if address in cache:
            cache.pop(address)
        cache[address] = load_new_chat()
        return cache[address]
    
    if address not in cache:
        raise Exception("Chat not found try again")
    
    return cache[address]

def load_new_chat():
    chat = ChatOpenAI(temperature=0)
    instructions_file = os.path.join(current_dir,'gpt_instructions.txt')
    instructions = load_instruction(instructions_file)
    system_message_prompt = SystemMessagePromptTemplate.from_template(instructions)

    system_message_prompt.format_messages()
    human_template = """
    You are a humam friend that involves in random human conversations. Your output should always just be JSON Response with the message field.
    Your JSON response format should have the following keys:
    message.if the user provides no input, you should prompt them to provide an input.

    input = {input}
    """
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        MessagesPlaceholder(variable_name="history"),
        human_message_prompt
    ])

    memory = ConversationBufferMemory(input_key = "input", output_key="response", return_messages=True)
    conversation = ConversationChain(memory=memory, prompt=chat_prompt, llm=chat)
    return conversation