#!/usr/bin/env python3
"""Test script to verify OpenRouter API key works"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

api_key = os.getenv("OPEN_ROUTER_API_KEY")

if not api_key:
    print("ERROR: OPEN_ROUTER_API_KEY not found in .env file")
    exit(1)

print(f"API Key found: {api_key[:8]}...{api_key[-4:]}")
print(f"API Key length: {len(api_key)} characters")
print()

# Create client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

print("Testing OpenRouter API...")
print("Model: mistralai/mistral-7b-instruct (cheap paid model)")
print()

try:
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Job Scraper Test",
        },
        model="mistralai/mistral-7b-instruct",
        messages=[
            {
                "role": "user",
                "content": "Say 'Hello, the API is working!' in exactly those words.",
            }
        ],
    )

    response = completion.choices[0].message.content
    print("SUCCESS! Response from API:")
    print(f"  {response}")
    print()
    print("Your OpenRouter API key is working correctly.")

except Exception as e:
    print(f"ERROR: {type(e).__name__}")
    print(f"Message: {e}")
