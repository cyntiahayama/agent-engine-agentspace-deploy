import os
from dotenv import load_dotenv
from agentspace_manager import AgentspaceManager

load_dotenv()

PROJECT_ID=os.getenv('GOOGLE_CLOUD_PROJECT_NUMBER')
LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION')
AGENTSPACE_APP_ID = os.getenv('AGENTSPACE_APP_ID')
AGENTSPACE_APP_ID = "apagar_1751381593128"

client = AgentspaceManager(project_id=PROJECT_ID,app_id=AGENTSPACE_APP_ID, location="global")

resp = client.list_agents()

print(AGENTSPACE_APP_ID)

agents = resp["agents"]
for agent in agents:
        print(agent)
        print(agent["name"])
        print(agent["displayName"])
        print("adk: -------------------------------")
        if agent.get("adkAgentDefinition"):
           print(agent["adkAgentDefinition"]["provisionedReasoningEngine"]["reasoningEngine"])
           if "authorizations" in agent["adkAgentDefinition"]: 
                   print(agent["adkAgentDefinition"]["authorizations"])
        print("--------")
