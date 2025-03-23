# D&D Assistant

## Overview
The D&D Assistant is a Dungeon Master Assistant built using Dash and Ollama. It provides tools for managing Dungeons & Dragons (D&D) gameplay, including dice rolling, effect tracking, and a chat interface for assistance. While originally intended for DM use this tool can provide assistance to all.

This application features a persistent notepad that retains information between restarts. The SYSTEM_PROMPT has been fine-tuned to ensure responses are strictly related to D&D. It also utilizes previous assistant interactions and notepad content to enhance the context for assistance.

The underlying assistant uses Ollama, allowing for the use of various models, with `gemma3:4b` being the current choice for fast and impressive responses.

## Features
- **Dice Rolling**: Roll various types of dice (d4, d6, d8, d10, d12, d20).
- **Effect Tracking**: Add and manage active effects for characters.
- **Notepad**: A persistent notepad that serves as context for the DM Assistant.
- **Chat Interface**: Interact with the AI for D&D-related queries and assistance.

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute:
```bash
python main_dash.py
```
Then, open your web browser and navigate to `http://127.0.0.1:8050` to access the D&D Assistant.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bugs.

## License
This project is licensed under the MIT License.