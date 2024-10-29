from flask import Flask, request, jsonify
from utils import search_internet, append_learning_data, get_ai_response
# from utils import load_learning_data
# Import the get_ai_response function
from adaptive_ai import AdaptiveAI  # Import the AdaptiveAI class

app = Flask(__name__)

# Initialize AdaptiveAI instance
ai = AdaptiveAI()

# Load learning data once on startup
data = ai.data  # Assuming ai.data contains necessary learning data

@app.route('/ask', methods=['POST'])
def ask():
    """Handle user input and return AI-generated responses or internet search results."""
    user_input = request.json.get('input', '').strip().lower()

    if not user_input:
        return jsonify({"error": "No input provided."}), 400  # Bad request

    # Check if the user input is enclosed in quotes for an internet search
    if user_input.startswith('"') and user_input.endswith('"'):
        query = user_input.strip('"')
        response = search_internet(query)
    else:
        # Get AI response from the learning data
        response = get_ai_response(user_input, data)

    # Save new data only if the response is meaningful
    if response and len(response) > 10:
        append_learning_data(user_input, response, data)

    # Log the response for debugging
    print(response)

    return jsonify({"entries": response or "I'm sorry, I couldn't understand that. Please rephrase your question."})


@app.route('/speak', methods=['POST'])
def speak():
    """Handle user input and return a verbal response."""
    user_input = request.json.get('input', '').strip().lower()
    response = get_ai_response(user_input, data)
    audio_file = ai.speak(response)  # Generate verbal response
    return jsonify({"entries": response, "audio_file": audio_file})

@app.route('/define', methods=['POST'])
def define():
    """Fetch word meaning from the dictionary."""
    word = request.json.get('word', '').strip().lower()
    meaning = ai.get_word_meaning(word)
    return jsonify({"word": word, "meaning": meaning})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=False, port=5001)  # Ensure this block is included
