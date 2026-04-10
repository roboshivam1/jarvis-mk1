import os
import json
import ollama
from memory_manager import MemoryVault

TRANSCRIPT_FILE = "pending_transcript.txt"
MODEL_NAME = "llama3.2"
LINES_PER_CHUNK = 30  

def consolidate_memory():
    """
    Reads the pending transcript, chunks it into smaller blobs, 
    and performs multiple rounds of memory extraction.
    """
    if not os.path.exists(TRANSCRIPT_FILE):
        return 

    with open(TRANSCRIPT_FILE, 'r') as file:
        lines = file.readlines()

    if not lines:
        return 
        
    # group the lines into smaller chunks
    chunks = ["".join(lines[i:i + LINES_PER_CHUNK]) for i in range(0, len(lines), LINES_PER_CHUNK)]
        
    print(f"[System] Consolidating previous session's memories ({len(chunks)} chunks). Please wait...")
    vault = MemoryVault()

    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        print(f"[System] Processing chunk {i + 1}/{len(chunks)}...")

        extraction_prompt = f"""
        You are an AI data extractor. Read this portion of a conversation transcript.
        Extract any permanent facts about the user, their preferences, or their projects.
        Keep the facts as understandable sentences, not just words, so that they can be looked up later as meaningful facts.
        Do NOT invent information. If there are no new facts in this specific chunk, return empty lists.
        
        You MUST output strictly in JSON format matching this exact structure:
        {{
            "user_profile": ["fact 1", "fact 2"],
            "preferences": ["pref 1", "pref 2"],
            "current_projects": ["project 1"],
            "general_facts": ["fact 1"]
        }}
        
        Transcript Chunk:
        {chunk}
        """

        try:
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[{'role': 'user', 'content': extraction_prompt}],
                format='json'
            )
            
            extracted_data = json.loads(response['message']['content'])
            
            # Save the extracted data directly into the vault
            for category, facts in extracted_data.items():
                for fact in facts:
                    vault.add_memory(category, fact)

        except Exception as e:
            print(f"[System Error] Failed to extract from chunk {i + 1}: {e}")
            
    # Always delete the transcript when finished so we start fresh
    if os.path.exists(TRANSCRIPT_FILE):
        os.remove(TRANSCRIPT_FILE)
    print("[System] Memory consolidation complete.")

