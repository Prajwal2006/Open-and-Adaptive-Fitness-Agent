OPENCLAW_TOOL_SCHEMAS = [
    {
        "name": "get_today_workout",
        "description": "Get current planned workout split for today.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_training_state",
        "description": "Get current readiness, fatigue, and consistency state.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_notifications",
        "description": "Get unread notifications for the user.",
        "input_schema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 50}},
        },
    },
    {
        "name": "generate_workout_plan",
        "description": "Generate proactive plan recommendations.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_recovery_recommendation",
        "description": "Get recovery recommendation based on recent load.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "log_workout",
        "description": "Log completed workout.",
        "input_schema": {
            "type": "object",
            "properties": {
                "split_type": {"type": "string"},
                "duration_minutes": {"type": "integer"},
                "notes": {"type": "string"},
            },
            "required": ["split_type"],
        },
    },
    {
        "name": "log_habit",
        "description": "Log a behavior or habit event for fitness context.",
        "input_schema": {
            "type": "object",
            "properties": {
                "habit_name": {"type": "string"},
                "completed": {"type": "boolean"},
                "notes": {"type": "string"},
            },
            "required": ["habit_name", "completed"],
        },
    },
]
