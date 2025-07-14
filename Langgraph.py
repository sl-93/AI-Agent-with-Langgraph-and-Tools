# Import necessary libraries
import os
from typing import TypedDict, Annotated, Sequence, Literal
import operator
from datetime import date

# Langchain specific imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# LangGraph imports (Updated based on recent versions)
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode  # Preferred way to handle tool execution
from tools.current_date import get_current_date_tool
from tools.tavily_search import tavily_tool


openai_api_token = "YOUR_API_TOKEN"


# Initialize the OpenAI model
llm = ChatOpenAI(model = "gpt-4.1-mini", api_key=openai_api_token, base_url="https://api.metisai.ir/openai/v1", temperature = 0, streaming = False)



# Define the Agent State
class AgentState(TypedDict):
  # AgentState is the name of the dictionary (used to represent the agent's state in the workflow)
  # It has one key: "messages", which holds a list of messages (from the user, model, tools).
  # BaseMessage is the type used to represent each message in that list.
  # operator.add tells Langgraph to append new messages to the list during execution.
  messages: Annotated[Sequence[BaseMessage], operator.add]


tools_list = [tavily_tool,
                     get_current_date_tool]

  # Define node that the binds the tool(s) to the LLM
# This format is useful when we want to reuse the same model logic with different tools.
# We are building modular, reusable parts for our AI workflow.
# The outer function ( make_call_model_with_tools(tools) ) knows about the tools and returns a customized inner function.
# The inner function ( call_model_with_tools(state) ) knows how to use the current state (conversation history) and actually runs the model with tools.

def make_call_model_with_tools(tools: list):
  def call_model_with_tools(state: AgentState):
    messages = state["messages"]

    model_with_tools = llm.bind_tools(tools)

    response = model_with_tools.invoke(messages)

    return {"messages": [response]}

  return call_model_with_tools


# Define conditional Edge logic
# This function checks the most recent message in the state and decides whether to route to the 'action' node or END.
# This function is used to control the flow of the agent, it's a traffic signal deciding where to send the agent next.
# If the message includes a tool call, it routes to the next step ( the action node, where the tool is actually used )
# I there is no tool call, it ends the conversation (__end__).

def should_continue(state: AgentState) -> Literal["action", "__end__"]:
    """Determines the next step: continue with tools or end."""
    last_message = state["messages"][-1]

    # Check if the last message is an AIMessage with tool_calls
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print("DEBUG: Decision: continue (route to action)")
        return "action"  # Route to the node named "action"
    else:
        print("DEBUG: Decision: end (route to END)")
        return END  # Special value indicating the end of the graph
    

    # ToolNode is a prebuilt ready-to-use node from LangGraph that is specifically designed to run external tools
# like search, calculator, database query
from langgraph.prebuilt import ToolNode

def build_graph_one_tool(tools_list):

    # Let's Instantiate ToolNode
    tool_node = ToolNode(tools_list)

    # Define the call_node_fn, which binds the tools to the LLM and calls OpenAI API
    call_node_fn = make_call_model_with_tools(tools_list)

    # Build the Graph with One Tool using ToolNode
    graph_one_tool = StateGraph(AgentState)

    # Add nodes
    graph_one_tool.add_node("agent", call_node_fn)

    # Add the ToolNode instance directly, naming it "action"
    graph_one_tool.add_node("action", tool_node)

    # Set entry point
    graph_one_tool.set_entry_point("agent")

    # Add a conditional edge from the agent
    # The dictionary maps the return value of 'should_continue' ("action" or END)
    # to the name of the next node ("action" or the special END value).
    graph_one_tool.add_conditional_edges(
        "agent",  # Source node name
        should_continue,  # Function to decide the route
        {"action": "action", END: END},  # Mapping: {"decision": "destination_node_name"}
    )

    # Add edge from action (ToolNode) back to agent
    graph_one_tool.add_edge("action", "agent")

    # Compile the graph
    app = graph_one_tool.compile()

    # Visualize
    # print(app.get_graph().draw_mermaid_png())

    return app


def app_call(app, messages):
    # Initialize the state with the provided messages
    initial_state = {"messages": [HumanMessage(content=messages)]}

    # Invoke the app with the initial state
    final_state = app.invoke(initial_state)

    # Iterate through the messages in the final state
    for i in final_state["messages"]:
        # Print the type of the message in markdown format
        print(i.type)
        # Print the content of the message in markdown format
        print(i.content)
        # Print any additional kwargs associated with the message
        if i.additional_kwargs != {}:
            print(i.additional_kwargs)

    # Return the content of the last message and the final state
    return final_state["messages"][-1].content, final_state


app = build_graph_one_tool(tools_list)



messages = input("What is in your mind?")
output, history = app_call(app, messages)

print("\n==================== OUTPUT ====================")
print(output)
