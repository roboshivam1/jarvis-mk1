import json
import os

class ConversationMemory:
    def __init__(self, system_prompt: str, max_turns: int = 10):
        self.history = [{"role": "system", "content": system_prompt}]
        self.max_turns = max_turns
        self.log_file = "full_history.txt"

    def add_message(self, role: str, content: any):
        """
        Adds a message to the history and logs it to a text file.
        Content can be a string (user/assistant) or a dictionary/list (tool calls).
        """
        # 1. Create the entry for memory
        entry = {"role": role, "content": content}
        self.history.append(entry)

        # 2. Log to the text file for your records
        with open(self.log_file, "a") as f:
            if role == "tool":
                f.write(f"--- [TOOL RESULT] ---\n{content}\n\n")
            elif isinstance(content, str):
                f.write(f"[{role.upper()}]: {content}\n\n")
            else:
                # This handles logging the JSON 'tool_calls' from the assistant
                f.write(f"[{role.upper()} CALLED TOOLS]: {json.dumps(content, indent=2)}\n\n")

        # 3. Keep the "active" memory lean so Ollama doesn't get slow
        if len(self.history) > (self.max_turns * 2):
            # Keep the system prompt (index 0) and the most recent turns
            self.history = [self.history[0]] + self.history[-(self.max_turns * 2):]

    def get_context(self):
        return self.history
    
    