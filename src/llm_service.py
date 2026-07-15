import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# Locate the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Load secret values from the local .env file
load_dotenv(BASE_DIR / ".env")


def generate_llm_text(prompt):
    """
    Send a prompt to the configured LLM and return its response.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY was not found in the .env file."
        )

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an IT service-management assistant. "
                    "Give clear, concise and professional responses."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    response = completion.choices[0].message.content

    return response.strip()


if __name__ == "__main__":
    test_prompt = (
        "Write one short support response for a user "
        "whose VPN stopped working after a password reset."
    )

    print(generate_llm_text(test_prompt))