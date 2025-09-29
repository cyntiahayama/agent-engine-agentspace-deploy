import vertexai
from vertexai import agent_engines
import importlib
import os
import logging
from dotenv import load_dotenv, dotenv_values, set_key

# Load environment variables from .env file
load_dotenv()

# Configure the logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
STAGING_BUCKET = os.environ["STAGING_BUCKET"]
AGENT_DISPLAY_NAME = os.environ["AGENT_DISPLAY_NAME"]
AGENT_FOLDER = os.environ["AGENT_FOLDER"]
PROJECT_NUMBER = os.environ["GOOGLE_CLOUD_PROJECT_NUMBER"]

# Deploy the agent to Agent Engine
def deploy_agent():

    root_agent = importlib.import_module(f"{AGENT_FOLDER}.agent")
    root_agent = root_agent.root_agent

    # Load the agent from the AGENT_FOLDER folder
    app = agent_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket="gs://"+STAGING_BUCKET,
    )

    # Get the env variables to send in the agent deploy
    agent_env_vars = dict(dotenv_values(".env"))
    keys_to_copy = ["MODEL", "AGENT_APP_NAME", "DATASTORE_LOCATION", "DATASTORE_ID", "AGENT_AUTH_OBJECT_ID", "AGENTSPACE_APP_ID_SEARCH"]
    agent_env_vars = dict((k, agent_env_vars[k]) for k in keys_to_copy if k in agent_env_vars)

    logger.info(os.path.join("./", AGENT_FOLDER, 'agent.py'))
    logger.info(f"AGENT_DISPLAY_NAME: {AGENT_DISPLAY_NAME}")

    remote_app = agent_engines.create(
        app,
        requirements=os.path.join("./", AGENT_FOLDER, 'requirements.txt'),
        extra_packages=[os.path.join("./", AGENT_FOLDER, 'agent.py')],
        display_name=AGENT_DISPLAY_NAME,
        env_vars=agent_env_vars
    )

    resource_name = remote_app.resource_name

    logger.info(f"Resource name: {resource_name}")

    # Save the Reasoning Engine ID to the .env file
    set_key(dotenv_path=".env", key_to_set="REASONING_ENGINE_ID", value_to_set=resource_name.split('/')[-1])


# Update the agent in Agent Engine
def update_agent():

    root_agent = importlib.import_module(f"{AGENT_FOLDER}.agent")
    root_agent = root_agent.root_agent

    # Load the agent from the AGENT_FOLDER folder
    app = agent_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket="gs://"+STAGING_BUCKET,
    )

    # Get the env variables to send in the agent deploy
    agent_env_vars = dict(dotenv_values(".env"))
    keys_to_copy = ["MODEL", "AGENT_APP_NAME", "DATASTORE_LOCATION", "DATASTORE_ID", "AGENT_AUTH_OBJECT_ID", "AGENTSPACE_APP_ID_SEARCH"]
    agent_env_vars = new_dict = dict((k, agent_env_vars[k]) for k in keys_to_copy if k in agent_env_vars)

    logger.info(dict(agent_env_vars))

    REASONING_ENGINE_ID = os.environ["REASONING_ENGINE_ID"]
    resource_name = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}"

    remote_app = agent_engines.update(
        app,
        resource_name=resource_name,
        requirements=os.path.join("./", AGENT_FOLDER, 'requirements.txt'),
        extra_packages=['agent.py'],
        display_name=AGENT_DISPLAY_NAME,
        env_vars=agent_env_vars
    )

    resource_name = remote_app.resource_name

    logger.info(f"Resource name: {resource_name}")

    # Save the Reasoning Engine ID to the .env file
    set_key(dotenv_path=".env", key_to_set="REASONING_ENGINE_ID", value_to_set=resource_name.split('/')[-1])