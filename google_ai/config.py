"""
Shared configuration settings for Google AI services.
"""

# Default model names
DEFAULT_MODEL = "gemini-1.5-pro-latest"
#DEFAULT_MODEL = "gemini-1.5-flash"

DEFAULT_PRO_MODEL = "gemini-1.5-pro-latest"

# Generation configuration
GENERATION_CONFIG = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# Safety settings
SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]
