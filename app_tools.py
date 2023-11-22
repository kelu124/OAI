default_tools = [
    {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        },
    {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    }
                },
                "required": ["location", "format", "num_days"]
            },
        }

]



default_messages = [{'role': 'system',
  'content': "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.\nDon't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
 {'role': 'user', 'content': "What's the weather like today in Dublin"},
 {'role': 'assistant',
  'content': None,
  'function_call': {'name': 'get_current_weather',
   'arguments': {"location":"Dublin","format":"celsius"}}},
 {'role': 'user', 'content': 'The city is Dublin'}]