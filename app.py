from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from resume_utils import extract_resume_text, clean_text

try:
    from ranking import rank_resumes
except ImportError as e:
    raise ImportError(
        "The 'ranking' module could not be found. Ensure 'ranking.py' exists in the same directory as 'app.py'."
    ) from e

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Needed for flash messages

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_desc = request.form.get('job_desc', '')
        resume_files = request.files.getlist('resumes')
        if not job_desc.strip() or not resume_files or resume_files[0].filename == '':
            flash('Please provide a job description and at least one resume file.')
            return redirect(request.url)

        resume_texts = []
        filenames = []
        for file in resume_files:
            if not allowed_file(file.filename):
                flash(f"File '{file.filename}' is not a supported format (PDF, DOC, DOCX).")
                return redirect(request.url)
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            try:
                text = extract_resume_text(path)
                cleaned_text_val = clean_text(text)
            except Exception as e:
                flash(f"Could not process '{filename}': {str(e)}")
                return redirect(request.url)
            if not cleaned_text_val.strip():
                flash(f"The uploaded file '{filename}' could not be read or is empty. Please upload a valid text-based or scanned PDF, DOC, or DOCX file.")
                return redirect(request.url)
            resume_texts.append(cleaned_text_val)
            filenames.append(filename)

        cleaned_job_desc = clean_text(job_desc)
        try:
            scores = rank_resumes(cleaned_job_desc, resume_texts)
        except Exception as e:
            flash(f"Ranking failed: {str(e)}")
            return redirect(request.url)
        ranked = sorted(zip(filenames, scores), key=lambda x: x[1], reverse=True)
        return render_template('results.html', ranked=ranked, enumerate=enumerate)

    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    description = request.form.get('description', '')
    resume_file = request.files.get('resume')
    if not description.strip():
        flash('Please provide a candidate description.')
        return redirect(url_for('index'))
    if not resume_file or resume_file.filename == '':
        flash('Please upload a resume file.')
        return redirect(url_for('index'))
    if not allowed_file(resume_file.filename):
        flash("Uploaded file is not a supported format (PDF, DOC, DOCX).")
        return redirect(url_for('index'))

    filename = secure_filename(resume_file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume_file.save(path)
    try:
        text = extract_resume_text(path)
        cleaned_resume = clean_text(text)
    except Exception as e:
        flash(f"Could not process '{filename}': {str(e)}")
        return redirect(url_for('index'))
    cleaned_desc = clean_text(description)
    if not cleaned_resume.strip():
        flash("The uploaded resume file could not be read or is empty. Please upload a valid text-based or scanned PDF, DOC, or DOCX file.")
        return redirect(url_for('index'))
    try:
        score = rank_resumes(cleaned_desc, [cleaned_resume])[0]
    except Exception as e:
        flash(f"Ranking failed: {str(e)}")
        return redirect(url_for('index'))
    ranked = [(filename, score)]
    return render_template('results.html', ranked=ranked, enumerate=enumerate)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)