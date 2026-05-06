#  Intelligent Task Automation Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange.svg)](https://www.langchain.com/)

An autonomous AI agent system that takes high-level goals, breaks them down into actionable tasks, plans execution, adapts to obstacles, learns from experience, and knows when to ask for human help. This demonstrates advanced agentic AI patterns working together in a production-ready system.

## What This Does

Instead of building agents that follow fixed scripts, this system creates agents that:
- Understand high-level intent and break it down into tasks
- Plan their own execution approach
- Adapt when things go wrong
- Learn from successes and failures
- Know when to escalate to humans

## Key Features

- **Goal Decomposition**: Breaks down high-level goals into actionable tasks
- **Smart Planning**: Creates optimal execution plans with dependency management
- **Tool Execution**: Executes tasks using file operations, git, commands, and web tools
- **Adaptive Learning**: Learns from outcomes and improves strategies over time
- **Human-in-the-Loop**: Knows when to ask for human input or confirmation
- **Chain-of-Thought Reasoning**: Solves complex problems step-by-step
- **Progress Tracking**: Real-time monitoring of goal execution
- **Session Management**: Saves and loads execution sessions

## Architecture

The system uses six specialized agents:

1. **Goal Decomposer Agent**: Breaks down high-level goals into tasks
2. **Planner Agent**: Creates optimal execution plans
3. **Executor Agent**: Executes tasks using available tools
4. **Adaptation Agent**: Learns from outcomes and improves strategies
5. **Human Interface Agent**: Manages human interaction and escalation
6. **Reasoning Agent**: Solves complex problems using chain-of-thought

All agents are coordinated by an Orchestrator that manages the workflow.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd task_automation_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Usage

### Running the Streamlit UI

```bash
streamlit run frontend/streamlit_app.py
```

The UI will open in your browser where you can:
- Enter goals in natural language
- Monitor execution progress
- Provide human input when needed
- View session history
- Explore learned patterns

### Example Goals

- "Set up a new Python project with FastAPI, git repository, and README"
- "Create a new directory structure for a web application"
- "Initialize a git repository and create an initial commit"
- "Download and analyze data from a URL"

## Project Structure

```
task_automation_agent/
├── backend/
│   ├── agents/          # All agent implementations
│   ├── core/            # Orchestrator, memory, progress tracking
│   ├── tools/           # Tool implementations (file, git, web, commands)
│   └── models.py        # Data models
├── frontend/
│   └── streamlit_app.py # Streamlit UI
├── data/
│   ├── sessions/        # Saved execution sessions
│   └── memory/          # Learned patterns
└── tests/               # Test files
```

## Agentic Patterns Demonstrated

This project showcases multiple agentic AI patterns:

- **Goal Setting**: Breaking down high-level objectives
- **Planning**: Creating execution strategies
- **Tool Use**: Executing real-world actions
- **Adaptation**: Learning and improving over time
- **Human-in-the-Loop**: Knowing when to ask for help
- **Reasoning**: Chain-of-thought problem solving
- **Exception Handling**: Graceful failure recovery
- **Prioritization**: Task ordering and resource management
- **Memory**: Storing and retrieving learned patterns

## How It Works

1. **Goal Input**: User provides a high-level goal in natural language
2. **Decomposition**: Goal Decomposer breaks it into actionable tasks
3. **Planning**: Planner creates an optimal execution plan
4. **Execution**: Executor runs tasks using appropriate tools
5. **Adaptation**: System learns from outcomes and updates strategies
6. **Human Escalation**: System asks for input when needed
7. **Memory Storage**: Learned patterns are saved for future use

## Safety Features

- Path validation to prevent operations outside base directory
- Confirmation required for destructive operations
- Safe command execution with allowlists
- Error handling and graceful degradation

## Future Enhancements

- Multi-goal management
- Advanced reasoning capabilities
- More tool integrations
- Visual workflow builder
- Performance analytics dashboard
- Collaborative goal execution

##  Tech Stack

- **LangChain**: Agent framework and orchestration
- **Streamlit**: Web UI
- **Python 3.8+**: Core language
- **File Operations**: File system tools
- **Git Integration**: Version control tools
- **Web Tools**: HTTP requests and web scraping

##  Use Cases

- **Project Setup**: Automate project initialization and setup
- **Task Automation**: Execute complex multi-step tasks
- **Code Generation**: Generate and organize code files
- **Workflow Automation**: Automate repetitive workflows
- **Goal Achievement**: Break down high-level goals into actions

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


