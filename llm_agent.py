import os
import json
from clients.custom_mcp_client import CustomMCPClient
from clients.github_mcp_client import GitHubMCPClient
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()  # load environment variables from .env


# This function loads the prompt template from a markdown file.
def load_prompt_template():
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt_template.md')
    with open(prompt_path, 'r', encoding='utf-8') as file:
        english_prompt = file.read()
    return english_prompt


# Define global variables
english_prompt = load_prompt_template()
custom_client = None
github_client = None
github_tools = None
custom_tools = None
llm = "gpt-4.5-preview"

# Define the Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-05-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

#Initialize the OpenAI client
async def connect():
    global custom_client, github_client
    custom_client = CustomMCPClient()
    github_client = GitHubMCPClient()
    await custom_client.connect_to_server()
    await github_client.connect_to_server()

# Get the tools from GitHub and custom clients
async def get_tools():
    global github_tools, custom_tools
    github_tools = await github_client.get_tools()
    custom_tools = await custom_client.get_tools()

    # Merge custom_tools into github_tools
    return str(github_tools.tools)+'\n'+str(custom_tools.tools)

# Check if the tool is available in either GitHub or custom tools
async def check_tool(content: str, messages: list):
    try:
        mcp_tool = json.loads(content)

        if mcp_tool.get("name") in [t.name for t in github_tools.tools]:
            res = await github_client.call_tool(mcp_tool.get("name"), mcp_tool.get("args"))
            messages.append({"role": "user", "content": "the response of api:" + str(res)})
            return True

        if mcp_tool.get("name") in [t.name for t in custom_tools.tools]:
            res = await custom_client.call_tool(mcp_tool.get("name"), mcp_tool.get("args"))
            messages.append({"role": "user", "content": "the response of api:" + str(res)})
            return True

    except Exception as ex:
        print(ex)
        return False

    return False

# Connect MCP clients and get the tools
async def connect_mcp():
    await connect()
    tools = await get_tools()
    prompt = english_prompt.replace('{{tool_lists}}', tools)

    messages = [
        {
            "role": "system",
            "content": prompt
        }
    ]
    return messages

# Get the response from the LLM
def get_response(messages):
    completion = client.chat.completions.create(model=llm, messages=messages)
    return completion
