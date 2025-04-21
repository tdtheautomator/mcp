# Model Context Protocol (MCP) Demo

This projects provide a simple implementation of MCP Server and integrating with Azure Open AI.

## Project Features
1. Custom tool to search web for latest news
2. Custom tool to provide latest stock price
3. Custom tool to provide historical stock price
4. Using Github MCP Server (on docker)
5. Simple Gradio Web UI integrated with Azure Open AI


## Usage (CLI)

- Create new virtual environment
```
    python -m venv mcpdev
```
- Activate environment
```
    .\mcpdev\scripts\activate
```
- Install packages
```
    pip install -r requirements.txt
```
- Create .env file in root
- Add variables to .env file 
```
GITHUB_TOKEN=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
```