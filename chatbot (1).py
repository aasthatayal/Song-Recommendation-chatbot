#SONG RECOMMENDATION CHATBOT: MOODTUNES
import os
import random
import re
import nltk
#nltk.download('vader_lexicon')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from textblob import TextBlob
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from nltk.sentiment import SentimentIntensityAnalyzer

sound=""
mood=""
global pause_button
pause_button=None

class ChatBotApp(App):
    def build(self):
        global pause_button

        # Change the window size
        Window.size = (440, 280)

        # Create the main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Set the background image
        with layout.canvas.before:
            bg_color = Color(1, 1, 1, 1)
            bg_image = Rectangle(source='C:/image/image.jpeg', pos=layout.pos, size=layout.size,
                                 pos_hint={'center_x': 0.5, 'center_y': 0.5})

            # Bind the background image update to the layout's pos and size properties
            layout.bind(pos=self._update_background_image, size=self._update_background_image)

        # Create a scroll view for the chat history
        self.scroll_view = ScrollView()

        # Create a layout for the chat history
        self.chat_layout = BoxLayout(orientation='vertical', size_hint=(1, None), spacing=10, padding=10)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))

        # Add the chat layout to the scroll view
        self.scroll_view.add_widget(self.chat_layout)

        # Add the scroll view to the main layout
        layout.add_widget(self.scroll_view)

        # Create a BoxLayout for the input text box and its border
        input_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=5)

        # Create a text input for user messages
        self.text_input = TextInput(multiline=False,
                                    size_hint=(1, 0.15),
                                    font_size=14,
                                    background_color=(0, 0, 0, 0),
                                    foreground_color=(0, 0, 0, 1),
                                    hint_text='Type Something: ')
        self.text_input.bind(on_text_validate=self.send_message)  # Bind the enter key press event

        layout.add_widget(self.text_input)

        # Create a label for displaying the song name
        self.song_name_label = Label(pos_hint={'x': 0, 'y': 1},
                                     size_hint=(0.5, 0.1),
                                     font_size=12,
                                     color=(0, 0, 0, 1))  # Set bright black text color
        layout.add_widget(self.song_name_label)

        # Create buttons for sending messages and controlling music
        button_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)

        send_button = Button(text='SEND',
                             background_color=(0, 0, 0, 1),
                             size_hint=(1, 0.25),
                             font_size=15,
                             color=(1, 1, 1, 1))  # Set bright white text color
        send_button.bind(on_press=self.send_message)
        button_layout.add_widget(send_button)

        self.play_button = Button(text='STOP',
                                  background_color=(0, 0, 0, 1),
                                  size_hint=(1, 0.25),
                                  font_size=15,
                                  color=(1, 1, 1, 1))  # Set bright white text color
        self.play_button.bind(on_press=self.play_music)
        button_layout.add_widget(self.play_button)

        pause_button = Button(text='PAUSE',
                              background_color=(0, 0, 0, 1),
                              size_hint=(1, 0.25),
                              font_size=15,
                              color=(1, 1, 1, 1))  # Set bright white text color
        pause_button.bind(on_press=self.pause_music)
        button_layout.add_widget(pause_button)

        # Create the resume button
        shuffel_button = Button(text='SHUFFLE',
                               background_color=(0, 0, 0, 1),
                               size_hint=(1, 0.25),
                               font_size=15,
                               color=(1, 1, 1, 1))  # Set bright white text color
        shuffel_button.bind(on_press=self.shuffel_music)
        button_layout.add_widget(shuffel_button)

        layout.add_widget(button_layout)

        # Create a label for displaying the mood analysis result
        self.mood_label = Label(size_hint=(1, 0.25),
                                font_size=21,
                                color=(0, 0, 0, 1))  # Set bright black text color
        layout.add_widget(self.mood_label)

        # Add the initial message from the chatbot
        self.update_chat("Hello, \n How can I assist you today?", 'MoodTunes')

        return layout

    def _update_background_image(self, instance, value):
        # Clear the canvas before updating the background image
        instance.canvas.before.clear()

        # Set the background image
        with instance.canvas.before:
            bg_image = Rectangle(source='C:/image/image.jpeg', pos=instance.pos, size=instance.size)

    def send_message(self, instance):
        global sound
        global mood

        user_message = self.text_input.text

        # Remove special characters from the user's message
        user_message = re.sub('[^A-Za-z0-9\s]+', '', user_message)

        # Remove extra spaces from the user's message
        user_message = re.sub('\s+', ' ', user_message)

        # Insert spaces before capital letters that follow lowercase letters
        user_message = re.sub(r'([a-z])([A-Z])', r'\1 \2', user_message)

        # Process the user's message and generate a response
        bot_response = self.generate_response(user_message)

        # Update the chat label with the user's message and the bot's response
        self.update_chat(user_message, 'User')
        self.update_chat(bot_response, 'MoodTunes')

        # Perform sentiment analysis on the user's message
        sentiment, subjectivity = self.analyze_sentiment(user_message)

        # Determine the mood based on sentiment
        mood = self.determine_mood(sentiment, subjectivity)

        # Play a random song based on the mood
        if mood == 'Strongly Positive and Subjective':
            # Check if a song is already playing
            if sound and sound.state == 'play':
                sound.stop()

            self.mood_label.text = f'YOU ARE CURRENTLY FEELING: HAPPY!'
            self.play_random_song_from_folder("happy")

        elif mood == 'Strongly Negative and Subjective':
            # Check if a song is already playing
            if sound and sound.state == 'play':
                sound.stop()

            self.mood_label.text = f'YOU ARE CURRENTLY FEELING: ANGRY/DEVASTATED!'
            self.play_random_song_from_folder("sad")

        elif mood == 'Positive and Objective':
            # Check if a song is already playing
            if sound and sound.state == 'play':
                sound.stop()

            self.mood_label.text = f'YOU ARE CURRENTLY FEELING: CONTENT!'
            self.play_random_song_from_folder("happy")

        elif mood == 'Negative and Objective':
            # Check if a song is already playing
            if sound and sound.state == 'play':
                sound.stop()

            self.mood_label.text = f'YOU ARE CURRENTLY FEELING: SAD!'
            self.play_random_song_from_folder("sad")

        elif mood == 'Neutral':
            self.mood_label.text = "CURRENTLY YOUR MOOD IS NEUTRAL!"

        # Clear the text input
        self.text_input.text = ''

        # Show the hint text again
        self.text_input.hint_text = 'Type Something: '

    def generate_response(self, message):
        lowercase_message = message.lower()

        if re.search(r'\bhello\b|\bhi\b|\bhey\b|\bhiiiii\b|\bhi there\b', lowercase_message):
            responses = ["Hi there!", "Hello!", "Hey!", "What's up!"]

        elif re.search(r'\bhow are you\b|\bhow are you doing\b|\bhow are you today\b', lowercase_message):
            responses = ["I'm doing well, thank you! How are you?", "I'm great, thanks for asking! How about you?",
                         "I'm feeling good today! How about yourself?"]

        elif re.search(r'\bim\b|\bokay\b', lowercase_message) and not re.search(r'\bnot\b', lowercase_message):
            responses = ["That's good to hear! If there's anything on your mind, feel free to share. I'm here to listen.",
                         "Alright, but remember, I'm here for you if you ever want to talk or need support.",
                         "Okay, got it. Just know that I'm here if you need someone to talk to or if there's anything I can do to help."]

        elif re.search(r'\btell\b', lowercase_message) or re.search(r'\bjoke\b', lowercase_message):
            responses = [
                "Sure! Here's a joke for you: Why don't scientists trust atoms? Because they make up everything!",
                "Of course! I can also tell you something interesting. What topic are you interested in?",
                "Certainly! How about a joke? What did one wall say to the other wall? I'll meet you at the corner!"]

        elif re.search(r'\btell\b', lowercase_message):
            responses = ["Sure, I can tell you something. What would you like to know?",
                         "Of course! What kind of information are you looking for?",
                         "Certainly! What specific topic or question would you like me to address?"]

        elif re.search(r'\bjoke\b', lowercase_message):
            responses = [
                "Sure, here's a joke for you: Why don't scientists trust atoms? Because they make up everything!",
                "I've got a joke for you: Why don't skeletons fight each other? They don't have the guts!",
                "Here's a joke: What did one wall say to the other wall? I'll meet you at the corner!"]

        elif re.search(r'\bhow was your day\b', lowercase_message):
            responses = ["My day was fine. How was yours?", "Good. And yours?"]

        elif re.search(
                r'\btalk to me\b|\btalk with me\b|\bcan you talk to me\b|\bcan we please talk\b|\bwill you talk to me\b',
                lowercase_message):
            responses = ["Sure why not! Tell me how was your day"]

        elif re.search(
                r'\brecommend a song\b|\bsuggest a song\b|\bgive me a song recommendation\b|\bplay a song for me\b|\bplay a song\b',
                lowercase_message):
            responses = ["Sure! I recommend listening to a song based on your mood.",
                         "Sure! would you like to share your emotions?"
                         "Of course! Could you tell me how you are feeling so that I can find the perfect song for you?"]

        elif re.search(r'\bwhat is your name\b|\byour name\b|\bwhats your name\b|\bcan you tell me your name\b',
                       lowercase_message):
            responses = ["My name is Chatbot. How can I assist you?", "I'm Chatbot, nice to meet you!"]

        elif re.search(
                r'\bhow does your chatbot work\b|\bhow do you work\b|\bhow can you work\b|\bhow can your chatbot work\b',
                lowercase_message):
            responses = [
                "I use natural language processing algorithms to analyze your messages and generate responses.",
                "I'm powered by artificial intelligence and machine learning techniques."]

        elif re.search(r'\bthank you\b|\bthanks\b|\bthank you so much\b', lowercase_message):
            responses = ["You're welcome!", "No problem!", "Happy to help!"]

        elif re.search(r'\btell me a joke\b', lowercase_message):
            responses = ["Why don't scientists trust atoms? Because they make up everything!",
                         "Why did the scarecrow win an award? Because he was outstanding in his field!"]

        elif re.search(r'\b(my name is|I am|I\'m) \w+\b', lowercase_message):
            # Extract the name from the user's message
            name = re.search(r'\b(my name is|I am|I\'m) (\w+)\b', lowercase_message).group(2)
            responses = [f"Nice to meet you, {name}!", f"Hi, {name}!\nHow can I assist you?"]

        elif re.search(
                r'\b(i\'m fine|i\'m doing great|im feeling great today|great|happy|im feeling happy|im feeling happy today|im happy)\b',
                lowercase_message):
            responses = ["Glad to hear that!", "That's great!", "Good to know!"]

        elif re.search(r'\bwhat\s+.*?\b(?:you|u)\s+.*?\bdo\b', lowercase_message, re.IGNORECASE):
            responses = ["I can assist you with a variety of tasks!",
                         "I'm here to help you with information and tasks.",
                         "I can answer questions, provide information, and more."]

        elif re.search(r'\booh\b|\boh\b|\bI see\b|\bgot it\b', lowercase_message, re.IGNORECASE):
            responses = ["Interesting!", "Ah, I understand.", "I see.", "Great!"]
            return random.choice(responses)

        elif re.search(r'\b(i\'m great|im great)\b', lowercase_message):
            responses = ["Awesome!", "That's fantastic!", "Great to hear!"]

        elif re.search(r'\b(i\'m happy|im happy)\b', lowercase_message):
            responses = ["I'm happy for you!", "That's wonderful!", "Glad to hear you're happy!"]

        elif re.search(r'\b(i\'m angry|im feeling angry|angry)\b', lowercase_message):
            responses = ["Take a deep breath and try to calm down.",
                         "Anger is a normal emotion, but it's important to manage it in a healthy way.",
                         "Is there something specific that's making you angry?"]

        elif re.search(r'\b(i\'m sad|im feeling sad|sad)\b', lowercase_message):
            responses = ["I'm sorry to hear that you're feeling sad.",
                         "It's important to acknowledge your emotions and give yourself time to heal.",
                         "Do you want to talk about what's making you feel sad?"]

        elif re.search(r'\b(i\'m bored|im feeling bored|bored)\b', lowercase_message):
            responses = ["Boredom can be an opportunity for creativity or self-reflection.",
                         "Is there something you enjoy doing that could help pass the time?",
                         "Let's find something interesting for you to do!"]

        elif re.search(r'\b(i\'m scared|im feeling scared|scared)\b', lowercase_message):
            responses = ["It's natural to feel scared sometimes.",
                         "Try to identify what's causing your fear and think of ways to address it.",
                         "Remember, you're not alone. Reach out to someone you trust for support."]

        elif re.search(r'\b(i\'m ashamed|im feeling ashamed|ashamed)\b', lowercase_message):
            responses = ["Feeling ashamed can be tough.",
                         "Remember that everyone makes mistakes and it's an opportunity for growth.",
                         "Is there something specific that's causing your shame?"]

        elif re.search(r'\b(i\'m disgusted|im feeling disgusted|disgusted)\b', lowercase_message):
            responses = ["Disgust is a strong emotion.",
                         "Take a moment to reflect on what's causing your disgust and consider how to address it.",
                         "Is there something specific that's making you feel disgusted?"]

        elif re.search(r'\b(i\'m depressed|im feeling depressed|depressed)\b', lowercase_message):
            responses = ["I'm really sorry to hear that you're feeling depressed.",
                         "It's important to seek support from loved ones or a professional.",
                         "Remember that there is hope and help available to you."]

        elif re.search(r'\b(i\'m satisfied|im feeling satisfied|satisfied)\b', lowercase_message):
            responses = ["That's great to hear!", "Feeling satisfied is a wonderful emotion.",
                         "Celebrate your achievements and keep up the good work!"]

        elif re.search(r'\b(i\'m proud|im feeling proud|proud)\b', lowercase_message):
            responses = ["You should be proud of yourself!", "It's wonderful to feel a sense of pride.",
                         "Keep up the good work and continue to achieve great things!"]

        elif re.search(r'\b(i\'m envious|im feeling envious|envious)\b', lowercase_message):
            responses = ["Envy can be a challenging emotion.",
                         "Try to focus on your own strengths and accomplishments.",
                         "Remember, everyone's journey is unique."]

        elif re.search(r'\b(i\'m in love|im feeling in love|in love)\b', lowercase_message):
            responses = ["Love is a beautiful emotion.",
                         "Cherish the feeling and express your love to those who are important to you.",
                         "Wishing you a lifetime of love and happiness!"]

        elif re.search(r'\b(i\'m embarrassed|im feeling embarrassed|embarrassed)\b', lowercase_message):
            responses = ["We all feel embarrassed from time to time.", "Remember that it's a common human experience.",
                         "Don't be too hard on yourself and try to find humor in the situation."]

        elif re.search(r'\b(i\'m disappointed|im feeling disappointed|disappointed)\b', lowercase_message):
            responses = ["I'm sorry to hear that you're feeling disappointed.",
                         "Disappointment can be tough, but it's an opportunity to learn and grow.",
                         "Take some time for self-care and think about how you can move forward."]

        elif re.search(r'\b(i\'m confused|im feeling confused|confused)\b', lowercase_message):
            responses = ["Confusion is a natural part of the learning process.",
                         "Take a step back, gather information, and ask questions to gain clarity.",
                         "Don't hesitate to reach out for help or guidance."]

        elif re.search(r'\b(i\'m guilty|im feeling guilty|guilty)\b', lowercase_message):
            responses = ["Feeling guilty can be a sign that you value your actions and their impact on others.",
                         "Take responsibility for your actions and consider how to make amends if necessary.",
                         "Remember, we all make mistakes and it's important to learn from them."]

        elif re.search(r'\b(i\'m lonely|im feeling lonely|lonely)\b', lowercase_message):
            responses = ["I'm sorry to hear that you're feeling lonely.",
                         "It's important to reach out to others and seek connection.",
                         "You're not alone, and there are people who care about you."]

        elif re.search(r'\b(i\'m surprised|im feeling surprised|surprised)\b', lowercase_message):
            responses = ["Surprise can be a delightful emotion!",
                         "Enjoy the unexpected moment and embrace the element of surprise.",
                         "Life is full of surprises, and they can bring joy and excitement."]

        elif re.search(r'\b(i\'m contempt|im feeling contempt|contempt)\b', lowercase_message):
            responses = ["Feeling contempt can be challenging.",
                         "Try to understand the underlying reasons for your contempt and find constructive ways to address them.",
                         "It's important to approach situations with empathy and open-mindedness."]

        elif re.search(r'\b(i\'m admiring|im feeling admiring|admiring)\b', lowercase_message):
            responses = ["Admiration is a wonderful feeling!",
                         "Appreciate the qualities and actions of others that you admire.",
                         "Don't hesitate to express your admiration and inspire those around you."]

        elif 'office' in lowercase_message and 'tomorrow' in lowercase_message and 'want' in lowercase_message:
            responses = ["It seems like you're not looking forward to going to the office tomorrow.",
                         "I understand that you don't want to go to the office tomorrow.",
                         "Is there any specific reason why you don't want to go to the office tomorrow?"]

        elif re.search(r'\bthank you\b|\bthanks\b|\bthank you so much\b', lowercase_message):
            responses = ["You're welcome!", "No problem!", "Happy to help!"]

        elif re.search(r'\bbye\b|\bgoodbye\b|\bsee you later\b', lowercase_message):
            responses = ["Goodbye!", "Take care!", "See you later!"]

        elif re.search(r'\bsorry\b', lowercase_message):
            responses = ["No problem!", "It's alright.", "Don't worry about it."]

        elif re.search(r'\bcould you help\b|\bcould you assist\b', lowercase_message):
            responses = ["Of course! How can I assist you?", "I'm here to help. What do you need assistance with?"]

        elif re.search(r'\bwhat do you mean\b|\bcould you explain\b|\bcan you clarify\b', lowercase_message):
            responses = ["Sure! I'll be happy to explain. What specific part do you need clarification on?",
                         "Certainly! I'll do my best to provide a clear explanation. Please let me know what you're referring to."]

        elif re.search(r'\bhow can I contact you\b', lowercase_message):
            responses = ["You can contact me through this chat interface. How can I assist you?",
                         "You're already in contact with me through this chat. What do you need help with?"]

        elif re.search(r'\bwhat are you\b', lowercase_message):
            responses = ["I am a chatbot designed to assist with various tasks and provide information.",
                         "I'm an AI chatbot programmed to answer questions and engage in conversation."]

        elif re.search(r'\bwhat is your purpose\b', lowercase_message):
            responses = ["My purpose is to assist and provide helpful information to users.",
                         "I'm here to make your experience better by providing assistance and answering your questions."]

        elif re.search(r'\bwhere are you from\b', lowercase_message):
            responses = ["I'm an AI chatbot, so I don't have a physical location. I exist in the digital realm.",
                         "I don't have a specific location as I am an AI-powered chatbot."]

        elif re.search(r'\bwhen were you created\b', lowercase_message):
            responses = ["I was created recently and continuously updated to improve my performance.",
                         "As an AI chatbot, I don't have a specific creation date. I'm always evolving!"]

        elif re.search(r'\b(not|no|never)\b', lowercase_message):
            responses = ["Aw, I'm sorry to hear that. Is there anything I can do to help cheer you up?",
                         "Oh no, that's a bummer! I'm here for you if you need someone to talk to.",
                         "I totally get it, sometimes things just don't go our way. Anything I can do to make you feel better?",
                         "Yikes, that's no fun. Let's turn that frown upside down! What can I do to make your day better?",
                         "Is there anything I can do to help?"]

        elif re.search(r'\bnevermind\b', lowercase_message):
            responses = ["No problem! If there's anything else you'd like to discuss, just let me know.",
                         "Alright, if you change your mind or have any other questions, feel free to reach out!"]

        elif re.search(r'\bnothing\b', lowercase_message):
            responses = ["Alright, just remember I'm here if you need anything or if something comes up.",
                         "Got it! If there's anything you'd like to talk about later, don't hesitate to reach out!"]

        elif re.search(r'\bbored\b', lowercase_message):
            responses = [
                "I understand. If you need any suggestions for activities or want to chat about something, let me know!",
                "If you're feeling bored, maybe we can find something interesting to talk about. What's on your mind?"]

        elif re.search(r'\bfun\b', lowercase_message):
            responses = ["That sounds like fun! I'm here to chat and make your experience enjoyable.",
                         "Great! Let's have some fun and engage in a conversation. What would you like to talk about?"]

        elif re.search(r'\bchat with me\b', lowercase_message):
            responses = ["Absolutely! I'm here and ready to chat. What's on your mind?",
                         "Of course! I'm here for a chat. Feel free to share anything you'd like to discuss."]

        elif re.search(r'\bi want to tell you something\b', lowercase_message):
            responses = ["Sure, I'm all ears. Feel free to share. I'm here to listen.",
                         "I'm here and ready to listen. What would you like to tell me?"]

        elif re.search(r'\bi want to talk\b', lowercase_message):
            responses = ["Of course, I'm here to talk. What would you like to talk about?",
                         "Sure thing! I'm ready for a chat. What's on your mind?"]

        elif re.search(r'\bthat was funny\b', lowercase_message):
            responses = [
                "I'm glad you found it funny! Laughter is great. Do you want to hear another joke or talk about something else?",
                "Humor is always good! If you need more jokes or want to chat about something else, just let me know."]

        elif re.search(r'\bamazing\b', lowercase_message):
            responses = ["That's fantastic! It's always great to hear something amazing. What else can I do for you?",
                         "I'm thrilled to hear that! If you have any questions or need assistance, feel free to ask."]

        elif re.search(r'\bleave it\b', lowercase_message):
            responses = ["Alright, no problem. If there's anything else you'd like to discuss, feel free to reach out.",
                         "Sure thing! If you change your mind or have any other questions, I'll be here to assist you."]

        else:
            responses = ["I'm sorry, I didn't understand. Can you please rephrase your message?",
                         "Apologies, but I'm not sure I follow. Could you please provide more information?",
                         "I'm constantly learning and evolving. Can you provide more context or ask a different question?"]

        return random.choice(responses)

    def update_chat(self, message, sender):
        # Format the message with the sender's name
        formatted_message = f'{sender}: {message}'

        # Create a label widget for the message
        label = Label(text=formatted_message, size_hint=(1, None))

        # Set the text wrapping behavior of the label
        label.text_size = (240, None)  # Wrap text to the width of each message box

        # Create a BoxLayout to hold the label
        message_layout = BoxLayout(orientation='horizontal', size_hint=(1, None))

        # Set the alignment and color of the label based on the sender
        if sender == 'User':
            label.halign = 'left'  # Align user messages to the left
            label.color = (0, 0, 0, 1)  # Black text color for user messages
            label.font_size = 18

            # Create a spacer widget to push the label to the right side
            spacer = Widget()
            message_layout.add_widget(spacer)
            message_layout.add_widget(label)
        else:
            label.halign = 'right'  # Align chatbot messages to the right
            label.color = (0, 0, 0, 1)  # Black text color for chatbot messages
            label.font_size = 18

            message_layout.add_widget(label)
            # Create a spacer widget to push the label to the left side
            spacer = Widget()
            message_layout.add_widget(spacer)

        # Append the new message layout to the existing chat history
        self.chat_layout.add_widget(message_layout)

        # Scroll to the bottom of the chat history
        self.scroll_view.scroll_to(message_layout)

    def analyze_sentiment(self, text):
        # Create a SentimentIntensityAnalyzer object
        analyzer = SentimentIntensityAnalyzer()

        # Perform sentiment analysis using VADER
        sentiment_scores = analyzer.polarity_scores(text)
        compound_score = sentiment_scores['compound']
        subjectivity = sentiment_scores['neu']  # Use the neutral score as an approximation for subjectivity

        return compound_score, subjectivity

    def determine_mood(self, compound_score, subjectivity):
        sentiment_threshold = 0.1
        subjectivity_threshold = 0.5

        if compound_score > sentiment_threshold and subjectivity > subjectivity_threshold:
            return 'Strongly Positive and Subjective'
        elif compound_score < -sentiment_threshold and subjectivity > subjectivity_threshold:
            return 'Strongly Negative and Subjective'
        elif compound_score > sentiment_threshold and subjectivity <= subjectivity_threshold:
            return 'Positive and Objective'
        elif compound_score < -sentiment_threshold and subjectivity <= subjectivity_threshold:
            return 'Negative and Objective'
        else:
            return 'Neutral'

    def play_random_song_from_folder(self, folder_name):
        global sound

        try:
            # Get the list of files in the specified folder
            song_folder = os.path.join("C:/music", folder_name)
            song_list = os.listdir(song_folder)

            # Randomly select a file from the list
            if len(song_list) > 0:
                random_file = random.choice(song_list)
                song_path = os.path.join(song_folder, random_file)

                # Load the song
                sound = SoundLoader.load(song_path)

                # Check if the song loaded successfully
                if sound:
                    # Play the song
                    sound.play()
                    sound.state = 'play'
                    self.song_name_label.text = f'LISTENING TO: {random_file}'
                    self.song_name_label.font_size = 12
                    self.song_name_label.size_hint = (0.5, 0.1)

                else:
                    print("Error loading the song.")
            else:
                print("No songs found in the specified folder.")
        except UnicodeEncodeError:
            print("Error encoding the file path.")

    def play_music(self, instance):
        global sound
        global pause_button

        # Check if a song is already playing
        if sound and sound.state == 'play':
            sound.stop()
            sound.state = 'stop'

            self.play_button.text = 'PLAY'  # Change the text of the play button to "Play"
            self.play_button.background_color = (0, 0, 0, 1)  # Change the background color of the play button
            pause_button.disabled = True  # Disable the play button

        elif sound and sound.state == 'stop':
                # Play the song
                sound.play()
                sound.state = 'play'

                self.play_button.text = 'STOP'  # Change the text of the play button to "Play"
                self.play_button.background_color = (0, 0, 0, 1)  # Change the background color of the play button

                pause_button.disabled = False  # Disable the play button

        else:
            print("Error loading the song.")

    def pause_music(self, instance):
        global sound

        sound.stop()
        sound.state = 'stop'

        self.play_button.text = 'PLAY'  # Change the text of the play button to "Play"
        pause_button.disabled = True  # Disable the play button

    def shuffel_music(self, instance):
        global sound
        global mood

        # Play a random song based on the mood
        if mood == 'Strongly Positive and Subjective':
            # Check if a song is already playing
            if sound and sound.state == 'play':
                sound.stop()

            self.mood_label.text = f'YOU ARE CURRENTLY FEELING: HAPPY!'
            self.play_random_song_from_folder("happy")

        elif mood == 'Strongly Negative and Subjective':
            # Check if a song is already playing
            if sound and sound.state == 'play':
                sound.stop()

            self.mood_label.text = f'YOU ARE CURRENTLY FEELING: ANGRY/DEVASTATED!'
            self.play_random_song_from_folder("sad")

        elif mood == 'Positive and Objective':
            # Check if a song is already playing
            if sound and sound.state == 'play':
                sound.stop()

            self.mood_label.text = f'YOU ARE CURRENTLY FEELING: CONTENT!'
            self.play_random_song_from_folder("happy")

        elif mood == 'Negative and Objective':
            # Check if a song is already playing
            if sound and sound.state == 'play':
                sound.stop()

            self.mood_label.text = f'YOU ARE CURRENTLY FEELING: SAD!'
            self.play_random_song_from_folder("sad")

        elif mood == 'Neutral':
            self.mood_label.text = "CURRENTLY YOUR MOOD IS NEUTRAL!"

    def on_textinput(self, instance, value):
        # Check if the Enter key was pressed
        if value and value.endswith('\n'):
            # Remove the newline character
            value = value[:-1]

            # Send the message
            self.send_message(instance)

            # Clear the text input
            self.text_input.text = ''


if __name__ == '__main__':
    ChatBotApp().run()
