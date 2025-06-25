import json
import re

def clean_text(text):
    # Replace line breaks with space
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    
    # Remove non-ASCII characters (weird unicode)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove phone numbers (simple pattern)
    text = re.sub(r'\b\d{10,15}\b', '', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading and trailing spaces
    return text.strip()

# Load your JSON file
with open('small_resume_jd_dataset.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Clean resume_text and job_description fields
for item in data:
    item['resume_text'] = clean_text(item['resume_text'])
    item['job_description'] = clean_text(item['job_description'])

# Save cleaned data to a new JSON file
with open('cleaned_resume_jd_dataset.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print("Cleaning done! Saved as cleaned_resume_jd_dataset.json")

