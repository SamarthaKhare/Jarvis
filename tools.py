
functions = [
    {
        "name": "check_messages",
        "description": "Retrieve a list of unread messages from the user's Telegram account, including sender details and message content. This helps users stay updated with pending communications.",
    },
    {
        "name": "send_message",
        "description": "Send a text message to a specified recipient via Telegram. The function requires a message string as input and delivers it through the Telegram API.",
        "parameters": {
            "message": {
                    "type": 'string'/'pdf',
                    "description": "The text message that should be sent to the recipient."
                },
            "required": ["message"]
        }
    },
    {
        "name": "get_calendar_events",
        "description": "Retrieve a list of upcoming events from the user's Google Calendar. The function fetches event details, including the event name, start time, end time, and location, helping users keep track of their schedule.",
    },
    {
        "name": "block_time",
        "description": "Reserve a specific time slot in Google Calendar by creating an event. This function requires a start time and an end time in ISO 8601 format to block availability for meetings or tasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_time": {
                    "type": "string",
                    "format": "formated according to RFC3339",
                    "description": "Start time of the event in ISO 8601 format (e.g., '2025-03-11T09:00:00Z')."
                },
                "end_time": {
                    "type": "string",
                    "format": "formated according to RFC3339",
                    "description": "End time of the event in ISO 8601 format (e.g., '2025-03-11T10:00:00Z')."
                },
                "message":{
                    "type":"string",
                    "description":"Event text that you want to show on calender"
                }
            },
            "required": ["start_time", "end_time"]
        }
    },
    {
        "name": "search_web",
        "description": "Perform a real-time Google search to fetch the latest and most relevant information for a given query. The function returns top search results, including website links, descriptions, and other useful details.",
        "parameters": {
            "query": {
                "type": "string",
                "description": "The search term or question to look up on Google."
            },
            "required": ["query"]
        }
    }
]