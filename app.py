from flask import Flask, request, render_template, send_file
from question_generator import generate_questions
import os
import io

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def extract_text(file_path):
    """Extract text safely from TXT, PDF, or DOCX without encoding errors."""
    
    ext = file_path.split('.')[-1].lower()
    text = ""

    if ext == "txt":
        # Try UTF-8 first, fallback to Windows-1252
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="windows-1252", errors="ignore") as f:
                text = f.read()

    elif ext == "pdf":
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

    elif ext == "docx":
        import docx
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text


@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        uploaded_file = request.files.get("syllabus_file")
        q_type = request.form.get("q_type")
        difficulty = request.form.get("difficulty")
        num = int(request.form.get("num", 5))
        show_answers = request.form.get("show_answers") == "on"

        if uploaded_file and uploaded_file.filename != "":
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(file_path)

            syllabus_text = extract_text(file_path)

            result = generate_questions(
                syllabus_text,
                q_type=q_type,
                num=num,
                difficulty=difficulty,
                show_answers=show_answers
            )
        else:
            result = "Please upload a syllabus or notes file."

        with open("latest_questions.txt", "w", encoding="utf-8") as f:
            f.write(result)

    return render_template("index.html", result=result)


@app.route("/download_pdf")
def download_pdf():
    if not os.path.exists("latest_questions.txt"):
        return "No questions generated yet!", 400

    with open("latest_questions.txt", "r", encoding="utf-8") as f:
        content = f.read()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    lines = content.split("\n")
    y = height - 40

    for line in lines:
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line)
        y -= 20

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="question_paper.pdf", mimetype="application/pdf")


if __name__ == "__main__":
    app.run(debug=True)
