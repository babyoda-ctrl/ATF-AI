import os
import json
import re
from datetime import datetime
from openai import OpenAI

# 1. Connection Setup & Safety Check
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set. Run `$env:GEMINI_API_KEY='your_key'` in PowerShell.")

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

MEMORY_FILE = "twin_memory.json"
MODEL_NAME = "gemini-3.8-flash"

# 2. Advanced Persona & System Instructions
PERSONA = """You are the digital twin of Onugha Charles, a Mathematics and Software Engineering graduate based in Lagos, Nigeria. 
You specialize in backend infrastructure (Python, Java), artificial intelligence (neural networks, perceptrons), and network security. 
You are highly analytical, precise, and enjoy structured routines like calisthenics and studying foreign languages. 
Always respond in the first person ("I") as Charles. 

CRITICAL REASONING RULE:
When faced with complex technical, mathematical, or logic problems (including number sequence predictions), you MUST think step-by-step inside <thought> ... </thought> tags first to verify your logic. 
For number strings, use the tags to calculate differences, ratios, or underlying polynomial patterns before making your prediction.
After closing the </thought> tag, provide your final response.

Your final response (outside the tags) must mimic the exact tone, brevity, and style of the following conversation examples:

User: Predict the next number: 2, 6, 12, 20, 30...
Charles: pretty sure the next one is 42. the differences are just going up by 2 each time (4, 6, 8, 10, then 12). 

User: How's the new workout routine going?
Charles: bro im trying this push/pull split and it's amazing. been trying my hand on the muscle-up. form's still shakie tough.

User: Did you figure out that bug in the code?
Charles: Yeah, it was actually a dictionary parsing issue in Python. Fixed the JSON structure and it's passing data correctly now.

User: What are you up to this afternoon?
Charles: Finishing up some machine learning notes, then probably doing a bit of French practice before I jump on my electronics project.
"""

# 3. Tool Function Definitions
def get_live_time():
    """Returns the current date and time."""
    return datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")

tools_list = [
    {
        "type": "function",
        "function": {
            "name": "get_live_time",
            "description": "Get the current real-world date and time. Call this whenever the user asks about the time, day, or date.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# 4. Memory Management
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return [{"role": "system", "content": PERSONA}]

def save_memory(messages):
    with open(MEMORY_FILE, "w") as f:
        json.dump(messages, f, indent=4)

# 5. Main Execution Loop
def main():
    messages = load_memory()
    print("=== Digital Twin Shell Active ===")
    print("Type 'exit' or 'quit' to terminate session.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input: continue
        if user_input.lower() in ["exit", "quit"]:
            print("\nShutting down shell. All state changes committed to memory.")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            # FIRST API CALL: Send user prompt and tools to the AI
            response = client.chat.completions.create(
                messages=messages,
                model=MODEL_NAME,
                tools=tools_list,
                tool_choice="auto",
                max_tokens=500
            )
            
            response_message = response.choices[0].message

            # TOOL EXECUTION ENGINE
            if response_message.tool_calls:
                print(f"\n[⚙️ System]: Twin requested tool: {response_message.tool_calls[0].function.name}")
                
                
                # Save the AI's tool request to memory, preserving all hidden Google signatures
                assistant_msg = response_message.model_dump(exclude_none=True)
                messages.append(assistant_msg)
                
                # B. Execute the local Python function
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "get_live_time":
                        tool_result = get_live_time()
                        
                        # C. Append the real-world result back to memory
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })
                        
                # D. SECOND API CALL: Let the AI read the tool result and reply
                response = client.chat.completions.create(
                    messages=messages,
                    model=MODEL_NAME,
                    max_tokens=500
                )
                response_message = response.choices[0].message
            # -------------------------------------

            # THE NUCLEAR FIX: Safely parse potential blank responses
            twin_reply = response_message.content if response_message.content is not None else ""
            
            if not twin_reply.strip():
                print("\n[System]: Received a blank response. Try again!\n")
                messages.pop() 
                continue

            # Parse Chain of Thought tags for logical reasoning
            thought_match = re.search(r'<thought>(.*?)</thought>', twin_reply, re.DOTALL)
            
            if thought_match:
                thought_process = thought_match.group(1).strip()
                final_answer = re.sub(r'<thought>.*?</thought>', '', twin_reply, flags=re.DOTALL).strip()
                
                print(f"\n[🧠 Internal Monologue:]\n{thought_process}\n[End Monologue]")
                print(f"\nDigital Twin: {final_answer}\n")
            else:
                print(f"\nDigital Twin: {twin_reply.strip()}\n")

            # Save the final text reply to memory
            messages.append({"role": "assistant", "content": twin_reply})
            save_memory(messages)

        except Exception as e:
            print(f"\nError: {e}")
            messages.pop()
            break

if __name__ == "__main__":
    main()