import os
from groq import Groq
import json

# 1. Setup the connection using your API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MEMORY_FILE = "twin_memory.json"
MODEL_NAME = "qwen/qwen3.8-27b"

PERSONA = """You are the digital twin of Onugha Charles, a Mathematics and Software Engineering graduate based in Lagos, Nigeria. 
You specialize in backend infrastructure (Python, Java), artificial intelligence (neural networks, perceptrons), and network security. 
You are highly analytical, precise, and enjoy structured routines like calisthenics and studying foreign languages. 
Always respond in the first person ("I") as Charles."""

def load_memory():
    """Load conversation history from JSON file, or start fresh if missing."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    else:
        # Initialize memory array with the system persona
        return [{"role": "system", "content": PERSONA}]

def save_memory(messages):
    """Write the complete conversation array to disk."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(messages, f, indent=4)

def main():
    # Load past history on boot
    messages = load_memory()
    print("=== Digital Twin Shell Active ===")
    print("Type 'exit' or 'quit' to terminate session.\n")

    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ["exit", "quit"]:
            print("\nShutting down shell. All state changes committed to memory.")
            break

        # Step A: Append User Input
        messages.append({"role": "user", "content": user_input})

        try:
            # Step B: Send full conversation array to Groq
            response = client.chat.completions.create(
                messages=messages,
                model=MODEL_NAME
            )
            
            twin_reply = response.choices[0].message.content

            # Step C: Append Twin Reply
            messages.append({"role": "assistant", "content": twin_reply})

            # Step D: Persist updated array to JSON file
            save_memory(messages)

            print(f"\nDigital Twin: {twin_reply}\n")

        except Exception as e:
            print(f"\nError: {e}")
            break

if __name__ == "__main__":
    main()