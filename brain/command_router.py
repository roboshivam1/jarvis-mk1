from brain.web_intent import get_web_command, parse_ai_command

def detect_command(text):
    text = text.lower()
    text.replace('launch', 'open')

    #APP COMMANDS
    if "open chrome" in text or "open google chrome" in text:
        return ("open_app", "Google Chrome")
    
    if "open vscode" in text or "open code" in text:
        return ("open_app", "Visual Studio Code")
    
    else:
        #WEB COMMANDS:
        ai_response = get_web_command(text)
        parsed = parse_ai_command(ai_response)

        if parsed:
            return (parsed["action"], parsed["value"])
    
        return None
    
    