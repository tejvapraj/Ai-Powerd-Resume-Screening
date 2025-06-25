import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score, f1_score

# Load SBERT model once
model = SentenceTransformer('all-MiniLM-L6-v2')


def compare_resumes(resume1, resume2, job_desc, model, threshold=0.05):
    """
    Compare two resumes against a job description and return which one is a better match.
    """
    emb = model.encode([resume1, resume2, job_desc])
    score1 = cosine_similarity([emb[0]], [emb[2]])[0][0]
    score2 = cosine_similarity([emb[1]], [emb[2]])[0][0]

    print(f"\n🔍 Resume 1 score: {score1:.3f}")
    print(f"🔍 Resume 2 score: {score2:.3f}")

    better = "Resume 1" if score1 > score2 else "Resume 2"
    print(f"✅ Better match: {better}")

    match1 = score1 > threshold
    match2 = score2 > threshold

    return better, match1, match2


def evaluate_dataset(model, data_path, threshold=0.05, debug=False):
    """
    Evaluate the SBERT model on a labeled dataset.
    """
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    y_true = []
    y_pred = []

    print("📊 Evaluating dataset...\n")

    for sample in data:
        resume = sample['resume_text']
        jd = sample['job_description']
        true_label = int(sample['label'])

        embeddings = model.encode([resume, jd])
        score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        predicted_label = 1 if score > threshold else 0

        y_true.append(true_label)
        y_pred.append(predicted_label)

        print(f"Similarity Score: {score:.3f}, Predicted Label: {predicted_label}, True Label: {true_label}")

        if debug and score < threshold and true_label == 1:
            print("\n⚠️ Low score but labeled as match:")
            print("Resume Snippet:", resume[:200].replace("\n", " "), "...")
            print("JD Snippet:", jd[:200].replace("\n", " "), "...\n")

    # Calculate metrics
    accuracy = sum([yt == yp for yt, yp in zip(y_true, y_pred)]) / len(y_true)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print(f"\n✅ Accuracy on test set with threshold {threshold}: {accuracy:.2f}")
    print(f"🎯 Precision: {precision:.2f}")
    print(f"🔁 Recall:    {recall:.2f}")
    print(f"📊 F1 Score:  {f1:.2f}")


if __name__ == "__main__":
    # Evaluate on dataset
    evaluate_dataset(model, 'cleaned_resume_jd_dataset.json', threshold=0.05, debug=True)

    # Optional sample test
    sample_resume1 = "Experienced Python developer with knowledge of machine learning and web development."
    sample_resume2 = "Graduate with project experience in AI-based resume screening systems and front-end development."
    sample_jd = "Looking for a front-end developer with experience in React and good understanding of machine learning."

    compare_resumes(sample_resume1, sample_resume2, sample_jd, model, threshold=0.05)
