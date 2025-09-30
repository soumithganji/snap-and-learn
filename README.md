# Snap & Learn 📸

**Snap & Learn** is an interactive educational web application designed to make learning playful, personalized, and exploratory for children aged 5–9. It combines computer vision, natural language processing, and text-to-speech technologies, all while providing parents with a minimal dashboard to track their child’s discoveries.

---

## **Demo**
- Children can upload a photo or doodle of anything around them — a toy, plant, animal, or drawing.
- The system recognizes the object and generates:
  - A **short, age-appropriate line** about it
  - **Interactive voice playback** of the story
- Parents can track what their child has discovered through the **Parent Dashboard**.

**Try the live demo here:** [Snap & Learn Web App](https://snap-and-learn.streamlit.app)

---

## **Technologies Used**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend / UI** | Streamlit | Rapid prototyping of web interface with interactive widgets, columns, and file upload support. |
| **Image Captioning** | BLIP (Salesforce BLIP-Image-Captioning-Base) | Converts uploaded images to natural language captions for downstream processing. |
| **Image Classification** | CLIP (OpenAI CLIP-ViT-Base-Patch32) | Maps captions and candidate prompts to likely objects using zero-shot classification. |
| **NLP / Knowledge Expansion** | NLTK (tokenization, POS tagging, WordNet) | Extracts nouns from captions and expands them using hyponyms, hypernyms, and synonyms to improve recognition accuracy. |
| **Story Generation** | LangChain + ChatNVIDIA (Mistral 7B Instruct) | Generates age-appropriate, playful stories using LLMs with a prompt template designed specifically for young children. |
| **Text-to-Speech** | gTTS (Google TTS) | Converts the generated stories into voice for interactive audio playback. |
| **Data Storage** | JSON (Parent Log) | Keeps a minimal record of child interactions (object detected, confidence, timestamp, story) for parental insights. |
| **Deployment / Infra** | Local or Cloud (Streamlit-compatible) | Modular backend, easy to deploy incrementally; can scale to Azure/GCP if needed. |

---

## **Project Structure**
```
snap-and-learn/
├── app.py                     # Main Streamlit app: UI, file uploads, audio playback, dashboard
├── requirements.txt           # All dependencies for reproducibility
├── utils/                     # Helper modules
│   ├── __init__.py
│   ├── image_processor.py     # Image captioning, noun extraction, CLIP classification
│   ├── story_generator.py     # Story generation via LLM + fallback templates
│   └── voice_generator.py     # Text-to-speech conversion and audio management
├── data/                      # Parent log JSON storage
└── audio/                     # Generated voice files
```

---

## **Module Overview & Technical Decisions**

### **1. `app.py`**
- Handles the **web interface** using Streamlit.
- Child interaction: image upload, text display, and voice playback.
- Parent dashboard: tracks learning sessions.
- **Design choice:** Streamlit allows rapid iteration and prototyping while maintaining a polished interface, essential for a basic demo.


### **2. `utils/image_processor.py`**
- **Purpose:** Converts uploaded images to structured object predictions.
- **Workflow:**
  1. **Captioning:** Uses BLIP to convert images to text.
  2. **Noun Extraction:** Tokenizes captions and extracts nouns via NLTK POS tagging.
  3. **Candidate Expansion:** Uses WordNet to include synonyms, hypernyms, and hyponyms to improve recognition.
  4. **Zero-shot Classification:** CLIP matches prompts derived from candidate labels to the image.(slow inference due to CLIPProcessor, streamlit doe supporting fast processor)
  5. Returns top object.

### **3. `utils/story_generator.py`**
- **Purpose:** Converts recognized objects into short, age-appropriate information.
- **Technical Details:**
  - Uses **LangChain** + **ChatNVIDIA** LLM pipeline with a **playful prompt template**.
  - **Fallback mechanism:** If LLM fails, selects story templates based on object category.
- **Why implemented this way:**
  - Guarantees that every interaction produces a story.
  - Demonstrates ability to integrate cutting-edge LLMs and maintain resiliency.

### **4. `utils/voice_generator.py`**
- **Purpose:** Converts story text into audio for interactive playback.
- **Technical Details:**
  - Uses **gTTS** (Google Text-to-Speech).


### **5. `data/` and `audio/`**
- **Parent Log:** Tracks object detected, timestamp, and generated information.
- **Audio:** Stores generated voice files with caching + cleanup logic to optimize storage.


---

## **How to Run**
1. **Clone repo**:
```bash
git clone <https://github.com/soumithganji/snap-and-learn>
cd snap-and-learn
```
2. **Install dependencies**:
```bash
pip install -r requirements.txt
```
3. **Run Streamlit app**:
```bash
streamlit run app.py
```

