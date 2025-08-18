import os
import sys
from dotenv import load_dotenv
from pyngrok import ngrok
from anime_akinator_tools import mcp

# Load environment variables from a .env file
load_dotenv()

def start_mcp_server():
    """
    Starts the FastMCP server after prompting the user for the ngrok URL.
    This method is more robust as it bypasses ngrok's session limits.
    """
    print("Step 1: Starting server setup...")

    # Set ngrok auth token if available (ngrok command line still needs this)
    ngrok_auth_token = os.environ.get("NGROK_AUTH_TOKEN")
    if ngrok_auth_token:
        try:
            print("DEBUG: Attempting to set ngrok auth token.")
            ngrok.set_auth_token(ngrok_auth_token)
            print("Step 1.1: Ngrok auth token set successfully.")
        except Exception as e:
            print(f"Warning: Failed to set ngrok auth token: {e}")
    else:
        print("DEBUG: No NGROK_AUTH_TOKEN found in .env. Ngrok may not start without it.")
    
    PORT = int(os.environ.get("MCP_PORT", 8000))
    print(f"DEBUG: Server port is set to {PORT}")

    try:
        # Prompt user to start ngrok manually and provide the URL.
        print("\n=======================================================")
        print("ACTION REQUIRED:")
        print("Please open a separate terminal and run the following command:")
        print(f"  ngrok http {PORT}")
        print("Copy the 'Forwarding' URL from the ngrok terminal.")
        print("=======================================================")
        
        # The script now waits for you to manually input the URL.
        public_url = input("Paste your ngrok public URL here (e.g., https://abcde.ngrok.io): ")
        
        if not public_url.startswith("https://"):
            print("ERROR: The URL must start with 'https://'. Please try again.")
            sys.exit(1)
            
        print(f"Using provided URL for MCP server: {public_url}")
        
        # NOTE: The FastMCP library has its own .run() method.
        print("Step 2: Starting the FastMCP server...")
        # The mcp.run() function handles starting the server on the specified port.
        # It does not need the public URL to function.
        mcp.run(transport="http", port=PORT)

    except Exception as e:
        print(f"Step 3: An error occurred. Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_mcp_server()
