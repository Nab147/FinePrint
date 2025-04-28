from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import os
import google.generativeai as genai
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini AI Configuration
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Changed from "Fineprint" to standard naming
    model = genai.GenerativeModel('gemini-1.5-pro')
    logger.info("Gemini AI configured successfully")
except Exception as e:
    logger.error(f"Gemini configuration failed: {str(e)}")
    raise RuntimeError("Failed to initialize Gemini AI")

# Constants
SATIRE_KEYWORDS = ["satirical", "teaching example", "demonstration", "how not to"]
MAX_TEXT_LENGTH = 3000  # Limit text extraction for efficiency

def clean_analysis(text):
    """Process and structure the raw analysis text."""
    try:
        if any(keyword in text.lower() for keyword in SATIRE_KEYWORDS):
            return process_educational_content(text)
        return process_contract_content(text)
    except Exception as e:
        logger.error(f"Error in clean_analysis: {str(e)}")
        raise

def process_educational_content(text):
    """Process educational/satirical content."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    result = {
        "document_type": "educational",
        "timestamp": datetime.now().isoformat(),
        "key_insights": {
            "teaching_purpose": "",
            "key_principles": [],
            "anti_patterns": []
        }
    }

    current_section = None
    for line in lines:
        if "**Teaching Purpose:**" in line:
            result["key_insights"]["teaching_purpose"] = line.replace("**Teaching Purpose:**", "").strip()
        elif line.startswith("* ") and "**" in line:
            result["key_insights"]["key_principles"].append(line[2:].replace("**", "").strip())
        elif line.startswith("* "):
            result["key_insights"]["anti_patterns"].append(line[2:].strip())
    
    return result

def process_contract_content(text):
    """Process contract content and identify clauses."""
    clauses = []
    for clause in text.split("\n\n"):
        if clause.strip():
            parts = [p.strip() for p in clause.split("\n") if p.strip()]
            if len(parts) >= 3:  # Ensure we have quote, risk, and fix
                clauses.append({
                    "clause": parts[0],
                    "risk": parts[1],
                    "fix": parts[2],
                    "severity": "medium"  # Default severity
                })
    
    return {
        "document_type": "contract",
        "timestamp": datetime.now().isoformat(),
        "clauses": clauses,
        "summary": f"Found {len(clauses)} potentially problematic clauses"
    }

def format_analysis_for_layman(analysis_result):
    """Convert analysis to human-readable format."""
    try:
        if analysis_result["document_type"] == "educational":
            return format_educational_output(analysis_result)
        return format_contract_output(analysis_result)
    except Exception as e:
        logger.error(f"Formatting error: {str(e)}")
        return "Could not format analysis results."

def format_educational_output(analysis):
    """Format educational content output."""
    output = [
        "This document appears to be for educational purposes.",
        f"\n**Teaching Objective:** {analysis['key_insights']['teaching_purpose']}"
    ]
    
    if analysis['key_insights']['key_principles']:
        output.append("\n**Key Principles of Good Drafting:**")
        output.extend(f"- {p}" for p in analysis['key_insights']['key_principles'])
    
    if analysis['key_insights']['anti_patterns']:
        output.append("\n**Things to Avoid (Anti-Patterns):**")
        output.extend(f"- {p}" for p in analysis['key_insights']['anti_patterns'])
    
    return "\n".join(output)

def format_contract_output(analysis):
    """Format contract analysis output."""
    output = [
        "This document appears to be a contract.",
        f"\nAnalysis performed at: {analysis['timestamp']}",
        f"\n{analysis['summary']}:"
    ]
    
    for i, clause in enumerate(analysis.get("clauses", []), 1):
        output.extend([
            f"\n--- Clause {i} ---",
            f"**Original Text:** {clause['clause']}",
            f"**Potential Risk:** {clause['risk']}",
            f"**Suggested Improvement:** {clause['fix']}",
            f"**Severity:** {clause.get('severity', 'medium')}"
        ])
    
    return "\n".join(output)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint."""
    try:
        # Validate request
        if 'file' not in request.files:
            logger.warning("No file uploaded")
            return jsonify({"error": "No file uploaded"}), 400

        pdf_file = request.files['file']
        if not pdf_file.filename.lower().endswith('.pdf'):
            logger.warning(f"Invalid file type: {pdf_file.filename}")
            return jsonify({"error": "Only PDF files are supported"}), 400

        # Process PDF
        try:
            text = PyPDF2.PdfReader(pdf_file).pages[0].extract_text()[:MAX_TEXT_LENGTH]
            if not text.strip():
                logger.warning("Empty PDF or no text extracted")
                return jsonify({"error": "Empty PDF or no text extracted"}), 400
        except Exception as e:
            logger.error(f"PDF processing error: {str(e)}")
            return jsonify({"error": f"PDF processing error: {str(e)}"}), 400

        # Generate analysis
        prompt = """Analyze this contract. For each potentially unfair clause:
        1. [EXACT QUOTE] - Copy the full clause text
        2. [RISK] - Explain the legal/business risk (1-2 sentences)
        3. [FIX] - Suggest specific alternative wording"""
        
        try:
            response = model.generate_content(
                prompt + text,
                generation_config={"temperature": 0.2}
            )
            raw_output = response.text
        except Exception as e:
            logger.error(f"Gemini analysis failed: {str(e)}")
            return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500

        # Process and return results
        cleaned = clean_analysis(raw_output)
        layman_output = format_analysis_for_layman(cleaned)
        
        logger.info(f"Successfully analyzed {pdf_file.filename}")
        return jsonify({
            "status": "success",
            "result_json": cleaned,
            "result_text": layman_output
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  # For Render compatibility
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False for production
