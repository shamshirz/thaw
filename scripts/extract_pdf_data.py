import os
from pathlib import Path
import logging
import json
from typing import Optional, Dict
from datetime import datetime
import pandas as pd
from pdfminer.high_level import extract_text
import openai
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text content from PDF file"""
    try:
        return extract_text(str(pdf_path))
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        return ""

def parse_with_openai(text: str, api_key: str) -> Optional[Dict]:
    """
    Use OpenAI to extract relevant information from bill text
    Returns: Dictionary with date, amount, and kwh_used if found
    """
    client = openai.OpenAI(api_key=api_key)
    
    prompt = """
    Extract the following information from this electric bill text:
    1. Bill date (in YYYY-MM-DD format)
    2. Total amount due/paid (as a decimal number)
    3. Total kWh used (as a decimal number)
    
    Format the response as a JSON object with keys: date, amount, kwh_used
    If any value cannot be found, use null.
    
    Bill text:
    {text}
    """.format(text=text)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a utility bill parser. Respond only with JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Error parsing with OpenAI: {e}")
        return None

def process_pdf_bills(pdf_dir: Path, output_file: Path, use_openai: bool = False):
    """Process all PDF bills in directory and output to CSV"""
    if use_openai:
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    results = []
    
    # Process each PDF file
    for pdf_file in sorted(pdf_dir.glob('*.pdf')):
        logger.info(f"Processing {pdf_file}")
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_file)
        if not text:
            logger.warning(f"No text extracted from {pdf_file}")
            continue
        
        # Try to parse with OpenAI if enabled
        if use_openai:
            data = parse_with_openai(text, api_key)
            if data:
                results.append(data)
                continue
        else:
            print(text)
        
        # If we get here, either OpenAI is disabled or failed
        logger.warning(f"Could not parse {pdf_file}")
        
    # Convert results to DataFrame and save
    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        logger.info(f"Saved extracted data to {output_file}")
    else:
        logger.warning("No data was successfully extracted")

def main():
    # Setup paths
    pdf_dir = Path("data/electric_bills")
    output_file = Path("data/electric_raw.csv")
    
    # Create directories if they don't exist
    pdf_dir.mkdir(exist_ok=True)
    output_file.parent.mkdir(exist_ok=True)
    
    # Process bills
    process_pdf_bills(pdf_dir, output_file, use_openai=False)

if __name__ == "__main__":
    main() 