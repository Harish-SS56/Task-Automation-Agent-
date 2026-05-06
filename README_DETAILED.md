# Intelligent Task Automation Agent

An autonomous AI-powered agent system that takes high-level goals, intelligently breaks them down into actionable tasks, creates optimal execution plans, adapts to obstacles, learns from experience, and knows when to escalate to humans.

## 🎯 Overview

This project demonstrates advanced agentic AI patterns working together in a production-ready system. Instead of following fixed scripts, the agents understand intent, plan their own approach, adapt when things go wrong, learn from successes and failures, and escalate to humans when needed.

### Key Insight
Rather than building single monolithic agents, this system orchestrates **six specialized agents**, each with a specific role and expertise, working together to accomplish complex multi-step tasks autonomously.

---

## ✨ Key Features

- **Goal Decomposition**: Automatically breaks down high-level goals into specific, actionable tasks
- **Smart Planning**: Creates optimal execution plans with dependency management and parallel execution opportunities
- **Tool Execution**: Executes tasks using multiple tools (file operations, git, commands, web requests)
- **Adaptive Learning**: Learns from outcomes and improves strategies over time
- **Human-in-the-Loop**: Knows when to ask for human input or confirmation on complex decisions
- **Chain-of-Thought Reasoning**: Solves complex problems step-by-step with detailed reasoning
- **Progress Tracking**: Real-time monitoring of goal execution with detailed status updates
- **Session Management**: Saves and loads execution sessions for history and learning
- **Memory System**: Stores learned patterns and adapts strategies based on past experience

---

## 🏗️ Architecture

### System Components

#### 1. **Six Specialized Agents**

| Agent | Role | Responsibility |
|-------|------|-----------------|
| **Goal Decomposer** | Break down goals | Analyzes goal complexity, identifies sub-goals, creates task hierarchy |
| **Planner** | Create execution plans | Orders tasks by dependencies, identifies parallelization opportunities |
| **Executor** | Execute tasks | Runs tasks using available tools, handles errors, retries on failure |
| **Adaptation Agent** | Learn & improve | Analyzes outcomes, updates strategies, stores learned patterns |
| **Human Interface** | Manage escalation | Detects when human input needed, presents options, confirms actions |
| **Reasoning Agent** | Solve complex problems | Uses chain-of-thought for complex decisions and problem-solving |

#### 2. **Core Systems**

- **Orchestrator**: Coordinates all agents and manages workflow execution
- **Memory Manager**: Stores learned patterns, execution history, and user preferences
- **Progress Tracker**: Monitors task execution and provides real-time progress updates
- **Tool Registry**: Manages available tools (file operations, git, web, commands)

#### 3. **Data Flow**

```
User Goal (Natural Language)
    ↓
[Goal Decomposer] → Task Breakdown with Dependencies
    ↓
[Planner] → Execution Plan with Priorities & Parallelization
    ↓
[Orchestrator] → Coordinate Execution
    ↓
    ├─→ [Executor] → Execute Task
    │       ↓
    │   Execution Result
    │       ↓
    ├─→ [Adaptation Agent] → Learn & Update Strategies
    │       ↓
    │   Updated Patterns
    │       ↓
    ├─→ [Human Interface] → If Needed for Escalation
    │       ↓
    │   User Feedback
    │       ↓
    └─→ [Reasoning Agent] → For Complex Problems
            ↓
        Solution & Reasoning
            ↓
[Memory] → Store Learnings for Future
    ↓
Final Result + Learned Patterns
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **Git** (for version control operations)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd intelligent-task-automation-agent-main
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API configuration:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
```

**Get your API key from**: [Google AI Studio](https://aistudio.google.com/app/apikey)

### Step 5: Run the Application

```bash
streamlit run frontend/streamlit_app.py
```

The application will start and open in your browser at `http://localhost:8501`

---

## 📋 Project Structure

```
intelligent-task-automation-agent/
│
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py              # Base class for all agents
│   │   ├── goal_decomposer.py         # Breaks down goals into tasks
│   │   ├── planner_agent.py           # Creates execution plans
│   │   ├── executor_agent.py          # Executes tasks
│   │   ├── adaptation_agent.py        # Learns from outcomes
│   │   ├── human_interface_agent.py   # Manages human escalation
│   │   └── reasoning_agent.py         # Chain-of-thought reasoning
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py            # Coordinates all agents
│   │   ├── memory_manager.py          # Manages learned patterns
│   │   ├── progress_tracker.py        # Tracks execution progress
│   │   └── tool_registry.py           # Registry of available tools
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── command_executor.py        # Execute shell commands
│   │   ├── file_operations.py         # File/directory operations
│   │   ├── git_operations.py          # Git repository operations
│   │   └── web_operations.py          # Web requests & downloads
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── gemini_client.py           # Gemini API client
│   │
│   ├── models.py                      # Pydantic data models
│   └── __init__.py
│
├── frontend/
│   ├── streamlit_app.py               # Main Streamlit UI
│   └── components/
│       └── __init__.py
│
├── data/
│   ├── memory/                        # Stored learned patterns
│   └── sessions/                      # Saved execution sessions
│
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore
├── LICENSE
├── README.md                          # Quick start guide
├── ARCHITECTURE.md                    # Detailed architecture docs
├── CONTRIBUTING.md                    # Contributing guidelines
└── QUICKSTART.md                      # Quick start examples
```

---

## 🎮 Usage Guide

### Basic Usage

1. **Open the Application**
   ```
   http://localhost:8501
   ```

2. **Enter a Goal**
   Navigate to "Execute Goal" and describe what you want to accomplish in natural language.

3. **Monitor Progress**
   Watch the agent break down your goal, create a plan, and execute tasks in real-time.

4. **Provide Human Input** (if needed)
   Some tasks may require your confirmation before proceeding.

5. **Review Results**
   View execution history, learned patterns, and adaptation strategies.

### Example Goals

#### Simple File Operations
```
"Create a new Python file called hello.py with a simple hello world function"
"Create a directory structure: src/, tests/, docs/"
```

#### Git Operations
```
"Initialize a git repository and create an initial commit"
"Create a new branch called 'feature/new-feature'"
```

#### Project Setup
```
"Set up a new Python project with a requirements.txt file"
"Create a basic web project structure with HTML, CSS, and JavaScript files"
```

#### Complex Goals
```
"Set up a new Python project with FastAPI, create a git repository, and add a comprehensive README"
"Create a data analysis project structure with notebooks, data folder, and requirements file"
```

---

## 🧠 How It Works

### Step 1: Goal Decomposition
- Agent analyzes the goal description
- Identifies sub-goals and dependencies
- Creates a hierarchical task breakdown
- Assigns priorities and tools for each task

### Step 2: Planning
- Agent receives the task breakdown
- Orders tasks respecting dependencies
- Identifies tasks that can run in parallel
- Optimizes for efficiency and resource usage
- Creates estimated timeline

### Step 3: Execution
- Orchestrator manages task execution
- Executor runs each task using appropriate tools
- Tracks progress and handles errors
- Retries failed tasks (up to 3 times by default)
- Asks for human confirmation on sensitive operations

### Step 4: Adaptation
- Analyzes execution outcomes
- Identifies successful patterns
- Updates strategies based on results
- Stores learned patterns in memory
- Provides recommendations for improvements

### Step 5: Learning
- System remembers what worked
- Future goals benefit from past experience
- Confidence scores increase with repeated success
- Patterns are ranked by effectiveness

---

## 🛠️ Tools Available

### File Operations
- Create files and directories
- Read file contents
- List directory contents
- Delete files and directories
- Update file permissions

### Git Operations
- Initialize repositories
- Create and switch branches
- Make commits with messages
- Push/pull changes
- View status and logs

### Command Executor
- Execute system commands
- Run Python/pip commands
- Create virtual environments
- Install packages
- Run tests

### Web Operations
- Download files from URLs
- Make HTTP requests
- Parse HTML/JSON responses
- Extract data from web pages

---

## 🔧 Configuration

### Environment Variables

```env
# Gemini API
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite

# Optional: Custom settings
# BASE_PATH=/path/to/work/directory
# MAX_RETRIES=3
# TIMEOUT=30
```

### Model Selection

**Available Gemini Models:**
- `gemini-2.5-flash-lite` (Recommended) - Fast, efficient, lower quota usage
- `gemini-2.0-flash` - More capable, higher quota requirements
- `gemini-pro` - Full capabilities, experimental

---

## 📊 UI Features

### Execute Goal Page
- Enter goals in natural language
- Add optional context
- Monitor real-time execution
- Provide human input when requested

### View Progress Page
- Completion percentage
- Task status breakdown (completed, failed, in progress, pending)
- Individual task details
- Error messages and diagnostics

### Session History Page
- View past goal executions
- Review execution timelines
- See adaptations and improvements
- Filter by date or outcome

### Learned Patterns Page
- Explore discovered patterns
- View confidence scores
- See usage statistics
- Filter by pattern type

---

## 🐛 Troubleshooting

### "GEMINI_API_KEY is not set"
**Solution**: Make sure your `.env` file has the correct API key and it's in the project root directory.

### "Module not found" errors
**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt
```

### Streamlit not starting
**Solution**: Make sure you're in the correct directory and using the activated virtual environment:
```bash
cd intelligent-task-automation-agent-main
venv\Scripts\activate  # Windows
python -m streamlit run frontend/streamlit_app.py
```

### Tasks failing repeatedly
**Check**:
- File paths are correct
- Sufficient disk space available
- Git is installed (for git operations)
- Network connection (for web operations)
- API rate limits not exceeded

---

## 📈 Performance Tips

1. **Start Simple**: Begin with straightforward goals before complex ones
2. **Review Learned Patterns**: Check what patterns were learned for optimization
3. **Monitor Progress**: Use real-time progress tracking to identify bottlenecks
4. **Parallel Execution**: The agent automatically identifies parallelizable tasks
5. **Human Approval**: Review adaptive strategies to understand decision-making

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas for contribution:
- New tool implementations
- Performance improvements
- Bug fixes
- Documentation improvements
- Additional reasoning strategies

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Resources

- **Architecture Details**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Quick Start Examples**: See [QUICKSTART.md](QUICKSTART.md)
- **Gemini API Docs**: https://ai.google.dev/
- **Streamlit Docs**: https://docs.streamlit.io/
- **LangChain Docs**: https://python.langchain.com/

---

## 📧 Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing issues and solutions
3. Create a new issue with detailed information

---

## 🌟 Key Concepts

### Chain-of-Thought Reasoning
The system breaks down complex problems into step-by-step reasoning, showing its thought process.

### Learned Patterns
The system stores successful execution patterns and reuses them to improve future performance.

### Human-in-the-Loop
Critical decisions and destructive operations require human confirmation.

### Adaptive Learning
Strategies are continuously improved based on execution outcomes.

### Tool Composition
Complex tasks are achieved by composing multiple tools intelligently.

---

## 🎓 Learning Path

1. **Start**: Run simple goals to understand the system
2. **Explore**: Try more complex goals with dependencies
3. **Monitor**: Watch the learning patterns emerge
4. **Optimize**: Adjust settings based on performance
5. **Extend**: Add custom tools if needed

---

## 📞 Quick Links

- 🚀 [Quick Start](QUICKSTART.md)
- 🏗️ [Architecture](ARCHITECTURE.md)
- 📖 [Contributing](CONTRIBUTING.md)
- 📜 [License](LICENSE)

---

**Happy automating!** 🤖✨
