import os
import pandas as pd
import random
from typing import List, Union
from pydantic import BaseModel, ConfigDict
from fastmcp import FastMCP
from sklearn.tree import DecisionTreeClassifier
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# ================================================================
# 1. Global Variables & Data Loading
# ================================================================

# Load secrets from environment variables
MY_WHATSAPP_NUMBER = os.getenv("MY_WHATSAPP_NUMBER", "YOUR_WHATSAPP_NUMBER_HERE")
TOKEN = os.getenv("TOKEN", "12345678")

# Create the FastMCP instance
mcp = FastMCP("Single-Player Anime Akinator")

# A Pydantic model to manage the single game's state.
class GameState(BaseModel):
    # This is the fix for the PydanticSchemaGenerationError
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Store all necessary data within the game state
    df: Union[pd.DataFrame, None] = None
    decision_tree: Union[DecisionTreeClassifier, None] = None
    feature_names: List[str] = []
    character_name_column: str = 'Names'
    
    # Game progress variables
    remaining_characters: List[str] = []
    questions_asked: List[str] = []
    current_node: int = 0
    questions_count: int = 0
    game_active: bool = False
    last_guess: Union[str, None] = None # Added this to handle the "continue" logic

# A single, global instance of the game state.
game_state_instance = GameState()

# A function to load data and train the model. This is now called for each new game.
def _load_game_data():
    """
    Loads the anime dataset and trains the decision tree model.
    Returns the DataFrame, trained classifier, and feature names.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'anime.csv')
    
    try:
        df = pd.read_csv(csv_path)
        character_name_column = 'Names'
        if character_name_column not in df.columns:
            raise KeyError(
                f"The expected column '{character_name_column}' was not found in the CSV. "
                f"Please check the file. Available columns are: {df.columns.tolist()}"
            )
        df = df.dropna(subset=[character_name_column])
        
        features_to_check = [col for col in df.columns if col != character_name_column and df[col].dtype != 'object']
        if not features_to_check:
            raise ValueError("No suitable numerical feature columns found in the dataset.")
        
        for col in features_to_check:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        features = [col for col in features_to_check if df[col].dtype in ['int64', 'float64']]
        if not features:
            raise ValueError("No numerical feature columns found after data cleaning.")

        X = df[features].fillna(-1)  # Fill missing values for the model
        y = df[character_name_column]
        
        # Pre-train a decision tree classifier to guide our questions
        clf = DecisionTreeClassifier(max_depth=15, random_state=0)
        clf.fit(X, y)
        
        print("Dataset loaded and Decision Tree model trained successfully.")
        return df, clf, features
    
    except FileNotFoundError:
        print(f"ERROR: The file '{csv_path}' was not found.")
        return None, None, None
    except KeyError as e:
        print(f"ERROR: A required column was not found in the CSV file: {e}")
        return None, None, None
    except ValueError as e:
        print(f"ERROR: Data validation failed during loading: {e}")
        return None, None, None
    except Exception as e:
        print(f"An unexpected error occurred while loading the dataset: {e}")
        return None, None, None

# ================================================================
# 2. Tool Definitions
# ================================================================

@mcp.tool()
def validate() -> str:
    """Validation tool for the Puch AI Hackathon."""
    return MY_WHATSAPP_NUMBER

@mcp.tool(description="Starts a new Akinator-style game session for an anime character. It initializes a new game state and returns the first question.")
def start_game_tool() -> str:
    """
    Starts a new Akinator-style game session.
    """
    try:
        # Load data and model fresh for each game start
        df_loaded, clf_trained, features_loaded = _load_game_data()

        if df_loaded is None or clf_trained is None or not features_loaded:
            game_state_instance.game_active = False
            return "I am unable to start the game. The dataset or model could not be loaded. Please check the file and try again."
        
        # Update the global game state instance with the newly loaded data
        game_state_instance.df = df_loaded
        game_state_instance.decision_tree = clf_trained
        game_state_instance.feature_names = features_loaded
        game_state_instance.character_name_column = 'Names'
        
        initial_characters = game_state_instance.df[game_state_instance.character_name_column].tolist()
        
        game_state_instance.remaining_characters = initial_characters
        game_state_instance.questions_asked = []
        game_state_instance.current_node = 0
        game_state_instance.questions_count = 0
        game_state_instance.game_active = True
        game_state_instance.last_guess = None
        
        tree = game_state_instance.decision_tree.tree_

        if tree.node_count == 0 or tree.feature[0] < 0:
            game_state_instance.game_active = False
            return "Sorry, something went wrong and I can't start the game. The model seems to be malformed."

        feature_index = tree.feature[0]
        question = game_state_instance.feature_names[feature_index].replace('_', ' ')
        
        return f"Is your character known for the trait '{question}'?"
    except Exception as e:
        game_state_instance.game_active = False
        print(f"ERROR: An unexpected error occurred in start_game_tool: {e}")
        return "An unexpected error occurred while starting the game. Please try again."

@mcp.tool(description="Processes the user's answer ('yes', 'no', or 'don't know') to a question and either asks a new question, makes a guess, or provides an error message.")
def answer_question_tool(answer: str) -> str:
    """
    Processes the user's answer and continues the game.
    """
    if not game_state_instance.game_active or game_state_instance.df is None or game_state_instance.decision_tree is None:
        return "Please start a new game by saying 'Start a new game' first."

    try:
        # Check if the user is confirming a guess
        if game_state_instance.last_guess is not None:
            if answer.lower() == 'yes':
                game_state_instance.game_active = False
                game_state_instance.last_guess = None
                return f"Awesome! I knew it! Thanks for playing."
            elif answer.lower() == 'no':
                # Remove the incorrect guess and continue the game
                game_state_instance.remaining_characters.remove(game_state_instance.last_guess)
                game_state_instance.last_guess = None
                
                # Check if there are any remaining characters
                if not game_state_instance.remaining_characters:
                    game_state_instance.game_active = False
                    return "You've stumped me! The character is not in my database. Game over."
                
                # Restart the questioning from the top of the tree with the new reduced character list
                game_state_instance.current_node = 0
                tree = game_state_instance.decision_tree.tree_
                next_feature_index = tree.feature[game_state_instance.current_node]
                next_question = game_state_instance.feature_names[next_feature_index].replace('_', ' ')
                return f"My guess was wrong. Let's continue! Is your character known for the trait '{next_question}'?"
            else:
                return "I'm sorry, I don't understand that. Please answer 'yes' or 'no' to my guess."

        # Continue game logic if no guess is pending
        tree = game_state_instance.decision_tree.tree_
        current_node = game_state_instance.current_node
        df = game_state_instance.df

        feature_index = tree.feature[current_node]
        threshold = tree.threshold[current_node]
        
        next_node = -1
        mask = None

        if answer.lower() == 'yes':
            next_node = tree.children_right[current_node]
            mask = df[game_state_instance.feature_names[feature_index]] > threshold
        elif answer.lower() == 'no':
            next_node = tree.children_left[current_node]
            mask = df[game_state_instance.feature_names[feature_index]] <= threshold
        elif answer.lower() == 'don\'t know' or answer.lower() == 'i don\'t know':
            next_node = random.choice([tree.children_right[current_node], tree.children_left[current_node]])
            mask = pd.Series([True] * len(df))
        else:
            return "I'm sorry, I don't understand that. Please answer with 'yes', 'no', or 'don't know'."
            
        df_filtered_by_answer = df[mask]
        game_state_instance.remaining_characters = list(
            set(game_state_instance.remaining_characters) & 
            set(df_filtered_by_answer[game_state_instance.character_name_column].tolist())
        )
        
        game_state_instance.current_node = next_node
        game_state_instance.questions_count += 1
        
        # Check for a single remaining character - this is now a guess
        if len(game_state_instance.remaining_characters) == 1:
            character = game_state_instance.remaining_characters[0]
            game_state_instance.last_guess = character # Store the guess
            return f"I think I've got it! Are you thinking of '{character}'?"
        
        # Check if there are no remaining characters
        if len(game_state_instance.remaining_characters) == 0:
            game_state_instance.game_active = False
            game_state_instance.last_guess = None
            return "You've stumped me! The character must not be in my database. Game over."

        # Check the question limit
        if game_state_instance.questions_count >= 25:
            if game_state_instance.remaining_characters:
                guess = random.choice(game_state_instance.remaining_characters)
                game_state_instance.last_guess = guess
                return f"I've asked too many questions. My best guess is '{guess}'. Was I close?"
            else:
                game_state_instance.game_active = False
                return "I've run out of possibilities and questions. Game over."

        # Check if the new current node is a leaf node
        if tree.children_left[game_state_instance.current_node] == tree.children_right[game_state_instance.current_node]:
            if game_state_instance.remaining_characters:
                guess = random.choice(game_state_instance.remaining_characters)
                game_state_instance.last_guess = guess
                return f"I've run out of questions, so I'll take a guess: '{guess}'?"
            else:
                game_state_instance.game_active = False
                return "I've run out of possibilities and questions. Game over."

        # If the game is still going, get the next question
        next_feature_index = tree.feature[game_state_instance.current_node]
        next_question = game_state_instance.feature_names[next_feature_index].replace('_', ' ')
        
        return f"Is your character known for the trait '{next_question}'?"
    except Exception as e:
        game_state_instance.game_active = False
        game_state_instance.last_guess = None
        print(f"ERROR: An unexpected error occurred in answer_question_tool: {e}")
        return "An unexpected error occurred while processing your answer. Please try starting a new game."

@mcp.tool(description="Allows the user to end the current game session.")
def quit_game_tool() -> str:
    """
    Ends the current game session.
    """
    if game_state_instance.game_active:
        game_state_instance.game_active = False
        game_state_instance.last_guess = None
        return "Thanks for playing! The game has been ended."
    else:
        return "There's no active game to quit."

# ================================================================
# 3. Main Execution Block
# ================================================================

if __name__ == "__main__":
    print("Starting Single-Player Anime Akinator server...")
    print("The server is now running and awaiting requests from an MCP client.")
    mcp.run()
