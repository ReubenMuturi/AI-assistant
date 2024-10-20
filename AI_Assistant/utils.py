import json
import requests
from gtts import gTTS
import tempfile
import string


# Load the learning data from learning.json
def load_learning_data(filename='learning.json'):
    """Load learning data from a JSON file."""
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data if 'entries' in data else {"entries": []}
    except FileNotFoundError:
        return {"entries": []}  # Return an empty structure if the file is not found
    except json.JSONDecodeError:
        return {"entries": []}  # Return an empty structure if JSON is malformed


def save_learning_data(data, filename='learning.json'):
    """Save learning data to a JSON file."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4) #type: ignore


def get_ai_response(user_input, data):
    """Generate a response for the user's input based on learning data."""
    # Check if the input starts with a '#', in which case it should be passed as is
    if user_input.startswith('#'):
        print(f"Command received: {user_input}")  # Debugging
        return execute_command(user_input)

    # Normalize input by converting to lowercase and stripping extra spaces
    user_input = user_input.lower().strip()
    user_input_no_punct = user_input.translate(str.maketrans('', '', string.punctuation))

    # Access the 'entries' list in the data dictionary
    entries = data.get('entries', [])
    if not isinstance(entries, list) or not entries:
        print("No knowledge stored.")  # Debugging
        return "Error: No knowledge stored."

    # Find the corresponding entry in the data
    existing_entry = next(
        (entry for entry in entries if
         entry.get('question', '').lower().translate(str.maketrans('', '', string.punctuation)) == user_input_no_punct),
        None
    )

    # If an entry is found, return the answer
    return existing_entry.get('answer',
                              "Sorry, I don't have a proper answer for that.") if existing_entry else "I couldn't find any relevant information for that."


def execute_command(user_input):
    """Placeholder for command execution logic."""
    return f"Executing: {user_input[1:].strip()}"  # Remove '#' and execute the rest of the command


def search_internet(query):
    """Search the internet using the Google Custom Search API and return a snippet."""
    api_key = ''  # Replace with your actual API key
    search_engine_id = ''  # Replace with your actual Search Engine ID
    search_url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}"

    try:
        response = requests.get(search_url)
        response.raise_for_status()  # Raise an error for bad responses
        results = response.json().get('items', [])

        if results:
            snippet = results[0]['snippet']  # Get the first search result snippet
            return f"I found some information online: {snippet} Would you like to know more about this topic?"
        else:
            return "I couldn't find anything relevant online."
    except requests.RequestException as e:
        return f"Error searching the internet: {str(e)}"


def append_learning_data(user_input, response, data):
    """Append new learning data to the dictionary."""
    if isinstance(data, dict):
        # Check if user_input already exists in data
        if user_input not in data:
            data[user_input] = response  # Add new entry to the dictionary
        else:
            # If user_input already exists, append to the existing responses
            if isinstance(data[user_input], list):
                data[user_input].append(response)
            else:
                data[user_input] = [data[user_input], response]
    else:
        print("Error: Data is not a dictionary.")


def respond_verbal(response):
    """Convert the text response to speech and save it as an audio file."""
    try:
        tts = gTTS(text=response, lang='en')
        # Create a temporary file to save the audio
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.mp3')
        tts.save(temp_file.name)  # Save the audio file
        return temp_file.name  # Return the path to the audio file
    except Exception as e:
        return f"Error generating audio response: {str(e)}"
