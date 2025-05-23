from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rank_resumes(job_desc, resumes):
    """
    Ranks resumes based on their similarity to the job or candidate description using TF-IDF and cosine similarity.

    Args:
        job_desc (str): The job or candidate description text.
        resumes (list of str): A list of resume texts.

    Returns:
        list of float: A list of similarity scores for each resume.
    """
    if not isinstance(job_desc, str) or not job_desc.strip():
        raise ValueError("Job/candidate description cannot be empty.")
    if not resumes or not all(isinstance(r, str) and r.strip() for r in resumes):
        raise ValueError("Resumes list cannot be empty and must contain text.")

    # Combine job description and resumes into a single list for TF-IDF processing
    documents = [job_desc] + resumes

    # Initialize the TF-IDF vectorizer
    tfidf = TfidfVectorizer()

    # Transform the documents into a TF-IDF matrix
    tfidf_matrix = tfidf.fit_transform(documents)

    # Compute cosine similarity between the job description and each resume
    scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    return scores.tolist()