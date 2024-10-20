import json
import os
import subprocess
from gtts import gTTS
from numpy.core.defchararray import endswith

from adaptive_ai import AdaptiveAI
from textblob import TextBlob
from fuzzywuzzy import process
import speech_recognition as sr  # Ensure you have this library installed
import requests

# from ai_assistant.speak import user_input

"""
    Voice Recognition (Speech-to-Text)

The assistant listens for voice commands through the microphone using either Google's Speech Recognition API (online) or CMU Sphinx (offline).
Once it captures the command, it converts the audio input into text for further processing.

    Text Processing
The assistant processes the recognized text to understand user intent.
Depending on the content of the command, it can execute specific actions or provide answers.

    NLP (Natural Language Processing) for Responses
The assistant uses NLP techniques to generate responses based on user input. This could involve answering questions, providing feedback, or initiating conversations.
    
    Learning from Conversations
The assistant stores interactions in a learning.json file, allowing it to continuously improve by referencing past conversations.
This creates a growing memory base that enhances the assistant’s understanding over time.
    
    Knowledge Base Access
The assistant uses the knowledge.json file to answer questions and provide information. This file contains predefined questions and answers.
If the assistant encounters unfamiliar queries, it can attempt to generate responses based on its memory (learning from interactions).
    
    Idea Generation
The assistant can generate ideas or provide suggestions based on past interactions or data stored in the learning.json file.
This feature helps in creative problem-solving, assisting the user with tasks like brainstorming or coming up with new insights.
    
    Voice Responses (Text-to-Speech)
The assistant can convert its text-based responses into speech using text-to-speech (TTS) libraries like Google Text-to-Speech (gTTS).
This enables the assistant to verbally communicate with the user, making interactions more natural.
    
    Error Handling and Feedback
The assistant handles errors gracefully, whether it's due to failed voice recognition, missing information, or other issues.
If the assistant is unable to perform a task, it provides feedback to the user, allowing for smoother communication.
    
    Internet Search (Under Development)
The assistant can automatically search the internet for information when the user encloses queries in quotation marks.
This functionality allows it to retrieve real-time information from the web when needed.

Primary Use Case
The assistant is designed to assist users with everyday tasks through a natural and intuitive interface—primarily voice-based. It can help with:

Providing information
Holding conversations
Answering questions
Learning and improving based on interactions
Generating ideas or assisting with creative tasks
Searching for information online when required
Goals Moving Forward
Further Expansion of Knowledge Base: Continuously growing its ability to answer more complex questions by adding data to learning.json and knowledge.json.
Improving AI's Conversational Skills: Enhancing the AI’s ability to ask follow-up questions and engage in deeper conversations.
Enhancing Internet Search: Fully implementing the ability to search the web for information and seamlessly integrating it into conversations.
User-Specific Customization: Enabling the assistant to adapt more to the user’s personal preferences and past interactions, making it a more personalized tool.
"""

# Function to correct spelling with TextBlob
def correct_spelling(text):
    blob = TextBlob(text)
    corrected_text = blob.correct()
    return str(corrected_text)

# Function to find the closest match with FuzzyWuzzy
def suggest_closest_match(word, word_list):
    closest_match = process.extractOne(word, word_list)
    return closest_match

# Independent Speak function
def speak(text):
    """Convert text to speech and play it."""
    try:
        tts = gTTS(text=text, lang='en')
        audio_file = "response.mp3"
        tts.save(audio_file)

        if os.name == 'nt':
            os.startfile(audio_file)
        elif os.name == 'posix':
            subprocess.run(["xdg-open", audio_file])
        else:
            print("Unsupported OS for playing audio.")
    except Exception as e:
        print(f"Error in speech synthesis: {str(e)}")
        speak("There was an error generating my response.")

# Function to capture audio input and convert it to text
def listen_for_audio_command():
    """Capture audio input and return it as text using SpeechRecognition."""
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for your command...")

        audio = recognizer.listen(source)  # Listen for audio input

        try:
            # Using Google Web Speech API to recognize audio
            text = recognizer.recognize_sphinx(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""

# Learning Data Manager to handle learning.json
class LearningDataManager:
    def __init__(self, filename='learning.json'):
        """Initialize the manager with a filename and load the data."""
        self.filename = filename
        self.data = self.load_learning_data()

    def load_learning_data(self):
        """Load learning data from a JSON file."""
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                if 'entries' not in data:
                    return {"entries": []}  # Return an empty structure if 'entries' not found
                return data
        except FileNotFoundError:
            print(f"File {self.filename} not found. Creating a new one.")
            return {"entries": []}  # Return an empty structure if the file is not found
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.filename}. Returning an empty structure.")
            return {"entries": []}  # Return an empty structure if JSON is malformed

    def save_learning_data(self):
        """Save the current learning data back to the JSON file."""
        try:
            with open(self.filename, 'w') as file:
                json.dump(self.data, file, indent=4) #type: ignore # Save with indentation for readability
        except Exception as e:
            print(f"Error saving data to {self.filename}: {e}")

    def add_entry(self, question, answer):
        """Add a new entry to the learning data and save it."""
        new_entry = {
            "question": question,
            "answer": [answer],
            "follow_ups": [],
            "feedback": None
        }
        self.data['entries'].append(new_entry)
        self.save_learning_data()  # Automatically save after adding

    def find_entry_by_question(self, question):
        """Find an entry by matching the question."""
        for entry in self.data['entries']:
            if entry['question'].lower() == question.lower(): # Ensure there are answers available
                return random.choice(entry['answer'])  # Randomly select one answer
        return None

    def get_entries(self):
        """Return all the learning entries."""
        return self.data['entries']

# InputProcessor class for handling different user inputs
class InputProcessor:
    def __init__(self, assistant):
        self.assistant = assistant
        self.assist = Assistant
        self.aiassistant = AIAssistant()


    def process_input(self, user_input):
        """Process user input based on specific commands and prefixes."""
        user_input = user_input.strip().lower()

        if user_input.startswith('#'):
            app_name = user_input  # Get the app name after the #
            return self.run_application(app_name)
        elif user_input.startswith('/') and user_input.endswith('/'):
            word_to_define = user_input[1:-1].strip()
            word_define = word_to_define[0].upper() + word_to_define[1:]
            return self.search_dictionary(word_define)
        elif user_input.startswith('"') and user_input.endswith('"'):
            query = user_input[1:-1]  # Remove the surrounding quotes
            return self.search_internet(query)
        elif user_input:
            return self.search_learning_json(user_input)
        elif user_input.startswith("define "):
            word_to_define = user_input[7:].strip()  # Get the word after 'define '
            return self.reasoning_function(word_to_define)

        return None

    def run_application(self, app_name):
        """Run a specified application."""
        # print(f"Running application: {app_name}")
        if app_name.startswith("# run "):
            run = self.assistant.execute_command(app_name)
            # You can integrate an actual command to run applications if needed.
            return f"Executed command to {run}."
        elif app_name.startswith("# open "):
            open_d = self.assistant.execute_command(app_name)
            return f"Execute command to {app_name}"

    def search_dictionary(self, word):
        """Search for the definition of a word in the dictionary."""
        print(f"Searching for '{word}' in the dictionary.")
        # Simulating a dictionary lookup (replace this with an actual lookup function)
        definition = self.aiassistant.get_word_meaning(word)   # Assume this function retrieves the definition
        if definition:
            return f"Definition for '{word}': {definition}."
        return f"No definition found for '{word}'."

    def search_internet(self, query):
        """Search the internet for a query."""
        print(f"Searching the internet for: {query}")
        # Simulating an internet search (replace this with an actual search API)
        results = self.aiassistant.search_internet(query)  # Assume this function handles searching
        if results:
            return f"Search results for: {query}\nResults: {results}."
        return f"No results found for: {query}."

    def search_learning_json(self, query):
        """Search for a query in the learning.json."""
        print(f"Searching for '{query}' in learning.json.")
        entry = self.assistant.learning_data_manager.find_entry_by_question(query)
        return entry

    def reasoning_function(self, word):
        """Provide reasoning or knowledge based on the defined word."""
        print(f"Defining '{word}' using reasoning.")
        reasoning = self.aiassistant.reason_out_answer(word)  # Assume this function provides reasoning
        if reasoning:
            return f"Reasoned response for '{word}': {reasoning}."
        return f"No reasoning available for '{word}'."


# Assistant class to handle the overall interaction and AI behavior
class Assistant:
    def __init__(self):
        self.ai = AdaptiveAI()  # Initialize the AdaptiveAI instance
        self.learning_data_manager = LearningDataManager()  # Initialize the Learning Data Manager
        self.data = self.learning_data_manager.data  # Load learning data
        self.input_processor = InputProcessor(self)

    def choose_input_method(self):
        """Prompt the user to choose between text or audio input."""
        while True:
            choice = input("Choose input method (text/audio): ").strip().lower()

            if choice == 'text':
                return input("You: ").strip()  # Get text input from the user
            elif choice == 'audio':
                return listen_for_audio_command()  # Use the audio command function
            else:
                print("Invalid choice. Please enter 'text' or 'audio'.")

    def speak(self, text):
        """Convert text to speech and play it."""
        speak(text)

    def execute_command(self, user_input):
        """Execute a command based on user input."""
        command = user_input.lower()

        if command.startswith("# run "):
            cmd_to_run = command[6:].strip()
            return self.run_command(cmd_to_run)
        elif command.startswith("# open "):
            path_to_open = command[7:].strip()
            return self.open_file_or_folder(path_to_open)
        else:
            return "Sorry, I can't perform that command."

    def run_command(self, cmd):
        """Run a command on the system."""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def open_application(self, app_name):
        """Open an application based on the operating system."""
        try:
            if os.name == 'nt':  # For Windows
                os.startfile(app_name)
            elif os.name == 'posix':  # For Linux
                subprocess.Popen([app_name])
            else:
                return "Unsupported OS for running applications."
            return f"Opening {app_name}..."
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"

    def open_file_or_folder(self, path):
        """Open a file or folder."""
        if os.path.exists(path):
            try:
                if os.path.isfile(path):
                    os.startfile(path)  # Windows-specific
                else:
                    subprocess.Popen(f'explorer {path}')  # Open folder in Windows Explorer
                return f"Opening {path}..."
            except Exception as e:
                return f"Error opening file/folder: {str(e)}"
        else:
            return "The specified file or folder does not exist."

    def interact(self):
        """Interface for interacting with the AI assistant."""
        while True:
            user_input = self.choose_input_method()  # Get user input based on the selected method

            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            response = self.input_processor.process_input(user_input)

            if response:
                print(f"AI Response: {response}")
                self.speak(response)  # Generate verbal response
            else:
                print("AI Response: I'm sorry, I don't have an answer for that.")
                self.speak("I'm sorry, I don't have an answer for that.")

class AIAssistant:
    def __init__(self, dictionary_file='dictionary.json', response_function=None):
        self.dictionary_file = dictionary_file
        self.spell_checker = TextBlob
        self.load_dictionary()
        self.get_ai_response = response_function  # Assign the passed function

    def load_dictionary(self):
        """Load the dictionary from the specified JSON file."""
        try:
            with open(self.dictionary_file, 'r') as file:
                self.dictionary = json.load(file)
        except FileNotFoundError:
            self.dictionary = {}
            print("Dictionary file not found. Please ensure it exists.")

    def get_word_meaning(self, word):
        """Retrieve the definition of a word from the loaded dictionary."""
        if not word:
            return "Meaning not found."  # Handle empty word case
        return self.dictionary.get(word, "Definition not found.")

    def search_internet(self, query):
        """Search the internet for a given query using DuckDuckGo."""
        print(f"Searching the internet for: {query}")
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_redirect': 1,
            'no_html': 1,
            'skip_disambig': 1,
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()

            # Extracting relevant information from the response
            if 'RelatedTopics' in data:
                results = []
                for topic in data['RelatedTopics']:
                    if isinstance(topic, dict) and 'Text' in topic:
                        results.append(topic['Text'])
                return results if results else ["No results found."]
            else:
                return ["No results found."]
        except Exception as e:
            return [f"Error occurred while searching: {str(e)}"]

    def reason_out_answer(self, user_input):
        """AI tries to reason out an answer based on context and learned data."""
        if user_input.startswith("/") and endswith("/"): #type: ignore
            word_to_define = user_input[1:-1].strip()
            meaning = self.get_word_meaning(word_to_define)
            if meaning:
                return f"The definition of /{word_to_define}/ is: {meaning}"
            return f"I couldn't find the definition of '{word_to_define}'. Would you like me to search for it?"

        elif user_input.startswith('define '):
            word_to_define = user_input.split(' ', 1)[1] if len(user_input.split(' ', 1)) > 1 else ''
            meaning = self.get_word_meaning(word_to_define)
            word_define = word_to_define[6:].strip()
            meaning2 = self.get_ai_response(word_define)
            if meaning2:
                return f"My thought on '{word_to_define}' is: {meaning2}"
            if meaning:
                return f"The definition of '{word_to_define}' is: {meaning}"
            else:
                return f"I couldn't find any relevant information for '{word_to_define}'."

# Example function for AI responses wn

# from flask import Flask, request, jsonify
import random
from nltk.corpus import wordnet as wn

# Sample data for AI responses (this could be loaded from a file or database)
data = {
    "python": "Python is a high-level programming language.",
    "ai": "AI stands for Artificial Intelligence.",
    "quantum": "Quantum refers to the smallest possible discrete unit of any physical property."
}


def get_ai_response(user_input, data):
    """Generate AI response using the data."""

    # Normalize user input
    user_input_lower = user_input.lower()

    # Tokenization (split input into words)
    tokens = user_input_lower.split()

    # Check for keywords in user input
    found_responses = []

    for token in tokens:
        # Direct match in the data
        if token in data:
            found_responses.append((data[token], 1.0))  # Confidence of 1.0 for direct matches

        # Check for synonyms
        synonyms = wn.synsets(token)
        for syn in synonyms:
            for lemma in syn.lemmas():
                if lemma.name().lower() in data:
                    found_responses.append((data[lemma.name().lower()], 0.8))  # Lower confidence for synonyms

    # If matches are found, select a response
    if found_responses:
        response, confidence = random.choice(found_responses)
        return f"AI Response (Confidence: {confidence}): {response}"

    # If no match, return a default response
    return None  # Changed to return None for better handling

# Any other assistant functionalities can be defined here as needed

if __name__ == '__main__':
    assistant = Assistant()
    assistant.interact()