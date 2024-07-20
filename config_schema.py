CONFIG_SCHEMA = {
    "type": str,
    "mode": str,
    "WINDOW_TITLE": str,
    "DELAY_BETWEEN_KEYS": float,
    "DELAY_BETWEEN_COMMANDS": float,
    "DELAY_BETWEEN_APPLICATIONS": float,
    "APP_LOAD_TIME": float,
    "CHUNK_SIZE": int,
    "DELAY_BETWEEN_CHUNKS": float,
    "launch_command": str,
    "window_match": str,
    "open_steps": list,
    "no_payload": bool
}

# Define the schema for open steps
OPEN_STEP_SCHEMA = {
    "action": str,
    "value": str  # The 'value' can be any type, but we'll store it as a string and convert when needed
}