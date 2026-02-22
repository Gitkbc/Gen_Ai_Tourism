# travel_ai/config.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists.
# This is useful for local development.
load_dotenv()

# ==========================================================
# API and Model Configuration
# ==========================================================

# The API key for the OpenRouter service. It is loaded from an environment
# variable for security.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# The base URL for the OpenRouter API.
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# The specific language model to be used for generating content.
# Example: "meta-llama/llama-3-70b-instruct", "google/gemini-pro"
MODEL_NAME = "meta-llama/llama-3-70b-instruct"

# Controls the randomness of the model's output. Higher values (e.g., 0.8)
# make the output more creative, while lower values (e.g., 0.2) make it
# more deterministic.
TEMPERATURE = 0.7

# The maximum time in seconds to wait for a response from the API.
REQUEST_TIMEOUT = 60


# ==========================================================
# Application Settings
# ==========================================================

# The logging level for the application. Can be "INFO", "DEBUG", "WARNING",
# "ERROR", "CRITICAL".
LOGGING_LEVEL = "INFO"


# ==========================================================
# Environment Validation
# ==========================================================

# Ensure that the required API key is set. If not, raise an error
# with a helpful message to guide the user.
if not OPENROUTER_API_KEY:
    raise ValueError(
        "The OPENROUTER_API_KEY environment variable is not set. "
        "Please create a .env file in the 'travel_ai' directory and add the key, "
        "or set the environment variable directly."
    )