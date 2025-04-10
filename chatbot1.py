from flask import Flask, request, render_template, redirect, url_for
import google.generativeai as genai
from google.generativeai import GenerationConfig
import re

# Initialize Flask application
app = Flask(__name__)

# Configure Google Generative AI
genai.configure(api_key="AIzaSyC16vH2ymNgegzMmoJiUrJqrtqybwbhkMM")

# Create GenerationConfig object
generation_config = GenerationConfig(
    temperature=1,
    top_p=0.95,
    top_k=40,
    max_output_tokens=8192,
)

# Initialize the Generative Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# In-memory storage for chat history
chat_history = []


# Helper function to format and clean up the AI response
def format_response_as_points(response_text):
    # Remove markdown bold (**bold**) and list markers (*)
    cleaned_text = re.sub(r'\*\*(.*?)\*\*', r'\1', response_text)  # Removes **bold** formatting
    cleaned_text = re.sub(r'^\*', '', cleaned_text, flags=re.MULTILINE)  # Removes leading * from list items

    # Split the response into points based on newlines
    points = [point.strip() for point in cleaned_text.split("\n") if point.strip()]

    # Return as a numbered list (like 1. First point, 2. Second point, etc.)
    numbered_points = [f"{i + 1}. {point}" for i, point in enumerate(points)]

    # Join the points with newline characters and return as a plain text
    return "\n".join(numbered_points)


# Home route
@app.route("/")
def home():
    return render_template("index.html", chat_history=chat_history)


# Route to handle questions
@app.route("/ask", methods=["POST"])
def ask():
    # Get the user question from the form
    user_question = request.form["question"].strip()

    # Add user input to chat history
    chat_history.append({"type": "user", "content": user_question})

    # Prepare the prompt for the AI model
    prompt = f"""
    input: You are a chatbot assisting with JSS Academy of Technical Education (JSSATE). Your responses should be based on the website https://jssateb.ac.in, formatted concisely and in points. Avoid giving the website link directly. Stick to the user's question and keep answers under 200 words.
    output: Hello! Welcome to JSSATE College. How can I assist you?
    input: {user_question}
    output:
    """

    # Generate content using the model
    response = model.generate_content([prompt])
    ai_answer = response.text.strip()

    # Format the AI's response into numbered points
    formatted_response = format_response_as_points(ai_answer)

    # Add AI's response to chat history
    chat_history.append({"type": "bot", "content": formatted_response})

    # Redirect to home page to display updated conversation
    return redirect(url_for("home"))


# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
