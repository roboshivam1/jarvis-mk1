from typing import List, Dict

class conversationMemory:
    def __init__(self, system_prompt: str, max_turns: int = 8):
        "Initialises the memory buffer"
        self.system_message = {"role": "system", "content": system_prompt}
        self.max_turns = max_turns

        self.history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str) -> None:
        """
        Adds a new message to the memory and triggers pruning if necessary.
        """
        # Add the new message to our history list
        self.history.append({"role": role, "content": content})
        with open('full_history.txt', "a") as hist:
            hist.write(f"Role: {role}, Content: {content} \n")
        
        # Immediately check if we need to forget older messages
        self._manage_context_window()
    
    def _manage_context_window(self) -> None:
        """
        Ensures the memory doesn't exceed the max_turns.
        """
        # 1 turn = 1 user message + 1 assistant message (2 total)
        max_messages = self.max_turns * 2
        
        # If our history exceeds the limit, slice off the oldest messages
        if len(self.history) > max_messages:
            # TODO: Later we will add summarization logic right here
            
            # This keeps only the most recent 'max_messages' at the end of the list
            self.history = self.history[-max_messages:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """
        Retrieves the full formatted message list to send to Ollama.
        """
        # Combine the permanent system prompt with the recent history
        return [self.system_message] + self.history

    def clear_memory(self) -> None:
        """Wipes the short-term memory completely."""
        self.history = []