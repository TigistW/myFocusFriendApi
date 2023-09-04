import os
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
from cachetools import TTLCache


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