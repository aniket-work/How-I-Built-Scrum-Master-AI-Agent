# Scrum Master AI Agent

An AI-powered system that automates the collection, analysis, and reporting functions of a Scrum Master.

## Overview

Scrum Master AI Agent leverages the CrewAI framework and Large Language Models to gather data from Trello boards, analyze sprint progress, identify bottlenecks, and generate comprehensive sprint reports. It helps agile teams improve their processes by providing insights and recommendations based on their project data.

## Features

- **Automated Data Collection**: Fetches all relevant data from Trello boards including cards, comments, attachments, and member assignments
- **Comprehensive Sprint Analysis**: Identifies blockers, delays, and areas needing attention
- **Team Performance Evaluation**: Analyzes workload distribution, completion rates, and individual contributions
- **Process Bottleneck Detection**: Highlights areas where the sprint process may be breaking down
- **Professional Report Generation**: Creates detailed, well-formatted sprint reports suitable for team members and executives
- **Action Item Recommendations**: Suggests concrete steps to address identified issues

## Project Structure

```
scrum-master-ai/
├── config/                # Configuration files
├── src/                   # Source code
│   ├── agents/            # Agent definitions
│   ├── tasks/             # Task definitions
│   ├── tools/             # Tool implementations
│   ├── utils/             # Utility functions
│   ├── models/            # Data models
│   └── crew/              # Crew definitions
├── templates/             # Report templates
├── tests/                 # Unit tests
├── scripts/               # Helper scripts
├── docs/                  # Documentation
├── main.py                # Main entry point
└── requirements.txt       # Project dependencies
```

## Prerequisites

- Python 3.9+
- Trello API credentials
- OpenAI API key or other LLM provider credentials

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/scrum-master-ai.git
   cd scrum-master-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

## Configuration

Before running the Scrum Master AI, you need to configure:

1. Trello API credentials in the `.env` file:
   ```
   TRELLO_API_KEY=your_trello_api_key
   TRELLO_API_TOKEN=your_trello_api_token
   TRELLO_BOARD_ID=your_trello_board_id
   ```

2. LLM configuration in `config/settings.yaml`

## Usage

### Basic Usage

Run the Scrum Master AI to generate a sprint report:

```bash
python main.py run
```

This will:
1. Fetch all data from your configured Trello board
2. Analyze the sprint progress, blockers, and team performance
3. Generate a comprehensive sprint report

### Advanced Usage

```bash
# Run with a specific output file
python main.py run --output my_sprint_report.md

# Train the AI with multiple iterations
python main.py train --iterations 5 --output training_results.json

# Replay execution from a specific task
python main.py replay data_analysis_task

# Test with a specific model
python main.py test --iterations 2 --model gpt-4
```

## Customization

You can customize the behavior of the Scrum Master AI by modifying the configuration files:

- `config/agents.yaml`: Agent roles, goals, and personalities
- `config/tasks.yaml`: Task descriptions and expected outputs
- `config/settings.yaml`: Global application settings
- `templates/report_template.md`: Report format and structure

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License
~~~~
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [CrewAI](https://github.com/joaomdmoura/crewAI) for the agent orchestration framework
- Trello for the project management API
- OpenAI for the language model capabilities

