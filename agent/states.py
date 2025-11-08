from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class File(BaseModel):
    path: str = Field(description="The path to the file to be created or modified.")
    purpose: str = Field(description="The purpose of the file. e.g. 'Main application logic', 'Data manipulation module', etc.")

class Plan(BaseModel):
    name: str = Field(description="The name of the app to be built")
    description: str = Field(description="The one line description of the app to be built. e.g. 'A web app for managing the user's TO-DO LISTs '")
    tech_stack: str = Field(description="The tech-stack of the app to be built. e.g. 'python', 'javascript', 'react', 'flask', etc. ")
    features: list[str] = Field(description="The list of features that the app needs to have. e.g. 'User authentication', 'data visualization', etc. ")
    files: list[File] = Field(description="A list of files to be created, each with a 'path' and 'purpose'.")

class ImplementationTask(BaseModel):
    file_path: str = Field(description="The path to the file to be created or modified.")
    task_description: str = Field("A detailed description of the task to be performed on the file, e.g. 'add user authentication', 'implement data processing logic', etc.")

class TaskPlan(BaseModel):
    implementation_steps: list[ImplementationTask] = Field("A list of steps to be taken to implement the task")
    model_config = ConfigDict(extra="allow")


class CoderState(BaseModel):
    task_plan: TaskPlan = Field(description="The plan for the task to be implemented")
    current_step_idx: int = Field(0, description="The index of the current step in the implementation steps")
    current_file_content: Optional[str] = Field(None, description="The content of the file currently being edited or created")
    status: str = Field(description="The status of the task")