import requests
import os

API = "http://127.0.0.1:5000"

def test_health():
    res = requests.get(API + "/")
    print("Health Check:", res.json())

def test_analyze():
    # Test text analyze
    payload = {"text": "The indemnification clause shall be robust and comprehensive for the employer. Notwithstanding any contrary provisions, this agreement is complex."}
    res = requests.post(API + "/api/analyze", json=payload)
    data = res.json()
    print("Readability Score (FK):", data['readability']['flesch_kincaid_grade'])
    print("Complexity Label:", data['complexity_label'])
    print("Word Count:", data['word_count'])
    if 'cleaned_text' in data:
        print("✅ Cleaned text returned.")
    if 'sentence_tokens' in data and len(data['sentence_tokens']) > 0:
        print(f"✅ Sentence tokens returned: {len(data['sentence_tokens'])} sentences.")

def test_file_upload():
    # Create a dummy file
    with open("test.txt", "w") as f:
        f.write("This is a test file to verify persistence on the windows system.")
    
    with open("test.txt", "rb") as f:
        files = {'file': f}
        res = requests.post(API + "/api/analyze", files=files)
    
    data = res.json()
    print("File Upload Status:", data.get('file_saved'))
    print("Saved Filename:", data.get('saved_filename'))
    
    # Verify file exists on disk
    upload_path = os.path.join("backend", "uploads", data.get('saved_filename'))
    if os.path.exists(upload_path):
        print("✅ File verified on disk at:", upload_path)
    else:
        print("❌ File NOT found on disk at:", upload_path)
    
    try:
        os.remove("test.txt")
    except:
        pass

if __name__ == "__main__":
    try:
        test_health()
        test_analyze()
        test_file_upload()
    except Exception as e:
        print("Verification failed:", e)
