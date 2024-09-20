import os
import openai
import discord
from dotenv import load_dotenv
import asyncio
import csv

# Load environment variables from a .env file (Discord Token, OpenAI Key, etc.)
load_dotenv()

# Retrieve the bot's Discord token and OpenAI API key from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')

# Specify the user ID of the target user (whose messages you want to collect)
user_id =   # Change this to the user ID of the target user

# Specify the channel ID where the bot will look for messages
channel_id =   # The Discord channel you want the bot to interact with

# Set the OpenAI API key
openai.api_key = OPENAI_KEY

# Set up Discord bot intents to listen to events like messages
intents = discord.Intents.all()

# Create a Discord client instance with intents
client = discord.Client(command_prefix='!', intents=intents)
channel = None

# Open and read the chat logs from a CSV file
with open("chatcomp.csv", "r") as file:
    reader = csv.reader(file)
    rows = list(reader)

# Compress chat logs into a string
compressed = str(rows)

# Instructions for the OpenAI model (the system message)
instructions = ("You are (intended user). The following are many messages, use the ones "
                "associated with (intended user) to try and match his speech patterns when "
                "responding to messages. keep in mind his interests and things he's been up to: " 
                + compressed)

# Event handler for when the bot is ready and logged into Discord
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))  # Confirm the bot has logged in
    channel = client.get_channel(# Channel ID)  # Get the channel by ID
    print(channel)  # Print the channel info to confirm
    return channel

# Function to get messages from a specific user (based on user_id) in a channel
async def get_messages(user_id, channel):
    messages = []  # List to store the messages
    async for message in channel.history(limit=200):  # Retrieve the last 200 messages in the channel
        if message.author.id == user_id:  # If the message is from the target user
            messages.append(message.content)  # Add the message to the list
    return messages

# Event handler for new messages
@client.event
async def on_message(message):
    if message.author == client.user:  # Ignore the bot's own messages
        return
    if client.user in message.mentions:  # If the bot is mentioned in a message
        # Generate a response from OpenAI's GPT model using the instructions and the user's message
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": instructions},  # System message with instructions
                {"role": "user", "content": f"{message.content}"},  # User's message content
            ],
        )
        # Send the AI-generated response in the same channel
        await message.channel.send(response['choices'][0]['message']['content'])

# Start the bot using the Discord token
client.run(TOKEN)

# Run the get_messages function to retrieve messages from the target user
messages = asyncio.run(get_messages(user_id, channel))

# Write the collected messages to a text file
with open("messages.txt", "w") as f:
    f.write("\n".join(messages))
