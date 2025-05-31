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
    input_variables=["type", "topic", "tone", "length_description"],
    template="""  
You are a professional SEO copywriter.  

Write a {type} about "{topic}" in a {tone} tone in English.  
The length should be {length_description}.  

### Tone-specific instructions:
- If the tone is "friendly", use warm, approachable language.
- If the tone is "professional", use formal, polished language.
- If the tone is "funny", use humor and playful language.
- If the tone is "urgent", use action-driven language with immediacy.
- If the tone is "inspirational", use uplifting, motivational language.
- If the tone is "casual", use relaxed, informal language.
- If the tone is "sarcastic", use witty, ironic language.
- If the tone is "formal", use structured, official language.
- If the tone is "empathetic", use compassionate, understanding language.
- If the tone is "authoritative", use confident, commanding language.

### Formatting rules:  
- Use HTML tags (h1, h2, p, ul, li, strong).  
- Add line breaks and paragraph breaks where needed.  
- Use bullet points for lists.  
- Keep the text persuasive, readable, and engaging.  

### Content rules:  
- For blog posts, include subheadings (h2).  
- For social media posts, add 2-3 emojis.  
- For YouTube scripts, structure with an intro, main content, and call-to-action, optimized for video.  
- For newsletters, format with a header, sections, and footer, suitable for email campaigns.  
- For LinkedIn posts, use a professional tone with a clear message or insight.  
- For product descriptions, highlight key features and benefits.  
- For landing page copy, focus on persuasive headlines and clear calls-to-action.  
- Ensure content is complete; do not stop mid-sentence or mid-paragraph.  
- Aim for the specified word count but prioritize completing the last sentence.  
- If no content can be generated, return a message indicating failure.  

Output only the final copy in English.  
"""
)

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
def _generate_copy_sync(type, topic, tone, length):
    length_description = get_length_description(length)
    inputs = {
        "type": type,
        "topic": topic,
        "tone": tone,
        "length_description": length_description
    }
    try:
        logger.info(f"Generating content for topic: {topic}, tone: {tone}, length: {length}")
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
def generate_copy(type, topic, tone, length):
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = _generate_copy_sync(type, topic, tone, length)
        loop.close()
        return result

    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join()
    return _generate_copy_sync(type, topic, tone, length)
