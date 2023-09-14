from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts.prompt import PromptTemplate
from database import save_message_to_db, connect_2_db
import os 
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
import openai

load_dotenv()
default_prompt = os.getenv('DEFAULT_PROMPT')

def chain_setup(user_id, user_name):
    # get history msg and add it to memmory
    memory = ConversationBufferMemory()

    _, message_history = connect_2_db()

    conv = message_history.find_one({'user_id': user_id})
    
    if conv:
        messages = conv['messages']

        # Calculate how many messages are available
        num_messages = len(messages)
    
        # Start index for messages to be added
        start_index = max(num_messages - 5, 0)

        # Add messages to memory
        for i in range(start_index, num_messages):
            # Get message
            message = messages[i]

            #check if it is user/bot msg
            if 'user' in message:
                memory.chat_memory.add_user_message(message['user'])
            elif 'bot' in message:
                memory.chat_memory.add_ai_message(message['bot'])
    else:
        print("No previous conversation history found for this user.")


    chat = ChatOpenAI(temperature=0.75,
                      model=os.getenv("OPENAI_MODEL"),
                      openai_api_key=os.getenv("OPENAI_API_KEY"))

    
    memory.ai_prefix = os.getenv('AI_PREFIX')
    memory.human_prefix = os.getenv('HUMAN_PREFIX')
    
    template = default_prompt + """
    Наш текущий диалог:
    {history}
    Макс: {input}
    Соня: 
    """
    prompt = PromptTemplate(input_variables=["history", "input"], template=template)


    conversation = ConversationChain(
        prompt=prompt,
        llm=chat, 
        verbose=True, 
        memory=memory
        )
    
    return conversation


def get_chain_response(user_id, user_text, user_name):
      conv_chain = chain_setup(user_id=user_id, user_name=user_name)
      out = conv_chain(user_text)
      print(out['history'])
      return out['response']
      
      