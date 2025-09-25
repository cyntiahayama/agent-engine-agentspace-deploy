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
AGENT_APP_NAME = 'enterpriseagent'
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("DATASTORE_LOCATION")
DATA_STORE_ID = os.getenv("DATASTORE_ID")
AUTH_NAME = os.getenv("AGENT_AUTH_OBJECT_ID")

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
        url = f"https://{location}-discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{datastore_id}/servingConfigs/default_search:search"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # Define request data with placeholders for query
        data = {
            "query": f"{query}",
            "pageSize":10,
            "queryExpansionSpec":{"condition":"AUTO"},
            "spellCorrectionSpec":{"mode":"AUTO"},
            "relevanceScoreSpec":{"returnRelevanceScore":True},
            "languageCode":"pt-BR",
            "contentSearchSpec":{"snippetSpec":{"returnSnippet":True}},
            "naturalLanguageQueryUnderstandingSpec":{"filterExtractionCondition":"ENABLED"}
            }

        # Make POST request
        response = requests.post(url, headers=headers, json=data)
        
        logger.info(response.text)
        #response_json = response.json()
        #logger.info(response_json['totalSize'])
        #print(response_json)
        return response.text



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
        results = datastore_service.search_datastore(PROJECT_ID, LOCATION, DATA_STORE_ID, query) 
        # Return the search results
        return results


task_search_tool = FunctionTool(func=search_tasks)

instruction_prompt = """
Use as tools disponíveis para responder a pergunta do usuário. 
Garanta que a resposta final seja um Markdown válido.
"""

root_agent = Agent(
        model=MODEL,
        name=AGENT_APP_NAME,
        description="Você é um assistente prestativo que responde as perguntas do usuários usando as ferramentas disponíveis.",
        instruction=instruction_prompt,
        generate_content_config=types.GenerateContentConfig(temperature=1),
        tools = [search_tasks]
)