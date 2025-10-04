import torch
import warnings
from transformers import pipeline, AutoTokenizer, logging

# Set transformers logging to show only errors
logging.set_verbosity_error()

# Trained on 28 different emotional expressions
#
# https://huggingface.co/joeddav/distilbert-base-uncased-go-emotions-student/tree/main
#
# | admiration | curiosity | fear | optimism |
# | amusement | desire | gratitude | pride |
# | anger | disappointment | grief | realization |
# | annoyance | disapproval | joy | relief |
# | approval | disgust | love | remorse |
# | caring | embarrassment | nervousness | sadness |
# | confusion | excitement | neutral | surprise |
#

model_id = "joeddav/distilbert-base-uncased-go-emotions-student"

# Initialize the classifier globally to avoid reloading it on every call
try:
    # Use GPU if available (device=0), otherwise CPU.
    # If you encounter issues with device=0, try device=-1 for CPU.
    device = 0 if torch.cuda.is_available() else -1
    classifier = pipeline(
        "text-classification",
        model=model_id,
        device=device,
        top_k=1
    )
except Exception as e:
    print(f"Error initializing classifier: {e}")
    classifier = None

def classify_sentiment(text_content: str) -> dict:
    """
    Classifies the sentiment of the given text content.

    Args:
        text_content: The text to analyze.

    Returns:
        A dictionary containing the classification results, or an error message if classification fails.
        Example: {"emotion": "joy", "score": 0.99}
    """
    if classifier is None:
        return {"error": "Classifier not initialized. Please check logs for details."}
    
    try:
        # Ensure text_content is a string
        if not isinstance(text_content, str):
            text_content = str(text_content)
            
        predictions = classifier(text_content)
        
        # The pipeline returns a list of lists, e.g., [[{'label': 'joy', 'score': 0.99}]]
        # We want to return a more structured format, e.g., {'emotion': 'joy', 'score': 0.99}
        if predictions and predictions[0]:
            result = {
                "emotion": predictions[0][0]['label'],
                "score": predictions[0][0]['score']
            }
            return result
        else:
            return {"error": "No predictions returned by the classifier."}
            
    except Exception as e:
        warnings.warn(f"Error during sentiment classification: {e}")
        return {"error": f"An error occurred during classification: {e}"}

# Example usage (optional, for testing the function)
if __name__ == "__main__":
    test_text = "I'm so excited for the concert tonight!"
    sentiment = classify_sentiment(test_text)
    print(f"Sentiment for '{test_text}': {sentiment}")

    test_text_2 = "This is a very disappointing experience."
    sentiment_2 = classify_sentiment(test_text_2)
    print(f"Sentiment for '{test_text_2}': {sentiment_2}")

    test_text_3 = "I am feeling neutral about this."
    sentiment_3 = classify_sentiment(test_text_3)
    print(f"Sentiment for '{test_text_3}': {sentiment_3}")