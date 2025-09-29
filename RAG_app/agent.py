import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.genai import types
from google.auth import default
from google.auth import transport
import requests
from google.adk.tools import ToolContext, FunctionTool
import logging

load_dotenv()

# Configura o logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MODEL = os.getenv("MODEL")
AGENT_APP_NAME = os.getenv("AGENT_DISPLAY_NAME")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("DATASTORE_LOCATION")
DATA_STORE_ID = os.getenv("DATASTORE_ID")
AUTH_NAME = os.getenv("AGENT_AUTH_OBJECT_ID")
AGENTSPACE_APP_ID = os.getenv("AGENTSPACE_APP_ID_SEARCH")

class DatastoreService:
    def __init__(self, access_token: str):
        self.access_token = None
        if access_token: 
            self.access_token = access_token
        else: 
            creds, project_id = default()
            auth_req = transport.requests.Request()  # Use google.auth here
            creds.refresh(auth_req)
            access_token = creds.token
            self.access_token = access_token


    def search_datastore(self, project_id, location, datastore_id, query):
        # Define API endpoint and headers
        url = f"https://{location}-discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{DATA_STORE_ID}/servingConfigs/default_search:answer"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # Define request data with placeholders for query
        data = {
            "query": {"text":f"{query}"},
            "searchSpec": {
                "searchParams": {
                    "maxReturnResults": 5
                }
                }
            }

        # Make POST request
        response = requests.post(url, headers=headers, json=data)
        
        logger.info(response.text)
        
        try:            
            return response.json()['answer']['answerText']
        except Exception as e:
            logger.error(e)
            return print(f"An unexpected error occurred in the Agent: {e}")
        

    def search_streamAssist(self, project_id, location, datastore_id, query):
        # Define API endpoint and headers
        url = f"https://{location}-discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/{location}/collections/default_collection/engines/{AGENTSPACE_APP_ID}/assistants/default_assistant:streamAssist"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # Define request data with placeholders for query
        data = {
            "query": {"text":f"{query}"},
        #    "toolsSpec": {
        #        "vertexAiSearchSpec": {
        #            "dataStoreSpecs": [ { "dataStore": f"projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{datastore_id}" }]
        #        }
        #        }
            }

        # Make POST request
        response = requests.post(url, headers=headers, json=data)
        
#        try:

        agentspace_answer = ""

        for r in response.json():
            if "answer" in r:
                if "replies" in r["answer"]:
                    for rep in r["answer"]["replies"]:
                        if "groundedContent" in rep:
                            if "content" in rep["groundedContent"]:
                                if "thought" not in rep['groundedContent']['content']:
                                    agentspace_answer = f"{agentspace_answer} {r['answer']['replies'][0]['groundedContent']['content']['text']}"

        logger.info(f'"Answer": {agentspace_answer}, "url":{url}')
                                    
        return f'"Answer": {agentspace_answer}, "url":{url}'
        #return agentspace_answer
 #       except Exception as e:
 #           logger.error(e)
 #           return print(f"An unexpected error occurred in the Agent: {e}")



def search_tasks(query: str, tool_context: ToolContext):
        """
        Searches the task registry using the DatastoreService.
        
        Args:
            query (str): The search query string.

        Returns:
            dict: The search results from the DatastoreService in JSON format.
        """
        datastore_service = None
        auth_name= f"temp:{AUTH_NAME}"
        access_token = tool_context.state.get(auth_name)
        if access_token: 
            datastore_service = DatastoreService(access_token)
        else:
           access_token = ""
           datastore_service = DatastoreService(access_token)
        # Call the search method of the DatastoreService with the project ID, App Engine ID, and query
        results = datastore_service.search_streamAssist(PROJECT_ID, LOCATION, DATA_STORE_ID, query) 
        # Return the search results
        return results


task_search_tool = FunctionTool(func=search_tasks)

instruction_prompt = """
Use as tools disponíveis para responder a pergunta do usuário. 
Garanta que a resposta final seja um Markdown válido.
"""

logger.info(f"MODEL: `{MODEL}`")
logger.info(f"AGENT_APP_NAME: `{AGENT_APP_NAME}`")
logger.info(f"PROJECT_ID: `{PROJECT_ID}`")
logger.info(f"LOCATION: `{LOCATION}`")
logger.info(f"DATA_STORE_ID: `{DATA_STORE_ID}`")
logger.info(f"AUTH_NAME: `{AUTH_NAME}`")
logger.info(f"AGENTSPACE_APP_ID: `{AGENTSPACE_APP_ID}`")

root_agent = Agent(
        model=MODEL,
        name="root_agent",
        description="Você é um assistente prestativo que responde as perguntas do usuários usando as ferramentas disponíveis.",
        instruction=instruction_prompt,
        generate_content_config=types.GenerateContentConfig(temperature=1),
        tools = [task_search_tool]
)