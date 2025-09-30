

import os
import streamlit as st
from utils.image_processor import get_category_type

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
os.environ["NVIDIA_API_KEY"] = "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"


chat_model = ChatNVIDIA(model="mistralai/mistral-7b-instruct-v0.2")
llm = chat_model | StrOutputParser()


def generate_story(object_name):
    prompt = create_prompt(object_name)
    story = generate_with_model(prompt)
    if not story or len(story) < 20:
        story = generate_fallback_story(object_name)
    return story

def create_prompt(object_name):
    system_prompt = """You are a playful and curious teacher for children aged 5-9 years old. 
Your job is to make learning fun and exciting!

Rules:
- Respond with ONE short line only
- Always start with what the object is
- Use simple words that kids understand
- Be encouraging and enthusiastic
- Include ONE fun fact
- Never use scary or complicated words"""

    user_prompt = f"""A child just took a picture of {object_name}!

Tell them something amazing about it! Include one cool fun fact

Remember: Keep it short, simple, and exciting for a young kid!"""

    return f"{system_prompt}\n\n{user_prompt}"

def generate_with_model(prompt: str) -> str:
    gen_prompt = ChatPromptTemplate.from_messages([("user", "{text}")])
    chain = gen_prompt | llm
    try:
        story = chain.invoke({"text": prompt}).strip()
        return story[:300]
    except Exception as e:
        print(f"[red]Model error: {e}")
        return None

def generate_fallback_story(object_name, category):
    """
    Generate template-based stories as fallback
    This ensures the app always works even if API fails
    """
    
    stories = {
        "animal": [
            f"Wow! You found {object_name}! Did you know {object_name}s have amazing superpowers? "
            f"They can do things we can't! Can you guess what special thing a {object_name} can do?",
            
            f"Look at that beautiful {object_name}! {object_name.title()}s are so cool! "
            f"They live in special places and eat yummy food. Where do you think this {object_name} likes to sleep?",
            
            f"Amazing! A {object_name}! These little friends are super important for our world. "
            f"What sound do you think {object_name}s make?"
        ],
        
        "plant": [
            f"You discovered {object_name}! Did you know plants make the air we breathe? "
            f"This {object_name} is like a tiny superhero! What color is your {object_name}?",
            
            f"Wow! {object_name.title()}s are amazing! They drink water and eat sunlight! "
            f"Can you find the prettiest part of this {object_name}?",
            
            f"Great find! {object_name.title()}s grow from tiny seeds into big beautiful plants! "
            f"How tall do you think this {object_name} can grow?"
        ],
        
        "food": [
            f"Yummy! You found {object_name}! This delicious food gives your body energy to run and play! "
            f"What's your favorite way to eat {object_name}?",
            
            f"Look at that tasty {object_name}! Did you know {object_name}s grow on plants? "
            f"They're full of vitamins that make you strong! What color is your {object_name}?",
            
            f"Awesome! {object_name.title()}s are super healthy! They help your body grow big and strong! "
            f"Can you think of a yummy snack you can make with {object_name}?"
        ],
        
        "toy": [
            f"Cool toy! {object_name.title()}s are so much fun to play with! "
            f"Playing helps your brain learn new things! What games can you play with your {object_name}?",
            
            f"You found {object_name}! Toys are special because they help us use our imagination! "
            f"What adventure will you go on with your {object_name} today?",
            
            f"Nice! {object_name.title()}s are awesome for creative play! "
            f"Can you build something amazing with your {object_name}?"
        ],
        
        "art": [
            f"Beautiful! You're so creative! {object_name.title()}s help us make amazing art! "
            f"Every artist needs good tools! What will you create today?",
            
            f"Wonderful {object_name}! Art is how we show the world what's in our imagination! "
            f"What colors do you see in your {object_name}?",
            
            f"Great job! Making art with {object_name}s is super fun! "
            f"Can you draw your favorite animal using your {object_name}?"
        ],
        
        "nature": [
            f"Beautiful! You found {object_name}! Nature is full of amazing surprises! "
            f"Our Earth gives us so many wonderful things! What else do you see around you?",
            
            f"Wow! {object_name.title()}s are part of our wonderful planet! "
            f"Nature is like a big outdoor classroom! How does the {object_name} make you feel?",
            
            f"Amazing discovery! {object_name.title()}s show us how incredible our world is! "
            f"What do you think makes {object_name}s so special?"
        ],
        
        "vehicle": [
            f"Vroom vroom! You found {object_name}! Vehicles help us travel to exciting places! "
            f"Where would you go if you had your own {object_name}?",
            
            f"Cool {object_name}! Did you know vehicles need energy to move, just like we need food? "
            f"How fast do you think {object_name}s can go?",
            
            f"Awesome! {object_name.title()}s are amazing machines! "
            f"What's the furthest place you'd like to travel in a {object_name}?"
        ],
        
        "object": [
            f"You found {object_name}! Everything around us has a story! "
            f"Objects help us do so many things every day! What do you use your {object_name} for?",
            
            f"Cool discovery! {object_name.title()}s are interesting! "
            f"The world is full of amazing things to explore! What else can you find today?"
        ]
    }
    
    # Get stories for this category, or use default
    category_stories = stories.get(category, stories["object"])
    
    # Pick a random story (using hash for consistency)
    import hashlib
    story_idx = int(hashlib.md5(object_name.encode()).hexdigest(), 16) % len(category_stories)
    
    return category_stories[story_idx]