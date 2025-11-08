from langchain_groq.chat_models import ChatGroq
from dotenv import load_dotenv
from agent.prompts import *
from agent.tools import *
from agent.states import *
from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain.agents import create_agent


_ = load_dotenv()

PROJECT_ROOT.mkdir(parents=True, exist_ok=True)

class InputState(TypedDict):
    user_prompt: str

class PlannerState(TypedDict):
    plan: Plan

class ArchitectState(TypedDict):
    task_plan: TaskPlan

llm = ChatGroq(model="llama-3.3-70b-versatile")
coder_llm = ChatGroq(model="qwen/qwen3-32b")
tools = [write_file, read_file, list_files, get_current_directory, run_cmd]




def planner_agent(state: InputState) -> PlannerState:
    prompt = planner_prompt(state["user_prompt"])
    response = llm.with_structured_output(Plan).invoke(prompt)
    state = PlannerState(plan=response)
    return state

def architect_agent(state: PlannerState) -> ArchitectState:
    plan = state["plan"]
    prompt = architect_prompt(plan)
    response = llm.with_structured_output(TaskPlan).invoke(prompt)
    state = ArchitectState(task_plan=response)
    return state

def coding_stator(state: ArchitectState) -> CoderState:
    task_plan = state["task_plan"]
    state = CoderState(task_plan=task_plan,
                       current_step_idx=0,
                       current_file_content="",
                       status="CODER"
                       )
    return state

def coder_agent(state: CoderState) -> CoderState:
    agent = create_agent(model=coder_llm,tools=tools,system_prompt=coder_system_prompt())
    steps = state.task_plan.implementation_steps
    idx = state.current_step_idx
    content = state.current_file_content
    if not content:
        content = read_file.invoke(steps[idx].file_path)
    prompt = f"""Complete the specific step mentioned as 'current step' by reviewing other files and full task plan in the project to make every files connected effectively and working efficiently.
                Full task: {state.task_plan}
                current step:{steps[idx]}
                content currently in the file:{content}"""
    agent.invoke({"messages":[{"role":"user","content":prompt}]})
    idx = idx + 1
    state.current_step_idx = idx
    state.current_file_content = ""
    if idx >= len(steps):
        status = "DONE"
    else:
        status = "CODER"
    state.status = status
    return state

def routing_function(state:CoderState) -> dict:
    status = state.status
    return status




graph = StateGraph(InputState)

graph.add_node("Planner",planner_agent)
graph.add_node("Architect",architect_agent)
graph.add_node("Stator",coding_stator)
graph.add_node("Coder",coder_agent)

graph.set_entry_point("Planner")
graph.add_edge("Planner","Architect")
graph.add_edge("Architect","Stator")
graph.add_edge("Stator","Coder")
graph.add_conditional_edges("Coder",routing_function,{"CODER":"Coder","DONE":END})

app = graph.compile()

resp = app.invoke({"user_prompt":"make a login page using html css and js."})