🧠 AI Agent with LangGraph and Tools
This project is a smart AI agent powered by LangGraph and GPT‑4.1, designed using a graph-based architecture. It can interact with external tools like web search and date retrieval. The agent is built to be modular, reusable, and stateful.

🚀 Key Features
⚙️ Modular Stateful Agent: Uses StateGraph to manage conversational state and decision-making.

🔧 Tool Integration: Supports tools like tavily_tool for web search and get_current_date_tool for date fetching.

🔁 Conditional Flow Control: Determines whether to call a tool or return a final answer based on the latest message.

🧱 Clean, Extendable Architecture: Easily expandable for new tools or model variations.

This is the Graph:
![alt text](image-1.png)


📂 File Structure
pgsql
Copy
Edit
Langgraph.py                # Main agent logic, graph definition, and tool setup
tools/
├── current_date.py         # Tool to fetch the current date
├── tavily_search.py        # Tool to perform web search
⚙️ Getting Started
Clone the repository:

bash
Copy
Edit
git clone https://github.com/sl-93/AI-Agent-with-Langgraph-and-Tools.git
cd AI-Agent-with-Langgraph-and-Tools
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Set your OpenAI-compatible API key:
Open Langgraph.py and replace:

python
Copy
Edit
openai_api_token = "YOUR_API_KEY"
Run the agent:

bash
Copy
Edit
python Langgraph.py
Interact with the agent:
Type your message and receive a response from the agent (with tool use if needed).

🧠 Agent Logic Overview
The user message is stored in the agent's state.

The agent is initialized with the selected tools and the GPT‑4.1 model.

The graph checks whether the model response requires tool execution:

If yes → routes to action node (tools are called)

If no → conversation ends with the model's response

If a tool is used, its result is added to the message list and passed back to the agent.

The process continues until a final answer is generated.

🧪 Adding New Tools
To add a new tool:

Create a Python file in the tools/ folder (e.g., weather_tool.py)

Define the tool following the standard format: Tool(name=..., func=...)

Import and register the tool in Langgraph.py:

python
Copy
Edit
from tools.weather_tool import weather_tool
tools_list = [tavily_tool, get_current_date_tool, weather_tool]

