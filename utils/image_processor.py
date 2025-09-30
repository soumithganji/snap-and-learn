import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from transformers import BlipProcessor, BlipForConditionalGeneration
import streamlit as st
import nltk
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("averaged_perceptron_tagger")
nltk.download('averaged_perceptron_tagger_eng')
nltk.download("wordnet")
nltk.download("omw-1.4")
from nltk.corpus import wordnet as wn
from nltk import word_tokenize, pos_tag
import re

device = "cuda" if torch.cuda.is_available() else "cpu"


@st.cache_resource
def load_clip_model():
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return model, processor

@st.cache_resource
def load_caption_model():
    # BLIP captioning model
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base", use_fast=True)
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
    return model, processor


def ensure_nltk():
    nltk_data = ["punkt", "averaged_perceptron_tagger", "wordnet", "omw-1.4"]
    for pkg in nltk_data:
        try:
            nltk.data.find(pkg)
        except LookupError:
            nltk.download(pkg, quiet=True)

ensure_nltk()


def caption_image(image: Image.Image, max_length: int = 40) -> str:
    blip_model, blip_processor = load_caption_model()
    inputs = blip_processor(images=image, return_tensors="pt").to(device)
    generated_ids = blip_model.generate(**inputs, max_length=max_length)
    caption = blip_processor.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    caption = caption.strip().lower()
    return caption


def extract_nouns(text: str):
    tokens = word_tokenize(text)
    tags = pos_tag(tokens)
    nouns = [w for w, t in tags if t.startswith("NN")]
    nouns = [re.sub(r'[^a-z0-9\s\-]', '', n).strip() for n in nouns if n.strip()]
    return list(dict.fromkeys(nouns))

def expand_candidates_with_wordnet(nouns, max_per_noun=20):
    candidates = set()
    for noun in nouns:
        noun = noun.lower()
        candidates.add(noun)
        synsets = wn.synsets(noun, pos=wn.NOUN)
        for s in synsets[:3]:
            for l in s.lemmas()[:6]:
                candidates.add(l.name().replace("_", " ").lower())
            for hy in s.hyponyms()[:6]:
                for l in hy.lemmas()[:6]:
                    candidates.add(l.name().replace("_", " ").lower())
            for hypr in s.hypernyms()[:3]:
                for l in hypr.lemmas()[:4]:
                    candidates.add(l.name().replace("_", " ").lower())
    cleaned = []
    for c in candidates:
        if 1 < len(c) <= 40 and re.match(r'^[a-z0-9 \-]+$', c):
            cleaned.append(c)
        if len(cleaned) >= max_per_noun * max(1, len(nouns)):
            break
    return list(dict.fromkeys(cleaned))


PROMPT_TEMPLATES = [
    "a photo of a {}",
    "a picture of a {}",
    "a drawing of a {}",
    "a toy {}",
    "an illustration of a {}",
    "a {} on a table",
]

def build_prompts_for_labels(labels):
    prompts = []
    mapping = []
    for lbl in labels:
        for t in PROMPT_TEMPLATES:
            prompts.append(t.format(lbl))
            mapping.append(lbl)
    return prompts, mapping

@st.cache_resource
def get_clip_models_for_device():
    model, processor = load_clip_model()
    return model, processor

def classify_image(image, top_k=3):
    caption = caption_image(image)
    nouns = extract_nouns(caption)
    if not nouns:
        tokens = [w for w in re.findall(r'\w+', caption) if len(w) > 2]
        nouns = tokens[:3]

    labels = expand_candidates_with_wordnet(nouns, max_per_noun=12)
    if not labels:
        labels = nouns or ["object"]

    prompts, mapping = build_prompts_for_labels(labels)
   
    clip_model, clip_processor = get_clip_models_for_device()
    inputs = clip_processor(text=prompts, images=image, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        outputs = clip_model(**inputs)
        logits_per_image = outputs.logits_per_image 
        probs = logits_per_image.softmax(dim=1) 
    probs = probs[0].cpu() 


    from collections import defaultdict
    label_scores = defaultdict(list)
    for i, lbl in enumerate(mapping):
        label_scores[lbl].append(probs[i].item())


    aggregated = [(lbl, sum(scores) / len(scores)) for lbl, scores in label_scores.items()]

    aggregated.sort(key=lambda x: x[1], reverse=True)


    top = aggregated[:top_k]

    object_name, confidence = aggregated[0]
    print(aggregated)
    print(aggregated[0])
    
    return object_name, confidence



def get_category_type(label):
    synsets = wn.synsets(label, pos=wn.NOUN)
    keywords = {"animal", "plant", "food", "vehicle", "toy", "person", "furniture", "electronics"}

    checked = set()
    for s in synsets[:4]:
        queue = [s]
        depth = 0
        while queue and depth < 6:
            next_q = []
            for q in queue:
                for h in q.hypernyms():
                    for l in h.lemmas()[:4]:
                        checked.add(l.name().lower().replace("_", " "))
                    next_q.append(h)
            queue = next_q
            depth += 1

    if any(k in checked for k in ("animal", "fauna")):
        return "animal"
    if any(k in checked for k in ("plant", "flora", "vegetable", "tree", "flower")):
        return "plant"
    if any(k in checked for k in ("food", "foodstuff", "edible")):
        return "food"
    if any(k in checked for k in ("vehicle", "conveyance", "car", "airplane", "ship")):
        return "vehicle"
    if any(k in checked for k in ("toy", "plaything")):
        return "toy"
    if any(k in checked for k in ("instrumentality", "artifact", "device", "electronics")):
        return "object"
    return "object"