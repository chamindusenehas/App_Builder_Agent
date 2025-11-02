# App Builder Agent
*A Python-based intelligent system that transforms user prompts into complete application scaffolds.*

---

## 🚀 Overview
App Builder Agent allows you to describe an application in plain language, and it generates a working project structure based on your input.  
It’s designed to speed up prototyping, automate repetitive coding tasks, and serve as a base for AI-driven development workflows.

The agent operates through modular components handling state management, code generation, and structured prompting.

---

## 🧩 Key Features
- Accepts natural language requirements as input
- Generates ready-to-run application structures (HTML, CSS, JS, and Python)
- Modular and extensible architecture:
  - `prompts.py` – prompt handling and parsing logic
  - `tools.py` – utility functions and generation helpers
  - `states.py` – manages agent states during the generation process
  - `graph.py` – controls the workflow of generation
- Produces output in `agent/generated_project/` (automatically ignored by Git)

---

## 📂 Project Structure
- App_Builder_Agent/
- ├── agent/
- │ ├── generated_project/ # Generated applications
- │ ├── graph.py
- │ ├── prompts.py
- │ ├── states.py
- │ └── tools.py
- ├── main.py
- ├── pyproject.toml
- ├── .gitignore
- ├── README.md
- └── .env
---
