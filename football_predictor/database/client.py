import os

def supabase_config():
    url=os.getenv("SUPABASE_URL")
    key=os.getenv("SUPABASE_KEY")
    if not url or not key:
        return None
    return {"url":url,"key":key}
