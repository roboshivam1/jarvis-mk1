import ollama
from memory import ConversationMemory
from tools.system_tools import AVAILABLE_TOOLS as system_tools
from tools.web_tools import WEB_TOOLS as web_tools
from tools.vision_tools import VISION_TOOLS as vision_tools

MASTER_TOOLS = {**system_tools, **web_tools, **vision_tools}

class JarvisBrain:
    def __init__(self, model_name: str = "llama3.2"):
        """
        Initializes the brain with the specific Ollama model and tools.
        """
        self.model_name = model_name
        self.tools_list = list(MASTER_TOOLS.values())
    
    def think(self, user_text: str, memory: ConversationMemory):
        """
        Takes user text, updates memory, handles tool calls, and YIELDS 
        the response sentence-by-sentence for real-time text-to-speech.
        """
        # 1. Add user message to memory
        memory.add_message("user", user_text)
        
        # 2. Ask Ollama with tools ability AND stream=True
        stream = ollama.chat(
            model=self.model_name,
            messages=memory.get_context(),
            tools=self.tools_list,
            stream=True
        )
        
        buffer = ""
        full_reply = ""
        terminators = ['.', '?', '!', '\n']
        tool_calls_buffer = []
        
        # 3. Read the live stream chunk by chunk
        for chunk in stream:
            message = chunk.get('message', {})
            
            # INTERCEPTION: Did Ollama decide to use a tool?
            # If so, it passes a tool_calls list instead of content.
            if 'tool_calls' in message and message['tool_calls']:
                tool_calls_buffer.extend(message['tool_calls'])
                continue # Skip speaking, we are executing a tool
                
            # Otherwise, it is normal text. Let's process the audio queue.
            token = message.get('content', '')
            if not token:
                continue
                
            buffer += token
            full_reply += token # We keep the full reply to save to memory later
            
            # If the chunk completes a sentence, yield it to the mouth
            if any(t in token for t in terminators):
                if buffer.strip():
                    yield buffer.strip()
                buffer = ""
                
        # 4. TOOL EXECUTION LOOP
        # If the tool_calls_buffer caught something, we execute them now
        if tool_calls_buffer:
            print("\n[System] JARVIS is executing system tools...")
            
            # Append Ollama's tool request to history
            memory.history.append({
                'role': 'assistant',
                'content': '',
                'tool_calls': tool_calls_buffer
            })
            
            for tool_call in tool_calls_buffer:
                func_name = tool_call['function']['name']
                arguments = tool_call['function']['arguments']
                
                print(f" -> Running: {func_name}{arguments}")
                
                if func_name in MASTER_TOOLS:
                    try:
                        result = MASTER_TOOLS[func_name](**arguments)
                    except Exception as e:
                        result = f"Error executing tool: {e}"
                else:
                    result = f"Tool {func_name} not found."
                    
                # Append tool result to memory
                memory.history.append({
                    'role': 'tool',
                    'content': str(result)
                })
            
            # 5. FEEDBACK LOOP: Second stream
            # Now JARVIS reads the tool results and streams the natural reply
            final_stream = ollama.chat(
                model=self.model_name,
                messages=memory.get_context(),
                stream=True
            )
            
            for chunk in final_stream:
                token = chunk.get('message', {}).get('content', '')
                if not token:
                    continue
                    
                buffer += token
                full_reply += token
                
                if any(t in token for t in terminators):
                    if buffer.strip():
                        yield buffer.strip()
                    buffer = ""
        
        # 6. Yield any leftover text that didn't end in punctuation
        if buffer.strip():
            yield buffer.strip()
            
        # 7. Finally, save the completely assembled spoken reply to memory
        if full_reply.strip():
            memory.add_message("assistant", full_reply.strip())