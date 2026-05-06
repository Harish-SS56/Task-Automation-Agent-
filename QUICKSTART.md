# Quick Start Guide

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up your API key:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=sk-your-key-here
```

## Running the Application

Start the Streamlit UI:
```bash
streamlit run frontend/streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

## Your First Goal

Try entering a simple goal like:

**"Create a new directory called 'my_project' and add a README.md file with a basic project description"**

The system will:
1. Break down the goal into tasks
2. Create an execution plan
3. Execute the tasks
4. Learn from the execution
5. Show you the results

## Example Goals to Try

### Simple File Operations
- "Create a new Python file called hello.py with a simple hello world function"
- "Create a directory structure: src/, tests/, docs/"

### Git Operations
- "Initialize a git repository and create an initial commit"
- "Create a new branch called 'feature/new-feature'"

### Project Setup
- "Set up a new Python project with a requirements.txt file"
- "Create a basic web project structure with HTML, CSS, and JavaScript files"

### Complex Goals
- "Set up a new Python project with FastAPI, create a git repository, and add a comprehensive README"
- "Create a data analysis project structure with notebooks, data folder, and requirements file"

## Understanding the UI

### Execute Goal Page
- Enter your goal in natural language
- Add optional context if needed
- Click "Execute Goal" to start
- Monitor progress in real-time
- Provide human input when requested

### View Progress Page
- See completion percentage
- View task status (completed, failed, in progress, pending)
- Check individual task details

### Session History Page
- View past goal executions
- Review execution results
- See adaptations and learnings

### Learned Patterns Page
- Explore patterns the system has learned
- Filter by pattern type
- See confidence scores and usage counts

## How It Works

1. **Goal Decomposition**: The system breaks your goal into specific, actionable tasks
2. **Planning**: Creates an optimal execution plan considering dependencies
3. **Execution**: Runs tasks using appropriate tools (file operations, git, commands, web)
4. **Adaptation**: Learns from outcomes and improves future execution
5. **Human Escalation**: Asks for your input when needed (destructive operations, ambiguous requirements)

## Tips

- Be specific in your goal descriptions for better results
- The system learns over time - try similar goals to see improvement
- Check the "Learned Patterns" page to see what the system has learned
- The system will ask for confirmation before destructive operations

## Troubleshooting

**Error: "GEMINI_API_KEY environment variable is required"**
- Make sure you've created a `.env` file with your API key
- Restart the Streamlit app after creating the `.env` file

**Tasks are failing:**
- Check that the goal description is clear and actionable
- Review the error messages in the task details
- Try breaking down complex goals into simpler ones

**Human input requests:**
- The system will ask for confirmation before destructive operations
- Provide clear responses to help the system proceed

## Next Steps

- Try more complex goals to see the system adapt
- Review learned patterns to understand how the system improves
- Check the ARCHITECTURE.md for detailed system design
- Explore the code to understand how each agent works


