import google.generativeai as genai
import logging
from config import GEMINI_API_KEY, GEMINI_MODEL

# Configure the generative AI model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_gemini_recommendations(financial_data, prompt_template):
    """
    Generates financial recommendations using the Gemini API.

    Args:
        financial_data (dict): A dictionary containing the user's financial data.
        prompt_template (str): The prompt template to use for the generation.

    Returns:
        str: The generated recommendations, or a graceful error message.
    """
    try:
        # Create the full prompt
        prompt = prompt_template.format(financial_data=financial_data)

        # Generate content
        response = model.generate_content(prompt)

        # Log the response for debugging (masking PII is crucial here)
        # In a real application, you would implement a robust PII masking solution.
        logger.info(f"Gemini API response: {response.text}")

        return response.text
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}", exc_info=True)
        # Depending on the context, you might want to return a more user-friendly
        # message on the UI.
        return "An error occurred while generating recommendations. Please try again later."
