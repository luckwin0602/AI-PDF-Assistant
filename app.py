import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from groq import Groq
from pypdf import PdfReader
from werkzeug.utils import secure_filename

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

conversation_memory = []

pdf_text = ""
pdf_filename = ""

CHAT_SYSTEM_PROMPT = "You are a helpful AI Assistant."

PDF_SYSTEM_PROMPT = (
    "You answer ONLY from the uploaded PDF. "
    "If the answer does not exist inside the PDF, "
    "say: I couldn't find this information in the uploaded PDF."
)


def get_groq_client():
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY is missing. Add it in your .env file.")
    return Groq(api_key=GROQ_API_KEY)


def extract_pdf_text(file_path):
    reader = PdfReader(str(file_path))
    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())

    return "\n\n".join(pages)


def ask_groq(user_message, use_pdf=False):
    client = get_groq_client()

    if use_pdf and pdf_text:

        messages = [
            {
                "role": "system",
                "content": PDF_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"PDF Content:\n{pdf_text[:12000]}\n\nStudent Question: {user_message}",
            },
        ]

    else:

        messages = [
            {
                "role": "system",
                "content": CHAT_SYSTEM_PROMPT,
            }
        ]

        for item in conversation_memory[-10:]:
            messages.append(
                {
                    "role": item["role"],
                    "content": item["content"],
                }
            )

        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content.strip()

    if not use_pdf:
        conversation_memory.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        conversation_memory.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    return answer


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    global pdf_text, pdf_filename

    try:

        if "file" not in request.files:
            return jsonify(
                {
                    "success": False,
                    "error": "No file uploaded.",
                }
            ), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify(
                {
                    "success": False,
                    "error": "No file selected.",
                }
            ), 400

        if not file.filename.lower().endswith(".pdf"):
            return jsonify(
                {
                    "success": False,
                    "error": "Only PDF files are allowed.",
                }
            ), 400

        filename = secure_filename(file.filename)

        save_path = UPLOAD_FOLDER / filename

        file.save(save_path)

        pdf_text = extract_pdf_text(save_path)
        pdf_filename = filename

        if not pdf_text.strip():
            return jsonify(
                {
                    "success": False,
                    "error": "Could not extract text from this PDF.",
                }
            ), 400

        return jsonify(
            {
                "success": True,
                "filename": filename,
                "message": f"PDF '{filename}' uploaded successfully. You can now ask questions about it.",
                "char_count": len(pdf_text),
            }
        )

    except Exception as error:
        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 500


@app.route("/chat", methods=["POST"])
def chat():
    try:

        data = request.get_json(silent=True) or {}

        message = (data.get("message") or "").strip()

        if not message:
            return jsonify(
                {
                    "success": False,
                    "error": "Message is required.",
                }
            ), 400

        use_pdf = bool(pdf_text)

        answer = ask_groq(message, use_pdf=use_pdf)

        return jsonify(
            {
                "success": True,
                "response": answer,
                "mode": "pdf" if use_pdf else "chat",
                "pdf_filename": pdf_filename if pdf_filename else None,
            }
        )

    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 400

    except Exception as error:
        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 500


if __name__ == "__main__":
    print("=" * 50)
    print("AI PDF Assistant")
    print("Open http://127.0.0.1:5000")
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )