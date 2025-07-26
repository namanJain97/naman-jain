import streamlit as st
import os
import re
import logging
import threading
import asyncio
from langchain.prompts import PromptTemplate
from groq import Groq

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Groq API setup
GROQ_API_KEY = "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"
if not GROQ_API_KEY:
    st.error("Groq API key not found. Please set GROQ_API_KEY in environment variables.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME = "llama-3.3-70b-versatile"


# Prompt Template with English as default
prompt = PromptTemplate(
    input_variables=["type", "tone", "length_description", "context"],
    template="""  
        **Assume, you are a professional SEO copywriter.  
        **Write a {type} about the given context in Engligh.
        **please rephrase the given text in quotes for you to use it as context for the content to be generated and do not return this in your output; "{context}".
        **while writing the content make sure to use {tone}.  
        **The length should be {length_description}.  
        **Use HTML tags (h1, h2, p, ul, li, strong) and make sure to add line breaks and paragraph breaks whereever needed.  
        **Use bullet points for lists where ever lists are required otherwise avoid lists.  
        **Keep the text persuasive, readable, and engaging.  
        **Ensure content is complete; do not leave incomplete sentences or paragraph and aim for the specified word count.  
        **If no content can be generated, return a message indicating failure.  
        **Output only the final version of your content generated on the basis of above given requirements and is ready to be uploaded as {type}. Do not return your assumptions or discussion text.
        """
)


def get_tone(tone):
    tones = {"friendly": "friendly, warm and approachable tone in your language",
                "professional": "formal, polished tone in your language",
                "funny": "humor and playful tone in your language",
                "urgent": "action-driven tone in your language with sense of urgency",
                "inspirational": "uplifting, motivational tone in your language",
                "casual": "relaxed, informal tone in your language",
                "sarcastic": "witty, ironic tone in your language",
                "formal": "structured, official tone in your language",
                "empathetic": "compassionate, understanding tone in your language",
                "authoritative": "confident, commanding tone in your language"}
    return tones[tone]


def get_content(type):
    content_guidelines = {
                "blog post": "detailed blog post using informative language and include subheadings (H2) to structure the content clearly.",
                "social media post": "short, engaging social media post using casual language and include 2-3 emojis to enhance expressiveness.",
                "YouTube script": "YouTube script with a compelling intro, clear main content, and an enthusiastic call-to-action, optimized for video delivery.",
                "newsletter": "newsletter formatted with a header, well-organized sections, and a footer, suitable for email campaigns. Use friendly yet professional language.",
                "LinkedIn post": "professional LinkedIn post using insightful language, clear messaging, and a tone suitable for a career-focused audience.",
                "product description": "description for the product with clear, benefit-driven language highlighting key features and practical advantages.",
                "landing page copy": "Write persuasive landing page copy focused on attention-grabbing headlines and clear calls-to-action. Keep the tone motivating and goal-oriented."
                }
    return content_guidelines[type]


def clean_context(context):
    # This pattern keeps only alphanumeric characters and spaces
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', context)
    return cleaned_text


# Mapping content length into word limit instructions
def get_length_description(length):
    if length == "short":
        return "around 150-200 words"
    elif length == "medium":
        return "around 300-400 words"
    elif length == "long":
        return "around 500-600 words"
    else:
        return "around 300-400 words"


# Post-process the output to ensure completeness
def post_process_output(text):
    if not text or text.strip() == "":
        return "<p>No content generated. Please try again with different settings.</p>"
    text = re.sub(r'<[^>]+$', '', text.strip())
    last_sentence_end = max(text.rfind('.'), text.rfind('?'), text.rfind('!'))
    if last_sentence_end != -1:
        text = text[:last_sentence_end + 1]
    if text.count('<p>') > text.count('</p>'):
        text += '</p>'
    clean_text = re.sub(r'<[^>]+>', '', text).strip()
    if not clean_text:
        return "<p>No content generated. Please try again with different settings.</p>"
    return text


# Function to generate copy using the Groq API
@st.cache_data(show_spinner=False)
def _generate_copy_sync(type, tone, length, context):
    length_description = get_length_description(length)
    context = clean_context(context)
    inputs = {
        "type": type,
        # "topic": topic,
        "tone": tone,
        "length_description": length_description,
        "context": context
    }
    try:
        # logger.info(f"Generating {type} for topic: {topic}, tone: {tone}, length: {length}")
        logger.info("Generating your content...")
        prompt_text = prompt.format(**inputs)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=512,
            temperature=0.5
        )
        cleaned_response = post_process_output(response.choices[0].message.content)
        logger.info("Content generated successfully")
        return cleaned_response
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return "<p>Error generating content. Please try again.</p>"


# Async wrapper for generate_copy
def generate_copy(type, tone, length, context):
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = _generate_copy_sync(type, tone, length, context)
        loop.close()
        return result

    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join()
    return _generate_copy_sync(type, tone, length, context)
