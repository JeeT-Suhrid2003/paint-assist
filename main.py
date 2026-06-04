from flask import Flask, render_template, request, jsonify
from google.cloud import storage
from google import genai
from google.genai import types
import os
import json

app = Flask(__name__)

# CONFIGURATION: Change these to match your GCP setup
PROJECT_ID = "qwiklabs-gcp-01-a8bd18e62a60"
BUCKET_NAME = "paint-1"

# Initialize GCP Clients
storage_client = storage.Client(project=PROJECT_ID)
ai_client = genai.Client(
    vertexai=True, 
    project=PROJECT_ID, 
    location="us-central1" # Or your preferred GCP region like 'asia-south1'
)
def analyze_painting_with_ai(file_bytes, mime_type):
    """Sends the painting image to Gemini to extract colors and recipes."""
    
    prompt = """
    Analyze this painting. Return a JSON object with exactly two keys:
    1. "base_paints": A list of standard, single-pigment acrylic/oil paint colors needed to recreate this image.
    2. "color_mixtures": A list of objects, each containing:
       - "target_color": The name of a distinct complex color found in the painting.
       - "recipe": Detailed mixing instructions using percentages of the base_paints.
    
    Respond ONLY with valid JSON. Do not include markdown formatting or blocks.
    """
    
    # Structure the image data for the API
    image_part = types.Part.from_bytes(
        data=file_bytes,
        mime_type=mime_type,
    )
    
    # Call the lightweight, multi-modal Gemini Flash model
    response = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[image_part, prompt]
    )
    
    # Parse and return the JSON response
    try:
        # Clean up text if the model wrapped it in markdown code blocks
        clean_text = response.text.strip().strip("```json").strip("```")
        print("AI Response:", clean_text)  # Debugging output
        return json.loads(clean_text)
    except Exception as e:
        return {
            "error": "Failed to parse AI response",
            "raw_response": response.text
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'painting' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['painting']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Read file data into memory
    file_bytes = file.read()
    mime_type = file.content_type

    try:
        # 1. Save the file to Google Cloud Storage (The Bucket)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(file.filename)
        # Rewind file pointer just in case, and upload
        blob.upload_from_string(file_bytes, content_type=mime_type)
        
        # 2. Get the real analysis from the Gemini Cloud Model
        ai_result = analyze_painting_with_ai(file_bytes, mime_type)
        
        return jsonify(ai_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))