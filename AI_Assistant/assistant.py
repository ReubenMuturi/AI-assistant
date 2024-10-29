# import json
import os
import subprocess
# from dataManagement import LearningDataManager
# from numpy.core.defchararray import endswith
from dataManagement import LearningDataManager
from adaptive_ai import AdaptiveAI
from textblob import TextBlob
# import speech_recognition as sr  # Ensure you have this library installed
import requests
from communication import listen_for_audio_command, speak
# from utils import get_ai_response, append_learning_data
# from ai_assistant.speak import user_input
import json
import random
import string
from utils import get_ai_response
from gtts import gTTS
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


class InputProcessor:
    def __init__(self, assistant):
        self.assistant = assistant
        self.assist = Assistant
        self.aiassistant = AIAssistant()
        self.learning_data_manager = LearningDataManager() # Instance of LearningDataManager
        self.generate_response = get_ai_response  # Assign function reference, not execution
        self.learning_data = self.learning_data_manager.data  # Load learning data directly from the manager
        self.data = self.learning_data_manager.data  # Ensure this points to the correct data structure

    def process_input(self, user_input):
        """Process user input based on specific commands and prefixes."""
        user_input = user_input.strip().lower()
        print(user_input)  # Debug: log user input

        try:
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
            elif user_input.startswith("define "):
                word_to_define = user_input[7:].strip()  # Get the word after 'define '
                return self.reasoning_function(word_to_define)
            elif user_input:  # Use AI response generation here
                learning = self.search_learning_json(user_input)
                speak(learning)
                return learning

        except Exception as e:
            print(f"Error processing input: {e}")  # Log any processing errors
            return None


    def run_application(self, app_name):
        """Run a specified application."""
        if app_name.startswith("# run "):
            run = self.assistant.execute_command(app_name)
            return f"Executed command to {run}."
        elif app_name.startswith("# open "):
            open_d = self.assistant.execute_command(app_name)
            return f"Executed command to {app_name}"

    def search_dictionary(self, word):
        """Search for the definition of a word in the dictionary."""
        print(f"Searching for '{word}' in the dictionary.")
        # Assuming aiassistant has a function to retrieve definitions
        definition = self.aiassistant.get_word_meaning(word)
        if definition:
            return f"Definition for '{word}': {definition}."
        return f"No definition found for '{word}'."

    def search_internet(self, query):
        """Search the internet for a query."""
        print(f"Searching the internet for: {query}")
        # Simulate an internet search
        results = self.aiassistant.search_internet(query)
        if results:
            return f"Search results for: {query}\nResults: {results}."
        return f"No results found for: {query}."

    def search_learning_json(self, user_input):
        """Search for a response in the learning data."""
        user_input = user_input.lower().strip(string.punctuation)
        # print(f"User Input: {user_input}")  # Debugging: print the user input
        for entry in self.learning_data.get('entries', []):  # Use get to avoid KeyError
            if isinstance(entry, dict):
                question = entry.get("question", "").lower() # Use get to avoid KeyError
                question = question.strip(string.punctuation)
                # print(f"Comparing with: {question}")  # Debugging: print the question being compared
                if question == user_input:  # Indicate a match has been found
                    answers = entry.get('answer', [])  # Get answers, default to empty list
                    if answers:  # Check if answers list is not empty
                        return random.choice(answers)  # Return a random answer
                    else:
                        print("No answers available in my data but I will try to generate my answer.")  # Debugging

        return None  # Return None if no matching entry is found

    def get_ai_response(self, user_input):
        """Get AI response based on user input and learning data."""
        for entry in self.data:
            if entry['question'] == user_input:  # Ensure you're comparing correctly
                return entry['answer'][0]  # Assuming answer is a list
        return "I'm sorry, I don't have an answer for that."


    def append_learning_data(self, question, answer):
        """Append new learning data to the JSON and save it."""
        self.learning_data_manager.add_entry(question, answer)  # Add a new entry and save it

    def reasoning_function(self, word):
        """Provide reasoning or knowledge based on the defined word."""
        print(f"Defining '{word}' using reasoning.")
        reasoning = self.aiassistant.reason_out_answer(word)  # Assume this function provides reasoning
        if reasoning:
            return f"Reasoned response for '{word}': {reasoning}."
        return f"No reasoning available for '{word}'."


class Assistant:
    def __init__(self):
        self.ai = AdaptiveAI()  # Initialize the AdaptiveAI instance
        self.learning_data_manager = LearningDataManager()  # Initialize the Learning Data Manager
        self.data = self.learning_data_manager.data  # Load learning data
        self.input_processor = InputProcessor(self)
        self.get_response = InputProcessor(self)
        self.get_ai_response = self.get_response.reasoning_function

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
        if text.strip() == "":
            return  # Avoid speaking empty text

        # Create the gTTS object and save the speech to an MP3 file
        tts = gTTS(text=text, lang='en')
        audio_file_path = "response.mp3"
        tts.save(audio_file_path)

        # Use subprocess to play the audio without blocking the main thread
        subprocess.Popen(["mpg123", audio_file_path], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


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

            # Check the response and print debug information
            if response:
                print(f"AI Response: {response}")
                self.speak(response)  # Generate verbal response
            else:
                ai_response = self.get_ai_response(user_input)  # Ensure this method exists
                # self.append_learning_data(user_input, ai_response)  # Optionally save learning data
                self.speak(ai_response)
                return ai_response  # Return the AI response        print("No match found.")  # Indicate no match was found




class AIAssistant:
    def __init__(self, dictionary_file='dictionary.json', file_path="learning.json", response_function=None):
        self.dictionary_file = dictionary_file
        self.spell_checker = TextBlob
        self.load_dictionary()
        self.get_ai_response = response_function  # Assign the passed function
        self.file_path = file_path
        self.learning_data_manager = LearningDataManager()  # Instance of LearningDataManager
        self.load_data = self.learning_data_manager.data  # Load learning data

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
        return self.dictionary.get(word.lower(), "Definition not found.")  # Case-insensitive lookup

    def search_internet(self, query):
        """Search the internet for a given query using DuckDuckGo and save new knowledge."""
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

            # Log the full response for debugging
            print(f"Full API Response: {data}")

            # Check for RelatedTopics and Results
            if 'RelatedTopics' in data and data['RelatedTopics']:
                results = []
                for topic in data['RelatedTopics']:
                    if isinstance(topic, dict) and 'Text' in topic:
                        results.append(topic['Text'])

                if results:
                    # Save the first result to learning data
                    self.update_knowledge(query, results[0])
                    return results[0]  # Return the first result for simplicity

            # Fallback if no results found
            return f"I couldn't find any information on '{query}'. Would you like to know a definition or general thought about love?"

        except requests.RequestException as e:
            return f"Network error occurred: {str(e)}"
        except json.JSONDecodeError:
            return "Error decoding the response from the API."

    def reason_out_answer(self, user_input):
        """AI tries to reason out an answer based on context and learned data."""

        # Handles definitions within /word/
        if user_input.startswith("/") and user_input.endswith("/"):
            word_to_define = user_input[1:-1].strip()
            meaning = self.get_word_meaning(word_to_define)
            if meaning:
                return f"The definition of /{word_to_define}/ is: {meaning}"
            return f"I couldn't find the definition of '{word_to_define}'. Would you like me to search for it?"

        # Handles "define word" format
        elif user_input.startswith('define '):
            word_to_define = user_input.split(' ', 1)[1] if len(user_input.split(' ', 1)) > 1 else ''
            meaning = self.get_word_meaning(word_to_define)
            if meaning:
                return f"The definition of '{word_to_define}' is: {meaning}"
            else:
                # Search the internet for the word's definition
                internet_results = self.search_internet(word_to_define)
                if internet_results:
                    return f"Here's what I found online for '{word_to_define}': {internet_results[0]}"
                else:
                    # Fallback to general knowledge if no online results found
                    fallback_knowledge = {
                        "love": "Love is a profound and caring affection towards someone or something.",
                        "friendship": "Friendship is a close relationship between two people who care about each other.",
                        # Add more fallback definitions as needed
                    }
                    return f"I couldn't find any information for '{word_to_define}'. However, I know that: {fallback_knowledge.get(word_to_define.lower(), 'I don’t have any thoughts on that.')}"

        # If AI doesn't know, offer to search the internet and update learning data
        elif self.get_ai_response:
            response = self.get_ai_response(user_input)
            if response:
                return f"My thought on '{user_input}' is: {response}"
            else:
                internet_results = self.search_internet(user_input)
                if internet_results:
                    return f"Here's what I found online for '{user_input}': {internet_results[0]}"
                else:
                    # Provide a general fallback response
                    fallback_response = "I'm not sure about that. Would you like to ask something else or try rephrasing?"
                    return f"I'm not sure about '{user_input}', and I couldn't find much online either. {fallback_response}"


    def update_knowledge(self, question, answer):
        """Update the learning data with new knowledge."""
        self.learning_data_manager.add_entry(question, answer)
        return f"I've added new knowledge for: '{question}' with answer '{answer}'."


# Example usage:
ai_assistant = AIAssistant()

# Ask for the meaning of a word
response = ai_assistant.reason_out_answer("what does it mean by love?")
print(response)

# Ask for AI's thoughts or knowledge
response = ai_assistant.reason_out_answer("What is the meaning of life?")
print(response)

# Add new knowledge
ai_assistant.update_knowledge("What is Python?", "Python is a programming language.")

# Example function for AI responses wn


# Any other assistant functionalities can be defined here as needed

if __name__ == '__main__':
    assistant = Assistant()
    assistant.interact()
