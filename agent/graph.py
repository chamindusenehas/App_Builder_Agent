from langchain_groq import ChatGroq
from langchain.agents import create_agent
from dotenv import load_dotenv
from agent.prompts import *
from agent.tools import *
from agent.states import *
from langgraph.graph import StateGraph, END
from typing import TypedDict

_ = load_dotenv()


class AgentState(TypedDict):
    user_prompt: str
    plan: Plan
    architect_plan: TaskPlan
    code: list[str]
    coder_state: CoderState

llm = ChatGroq(model="llama-3.3-70b-versatile")

user_prompt = "make a simplecalculator web application"

def planner_agent(state: AgentState) -> AgentState:
    users_prompt = state["user_prompt"]
    prompt = planner_prompt(users_prompt)
    resp = llm.with_structured_output(Plan).invoke(prompt)
    state["plan"] = resp
    if resp is None:
        raise ValueError("Planner does not return a valid response.")
    return state

def architect_agent(state: AgentState) -> AgentState:
    plan = state["plan"]
    prompt = architect_prompt(plan)
    resp = llm.with_structured_output(TaskPlan).invoke(prompt)
    state["architect_plan"] = resp
    if resp is None:
        raise ValueError("Architect does not return a valid response.")
    return state

def coder_agent(state: AgentState) -> AgentState:
    coder_state = state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(task_plan=state["architect_plan"],current_step_idx=0)
    implementation_steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx >= len(implementation_steps):
        return {"coder_state": coder_state, "status": "DONE"}

    idx = coder_state.current_step_idx
    current_task = implementation_steps[idx]
    existing_content = read_file.invoke({"path": current_task.file_path})
    user_prmpt = f"""
    File path: {current_task.file_path}
    task: {current_task.task_description}
    existing content: {existing_content}"""

    tools = [read_file, write_file, get_current_directory, list_files, run_cmd]

    react = create_agent(llm,tools,system_prompt=coder_system_prompt())
    resp = react.invoke({"messages": [{"role": "user", "content": f"{user_prmpt}"}]})
    print(resp)
    coder_state.current_step_idx = coder_state.current_step_idx + 1
    state["coder_state"] = coder_state
    print("an step completed")
    return state



graph = StateGraph(AgentState)

graph.add_node("Planner", planner_agent)
graph.add_node("Architect", architect_agent)
graph.add_node("Coder", coder_agent)

graph.set_entry_point("Planner")
graph.add_edge("Planner", "Architect")
graph.add_edge("Architect", "Coder")
graph.add_conditional_edges(
    "Coder",
    lambda s: "END" if s.get("status") == "DONE" else "Coder",
    {"END":END, "Coder":"Coder"}
)

app = graph.compile()

response = app.invoke({'user_prompt': user_prompt})

print(response)