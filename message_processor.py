from text_utils import scrub_unsafe_characters, chunk_text
from feels_classifier import classify_sentiment

def process_message_for_tts(message: str) -> list[dict]:
    """
    Processes a message by chunking, scrubbing, and classifying sentiment for each chunk.

    Args:
        message: The input message string from the LLM.

    Returns:
        A list of dictionaries, where each dictionary contains the processed chunk,
        its sentiment classification, and the original chunk.
        Example: [{"original_chunk": "...", "processed_chunk": "...", "sentiment": {"emotion": "joy", "score": 0.99}}]
    """
    
    # Chunk the message if it's too long
    # The chunk_text function handles the tokenization and splitting
    chunks = chunk_text(message)
    
    processed_results = []

    for chunk in chunks:
        # Scrub unsafe characters from the chunk
        scrubbed_chunk = scrub_unsafe_characters(chunk)
        
        # Classify the sentiment of the scrubbed chunk
        sentiment = classify_sentiment(scrubbed_chunk)
        
        # Print debug statement
        if "error" not in sentiment:
            print(f"Debug: Sentiment for chunk - Emotion: {sentiment['emotion']}, Score: {sentiment['score']:.2f}")
        else:
            print(f"Debug: Sentiment classification failed for chunk: {sentiment['error']}")
            
        processed_results.append({
            "original_chunk": chunk,
            "processed_chunk": scrubbed_chunk,
            "sentiment": sentiment
        })
        
    return processed_results

# Example usage (optional, for testing the function)
if __name__ == "__main__":
    long_message = "This is a very long message that needs to be processed. It contains various emotions and characters. I am so happy today! But also a little bit sad. What a surprise! This should be chunked and analyzed. Let's see if it works. 😊👍" * 5
    
    print("--- Processing long message ---")
    results = process_message_for_tts(long_message)
    
    for i, result in enumerate(results):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Original Chunk: {result['original_chunk'][:100]}...") # Print first 100 chars
        print(f"Scrubbed Chunk: {result['processed_chunk'][:100]}...") # Print first 100 chars
        print(f"Sentiment: {result['sentiment']}")

    short_message = "I feel great!"
    print("\n--- Processing short message ---")
    results_short = process_message_for_tts(short_message)
    for i, result in enumerate(results_short):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Original Chunk: {result['original_chunk']}")
        print(f"Scrubbed Chunk: {result['processed_chunk']}")
        print(f"Sentiment: {result['sentiment']}")