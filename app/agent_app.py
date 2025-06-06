from langchain.agents import initialize_agent, AgentType
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.tools.shell import ShellTool
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema.messages import SystemMessage
import os

# Define a simple custom tool
@tool
def get_weather(location: str) -> str:
    # Basically how this works is you provide a string that describes the tool's purpose and then program in the logic to perform the task or provide information to the LLM
    """Get the current weather in a given location"""
    # make an api call to a free weather API for the current weather
    return f"The weather in {location} is currently sunny and 22°C."

@tool
def read_application_logs(input: str) -> str:
    """Reads the container's application logs and interprets them"""
    # This is a very simple log reading function, you can obviously expand this to do more complex log parsing and analysis
    log_file_path = "/var/log/application.log"
    if not os.path.exists(log_file_path):
        return "Log file not found. Please check the path."
    try:
        with open(log_file_path, 'r') as log_file:
            logs = log_file.readlines()
        if not logs:
            return "No logs found in the application log file."
        # Here you can implement logic to parse and interpret the logs
        errors = [log for log in logs if "ERROR" in log or "Exception" in log]
        if errors:
            return f"Found {len(errors)} errors in the application logs:\n" + "\n".join(errors)
        else:
            return "No errors found in the application logs."
    except Exception as e:
        return f"An error occurred while reading the log file: {str(e)}"
    
def main():
    print("Initializing Ollama-powered Agent...")
    
    # Initialize the Ollama LLM
    llm = ChatOllama(
        model="gemma3:4b", # You can replace with any model you have in Ollama, a list of those models can be found here https://ollama.com/search
        base_url="http://192.168.1.214:11434", # Change if your Ollama is running elsewhere
        temperature=0.7,
    )
    
    # Create tools list
    shell = ShellTool(ask_human_input=True)  # Allow human input for shell commands
    search = DuckDuckGoSearchResults()
    tools = [
        get_weather,
        read_application_logs,
        search,
        shell,

    ]
    
    # Define your system message (This is the very first prompt to the AI setting the stage for its behavior over the course of the conversation)
    system_message = SystemMessage(
        content="You are an AI with control over a variety of tools, help the user by providing accurate information and executing commands when necessary. Always respond in a helpful and friendly manner."
    )
    
    # Initialize conversation memory with the system message
    memory = ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True,
    )
    
    # Initialize the agent with system_message
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        system_message=system_message  # This injects your system prompt into the agent
    )
    
    # Prime the memory with an initial exchange to set the context
    agent.memory.chat_memory.add_message(system_message)
    # agent.run("Help the user with any requests presented")

    # Clear the console for a clean start
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("Agent initialized! Type 'exit' to quit.")
    print("You can ask questions about the container, perform actions in the container, or even get information about the weather!")
    
    # Simple interaction loop
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
            
        try:
            response = agent.run(user_input)
            print(f"\nAgent: {response}")
        except Exception as e:
            print(f"\nError: {e}")
            print("Agent: I encountered an error while processing your request.")

if __name__ == "__main__":
    main()