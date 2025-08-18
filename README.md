
# Anime Akinator AI  

An Akinator-style AI that guesses an anime character through a series of yes/no questions.  
This project is built as a Multi-Modal Communication Protocol (MCP) server, designed to be integrated with Puch AI.

---

## Features  

- **Decision Tree Logic**:  
  Uses scikit-learn to train a `DecisionTreeClassifier` on an anime character dataset for intelligent and efficient guessing.  

- **Conversational Interface**:  
  Game logic is exposed as a set of MCP tools that can be consumed by conversational AI agents.  

- **State Management**:  
  A Pydantic model manages the game’s state, including remaining characters, questions asked, and current tree position.  

- **Easy Deployment**:  
  Built with FastMCP, allowing quick deployment and public exposure using ngrok.  

---

## Project Structure  

```

.
├── anime.csv                # Dataset of anime characters
├── anime\_akinator\_tools.py  # Core game logic (data, model, MCP tools)
├── mcp\_server.py            # Main MCP server script
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (not committed)

````

---

## Installation & Setup  

### 1. Clone the Repository  
```bash
git clone [your-repository-url]
cd [your-repository-name]
````

### 2. Install Dependencies

It’s recommended to use a virtual environment.

```bash
pip install -r requirements.txt
```

### 3. Prepare Environment Variables

Create a `.env` file in the project root with the following values:

```env
MY_WHATSAPP_NUMBER=your_whatsapp_number
TOKEN=your_security_token
MCP_PORT=8000
NGROK_AUTH_TOKEN=your_ngrok_auth_token
```

* `MY_WHATSAPP_NUMBER`: Your WhatsApp number for validation
* `TOKEN`: A security token (optional, but recommended)
* `MCP_PORT`: Port the server will run on
* `NGROK_AUTH_TOKEN`: Authentication token from your [ngrok dashboard](https://dashboard.ngrok.com)

### 4. Start the Server

```bash
python mcp_server.py
```

Follow the on-screen instructions to start ngrok and paste the forwarding URL.
Your server will then be accessible via the provided URL.

---

## How It Works

The game flow is powered by three main MCP tools:

* **`start_game_tool`**
  Begins a new game by loading `anime.csv`, training the decision tree, and returning the first question.

* **`answer_question_tool`**
  Handles user responses (`yes`, `no`, `don’t know`) and uses the tree to select the next question or make a guess.
  Also manages confirmation or denial of guesses.

* **`quit_game_tool`**
  Ends the current game session and resets the state.

---

## Contributing

Pull requests are welcome.
For major changes, please open an issue first to discuss your ideas.

---

## License

This project is open-source under the MIT License.

