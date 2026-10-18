import os
from flask import Flask, render_template, request, session
from werkzeug.utils import secure_filename
from services.parser import extract_text, parse_resume
from services.matcher import compare
from services.resume_insights import inspect_resume

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(32)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    uploaded = request.files.get('resume')
    jd = request.form.get('job_description', '').strip()
    if not uploaded or not uploaded.filename or not jd:
        return render_template('index.html', error='Upload a resume and enter a job description.'), 400
    filename = secure_filename(uploaded.filename)
    if not filename.lower().endswith(('.pdf', '.docx')):
        return render_template('index.html', error='Only PDF and DOCX files are accepted.'), 400
    try:
        content = uploaded.read()
        if not content:
            raise ValueError('Empty file')
        text = extract_text(filename, content)
        if not text.strip():
            raise ValueError('No selectable text found')
        candidate = parse_resume(text)
        result = compare(text, jd)
        insights = inspect_resume(text, result)
        previous = session.get('last_analysis')
        current = {'filename': filename, 'overall': float(result.get('overall') or 0), 'semantic': float(result.get('semantic') or 0), 'skill_score': result.get('skill_score')}
        session['last_analysis'] = current
        return render_template('dashboard.html', candidate=candidate, result=result, insights=insights, resume_text=text, jd=jd, previous=previous, filename=filename)
    except Exception:
        app.logger.exception('Resume processing failed')
        return render_template('index.html', error='Could not process the resume. Use a valid text-based PDF or DOCX.'), 400

@app.errorhandler(413)
def too_large(error):
    return render_template('index.html', error='File exceeds 5 MB.'), 413

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1')
