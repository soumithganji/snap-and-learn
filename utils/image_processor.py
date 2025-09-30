import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import streamlit as st

# Cache the model to avoid reloading
@st.cache_resource
def load_clip_model():
    """Load CLIP model and processor"""
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return model, processor

# Kid-friendly categories
KID_CATEGORIES = [
    "a butterfly",
    "a bird",
    "a dog",
    "a cat",
    "a fish",
    "an insect",
    "a rabbit",
    "a bear",
    "a flower",
    "a tree",
    "a leaf",
    "a plant",
    "grass",
    "an apple",
    "a banana",
    "an orange",
    "a strawberry",
    "vegetables",
    "a carrot",
    "broccoli",
    "a toy car",
    "a doll",
    "a ball",
    "building blocks",
    "a teddy bear",
    "a robot",
    "a puzzle",
    "a book",
    "crayons",
    "a pencil",
    "a painting",
    "a drawing",
    "colored pencils",
    "a rainbow",
    "the sun",
    "the moon",
    "clouds",
    "stars",
    "a rock",
    "sand",
    "water",
    "a bicycle",
    "a car",
    "a train",
    "an airplane",
    "a boat",
    "a house",
    "a castle",
    "a mountain",
    "the ocean",
    "a beach"
]

def classify_image(image):
    """
    Classify an image using CLIP model
    
    Args:
        image: PIL Image object
    
    Returns:
        tuple: (object_name, confidence_score)
    """
    # Load model
    model, processor = load_clip_model()
    
    # Prepare inputs
    inputs = processor(
        text=KID_CATEGORIES,
        images=image,
        return_tensors="pt",
        padding=True
    )
    
    # Get predictions
    with torch.no_grad():
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)
    
    # Get top prediction
    confidence, idx = probs[0].max(0)
    object_name = KID_CATEGORIES[idx.item()].replace("a ", "").replace("an ", "")
    
    return object_name, confidence.item()

def get_category_type(object_name):
    """
    Categorize the object into broader categories for story generation
    
    Args:
        object_name: string name of detected object
    
    Returns:
        string: category type (animal, plant, food, toy, nature, vehicle)
    """
    animals = ["butterfly", "bird", "dog", "cat", "fish", "insect", "rabbit", "bear"]
    plants = ["flower", "tree", "leaf", "plant", "grass"]
    food = ["apple", "banana", "orange", "strawberry", "vegetables", "carrot", "broccoli"]
    toys = ["toy car", "doll", "ball", "building blocks", "teddy bear", "robot", "puzzle"]
    art = ["book", "crayons", "pencil", "painting", "drawing", "colored pencils"]
    nature = ["rainbow", "sun", "moon", "clouds", "stars", "rock", "sand", "water", "mountain", "ocean", "beach"]
    vehicles = ["bicycle", "car", "train", "airplane", "boat"]
    
    object_lower = object_name.lower()
    
    for animal in animals:
        if animal in object_lower:
            return "animal"
    
    for plant in plants:
        if plant in object_lower:
            return "plant"
    
    for f in food:
        if f in object_lower:
            return "food"
    
    for toy in toys:
        if toy in object_lower:
            return "toy"
    
    for a in art:
        if a in object_lower:
            return "art"
    
    for n in nature:
        if n in object_lower:
            return "nature"
    
    for v in vehicles:
        if v in object_lower:
            return "vehicle"
    
    return "object"