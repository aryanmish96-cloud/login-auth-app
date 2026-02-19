import io
import re
import nltk
import spacy
import textstat
from PyPDF2 import PdfReader

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('cmudict', quiet=True) # For better syllable counting if needed

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None

def extract_text_from_pdf(pdf_bytes):
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def clean_text(text):
    if not text:
        return ""
    
    # 1. Remove non-printable characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
    
    # 2. Remove common PDF noise like "____" or "****" or "...."
    text = re.sub(r'[_.*]{3,}', ' ', text)
    
    # 3. Handle line-break hyphens (fragword - at end of line)
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # 4. Normalize quotes and common special chars
    text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    
    # 5. Normalize whitespace first to simplify further regex
    text = re.sub(r'\s+', ' ', text)
    
    # 6. Filter out "garbage" lone characters (e.g., page 1 of 5 -> 1 of 5 is fine, but s t r a y chars aren't)
    # This regex looks for single characters that aren't 'a', 'i', 'A', 'I' or numbers
    # and are surrounded by spaces
    text = re.sub(r'(^| )[^aAiI0-9 ]( |$)', ' ', text)
    
    # Final trim and whitespace normalization
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_word_complexity(word):
    if not word or not word.strip():
        return "simple"
    
    # Remove punctuation for analysis
    clean_word = re.sub(r'[^\w\s]', '', word).lower()
    if not clean_word:
        return "simple"
    
    syllables = textstat.syllable_count(clean_word)
    
    if syllables >= 4 or textstat.is_difficult_word(clean_word):
        return "complex"  # Red
    elif syllables == 3:
        return "normal"   # Yellow
    else:
        return "simple"   # Green

def analyze_readability(text):
    if not text:
        return {}
    
    cleaned = clean_text(text)
    
    # Check if spaCy is available
    if nlp is None:
        # Fallback to NLTK
        sentences = nltk.sent_tokenize(cleaned)
        words = nltk.word_tokenize(cleaned)
        word_analysis = []
        word_count = 0
        
        for w in words:
            if re.search(r'\w', w):
                word_count += 1
                word_analysis.append({"text": w + " ", "complexity": get_word_complexity(w), "pos": "N/A"})
            else:
                word_analysis.append({"text": w + " ", "complexity": "none", "pos": "N/A"})
        
        sentence_count = len(sentences)
    else:
        # Use spaCy for robust analysis
        doc = nlp(cleaned)
        word_analysis = []
        word_count = 0
        sentence_count = len(list(doc.sents))
        
        for token in doc:
            if token.is_alpha:
                word_count += 1
                complexity = get_word_complexity(token.text)
                # Promote to normal if long and important POS
                if complexity == "simple" and len(token.text) > 8 and token.pos_ in ["NOUN", "VERB", "ADJ"]:
                    complexity = "normal"
                word_analysis.append({"text": token.text_with_ws, "complexity": complexity, "pos": token.pos_})
            else:
                word_analysis.append({"text": token.text_with_ws, "complexity": "none", "pos": token.pos_})

    # Scores using textstat
    fk_grade = textstat.flesch_kincaid_grade(cleaned)
    gf_index = textstat.gunning_fog(cleaned)
    ease = textstat.flesch_reading_ease(cleaned)

    # Extract tokens for display
    if nlp is not None:
        doc = nlp(cleaned)
        sentence_tokens = [s.text for s in doc.sents]
        word_tokens = [t.text for t in doc if not t.is_punct and not t.is_space]
    else:
        sentence_tokens = nltk.sent_tokenize(cleaned)
        word_tokens = [w for w in nltk.word_tokenize(cleaned) if re.search(r'\w', w)]

    # Complexity label
    if fk_grade > 14:
        label = "Very Complex (Legal/Academic)"
    elif fk_grade > 10:
        label = "Complex (Professional)"
    elif fk_grade > 7:
        label = "Normal (Clear)"
    else:
        label = "Simple (Conversational)"

    return {
        "readability": {
            "flesch_kincaid_grade": fk_grade,
            "gunning_fog": gf_index,
            "flesch_reading_ease": ease
        },
        "word_analysis": word_analysis,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "complexity_label": label,
        "cleaned_text": cleaned,
        "sentence_tokens": sentence_tokens,
        "word_tokens": word_tokens
    }

def get_complexity_label(grade_level):
    if grade_level <= 6:
        return "Low (Easy to read)"
    elif grade_level <= 12:
        return "Medium (High School level)"
    else:
        return "High (College/Professional level)"
