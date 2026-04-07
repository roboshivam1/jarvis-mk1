import ollama
from memory import ConversationMemory
from tools.system_tools import AVAILABLE_TOOLS as system_tools
from tools.web_tools import WEB_TOOLS as web_tools

MASTER_TOOLS = {**system_tools, **web_tools}

class JarvisBrain:
    def __init__(self, model_name: str= "llama3.1"):
        """
        Initializes the brain with the specific ollama model
        """
        self.model_name = model_name

        self.tools_list = list(MASTER_TOOLS.values())
    
    def think(self, user_text: str, memory: ConversationMemory) -> str:
        """
        Takes user text, updates memory, handles tool calls, and generates a response.
        """
        # 1. Add user message to memory
        memory.add_message("user", user_text)
        
        # 2. Ask Ollama with tools ability
        response = ollama.chat(
            model=self.model_name,
            messages=memory.get_context(),
            tools=self.tools_list
        )
        
        message = response['message']
        
        # 3. INTERCEPTION: Did Ollama decide to use a tool?
        if message.get('tool_calls'):
            print("\n[System] JARVIS is executing system tools...")
            
            # Append Ollama's tool request directly to the raw history list 
            memory.history.append(message)
            
            # 4. Loop through every tool Ollama asked to run (sometimes it asks for multiple at once)
            for tool_call in message['tool_calls']:
                func_name = tool_call['function']['name']
                arguments = tool_call['function']['arguments']
                
                print(f" -> Running: {func_name}{arguments}")
                
                # Execute the function from our dictionary
                if func_name in MASTER_TOOLS:
                    try:
                        # **arguments unpacks the JSON dictionary into Python function parameters
                        result = MASTER_TOOLS[func_name](**arguments)
                    except Exception as e:
                        result = f"Error executing tool: {e}"
                else:
                    result = f"Tool {func_name} not found."
                    
                # 5. Append the result of the tool back into memory so Ollama can read it
                memory.history.append({
                    'role': 'tool',
                    'content': str(result)
                })
            
            # 6. FEEDBACK LOOP: Ask Ollama one more time! 
            # Now it will read the tool results in the memory and generate a natural text reply.
            final_response = ollama.chat(
                model=self.model_name,
                messages=memory.get_context()
            )
            
            jarvis_reply = final_response['message']['content']
            
            # Save the final spoken reply to memory
            memory.add_message("assistant", jarvis_reply)
            return jarvis_reply

        # 7. NORMAL CONVERSATION: If no tools were needed, just return the text
        else:
            jarvis_reply = message['content']
            memory.add_message("assistant", jarvis_reply)
            return jarvis_reply