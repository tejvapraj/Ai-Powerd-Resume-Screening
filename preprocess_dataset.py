import pandas as pd
import json

# === Load CSVs ===
resume_file = 'UpdatedResumeDataSet.csv'
jd_file = 'job_descriptions.csv'

try:
    resume_df = pd.read_csv(resume_file)
    jd_df = pd.read_csv(jd_file)
except FileNotFoundError as e:
    print(f"❌ File not found: {e.filename}")
    exit()

# === Preview column names ===
print("Resume Columns:", resume_df.columns)
print("JD Columns:", jd_df.columns)

# === Adjust column names as needed ===
resume_column = 'Resume'
jd_column = 'Job Description'  # <-- corrected this


# === Drop NaNs and trim ===
resumes = resume_df[resume_column].dropna().tolist()[:100]
jds = jd_df[jd_column].dropna().tolist()[:100]

# === Clean too-short entries ===
resumes = [r for r in resumes if len(r) > 100]
jds = [jd for jd in jds if len(jd) > 100]

# === Pair and create mock dataset ===
min_len = min(len(resumes), len(jds), 50)
mock_data = []

for i in range(min_len):
    mock_data.append({
        'resume_text': resumes[i],
        'job_description': jds[i],
        'label': 1  # Assume matched for initial testing
    })

# === Save to JSON ===
with open('small_resume_jd_dataset.json', 'w', encoding='utf-8') as f:
    json.dump(mock_data, f, indent=2)

print(f"✅ Dataset saved with {len(mock_data)} pairs.")
