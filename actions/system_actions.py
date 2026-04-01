import os

def open_app(app_name):
    os.system(f"open -a '{app_name}'")
    return f"Opening {app_name}"