An Akinator-style AI that guesses an anime character through a series of yes/no questions. This project is built as a Multi-Modal Communication Protocol (MCP) server, designed to be integrated with Puch AI a whatsapp AI agent.

Features
Decision Tree Logic: Uses scikit-learn to train a Decision Tree on an anime character dataset, providing an intelligent and efficient guessing mechanism.

Conversational Interface: The game's logic is exposed as a set of tools that can be consumed by conversational AI agents.

State Management: A Pydantic model manages the game's state, including the remaining characters, questions asked, and the current position in the decision tree.

Easy Deployment: The FastMCP framework simplifies the process of creating and running a server, which can be exposed publicly using ngrok.

Project Structure
anime.csv: The dataset of anime characters used for training the model.

anime_akinator_tools.py: Contains the core game logic, including the data loading, model training, and the MCP tools.

mcp_server.py: The main script for running the MCP server locally.

requirements.txt: Lists all the necessary Python dependencies.

Installation and Setup
Clone the repository:

git clone [your-repository-url]
cd [your-repository-name]

Install dependencies:
It is recommended to use a virtual environment.

pip install -r requirements.txt

Prepare your environment variables:
Create a .env file in the project root with the following variables. These are used by anime_akinator_tools.py and mcp_server.py.

MY_WHATSAPP_NUMBER=your_whatsapp_number
TOKEN=your_security_token
MCP_PORT=8000
NGROK_AUTH_TOKEN=your_ngrok_auth_token

MY_WHATSAPP_NUMBER: Your WhatsApp number for validation.

TOKEN: A security token (optional, but good practice).

MCP_PORT: The port the server will run on.

NGROK_AUTH_TOKEN: Your ngrok authentication token. You can find this on your ngrok dashboard.

Start the server:
Run the mcp_server.py script. It will prompt you to start ngrok manually and paste the forwarding URL.

python mcp_server.py

Follow the on-screen instructions to get the ngrok URL. The server will then start and be accessible at that URL.

How It Works
The game's flow is managed through three main tools:

start_game_tool: Called to begin a new game. It loads the anime.csv dataset, trains a new DecisionTreeClassifier, and returns the first question to the user.

answer_question_tool: Processes the user's response (yes, no, or don't know). It uses the decision tree to determine the next question or makes a guess if the possibilities are narrowed down. It also handles the logic for a user confirming or denying a guess.

quit_game_tool: Ends the current game session, resetting the game state.

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
