import azure.functions as func
import logging
import json
import os
from google import genai
from google.genai import types
from pydantic import ValidationError
from models import ExtractionResult

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="ingest")
def ingest(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('AI Ingest function triggered.')

    # 1. Configure the AI (The Brain)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return func.HttpResponse("Error: GEMINI_API_KEY is missing.", status_code=500)

    # Initialize the Modern Client
    client = genai.Client(api_key=api_key)

    try:
        # 2. Get the Raw Text
        req_body = req.get_json()
        raw_text = req_body.get("document_text")

        if not raw_text:
            return func.HttpResponse("Error: 'document_text' field is required.", status_code=400)

    except ValueError:
        return func.HttpResponse("Error: Body must be valid JSON.", status_code=400)

    try:
        # 3. Construct the Prompt
        schema_json = json.dumps(ExtractionResult.model_json_schema(), indent=2)

        prompt = f"""
        You are an expert Project Manager AI. 
        Analyze the following text and extract all actionable tasks.
        
        CRITICAL RULES:
        1. Output MUST be strictly matching this JSON Schema:
        {schema_json}
        
        2. If no date is found, use null.
        3. Be concise.

        TEXT TO ANALYZE:
        {raw_text}
        """

        # 4. Call Gemini (Modern 2026 Syntax)
        logging.info("Sending text to Gemini...")
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # 5. Validate the AI's Output
        ai_data = json.loads(response.text)
        validated_result = ExtractionResult(**ai_data)

        # 6. Return the Result
        return func.HttpResponse(
            json.dumps({
                "status": "success", 
                "message": "AI Extraction Complete",
                "data": validated_result.model_dump()
            }),
            mimetype="application/json",
            status_code=200
        )

    except ValidationError as e:
        return func.HttpResponse(f"AI returned invalid data structure: {e.json()}", status_code=500)
    except Exception as e:
        logging.error(f"General Error: {str(e)}")
        return func.HttpResponse(f"Server Error: {str(e)}", status_code=500)