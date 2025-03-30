from google import genai
from google.genai import types
import pathlib

API_KEY = "AIzaSyDO-3Vtl-fFTei6qjCVKrlXCnFumNWLQzo"
# GLOBAL_CONFIG = types.GenerateContentConfig(
#         max_output_tokens=500,
#         temperature=0.1,
#         system_instruction="Estas ayudando a un usuario a traducir un texto."
#     )

# filename = "NDA.txt"
# with open(filename, "r", encoding="utf-8") as f:
#     textfile = f.read()

client = genai.Client(api_key=API_KEY)
chat = client.chats.create(model="gemini-2.0-flash")

def get_summary(pdf_file_path, language="español"):
    summary_prompt = f"""Read the legal document below carefully. Your main task is to generate a succinct summary in {language} that captures the following in just a couple of sentences:
    - **Type and Purpose:** What type of legal document it is and its overall purpose.
    - **Parties Involved:** Who the parties are.
    - **Key Obligations and Requirements:** What the document is asking for, including any obligations, rights, or conditions imposed on the parties.
    - **Essential Details:** Any critical points that define the document’s intent and scope.

    The summary should be written in clear, precise language that is accessible to a non-expert reader while maintaining legal accuracy. The response should contain only the summary.
    """

    pdf_bytes = pathlib.Path(pdf_file_path).read_bytes()
    pdf_part = types.Part.from_bytes(
        data=pdf_bytes,
        mime_type='application/pdf'
    )

    response = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=[summary_prompt, pdf_part]
    )

    # Collect all chunks into a final summary string
    return "".join(chunk.text for chunk in response if hasattr(chunk, "text"))

def open_chat(pdf_file_path, language="español"):
    global chat

    # Load PDF
    pdf_bytes = pathlib.Path(pdf_file_path).read_bytes()
    pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")

    # Create chat session (no system_instruction param)
    chat = client.chats.create(model="gemini-2.0-flash")

    # Send system prompt + document as a single message
    prompt = f"""
    You are a helpful assistant that always communicates in {language}.
    Answer all questions using the following legal document. If uncertain, say so.

    Be concise, factual, and polite. Use the document for context, 
    but if you are uncertain, feel free to search for appropriate sources.
    When the user has concerns about specfic situations then please provide sources that 
    would benefit the user.
    """

    # Send both prompt + PDF together
    chat.send_message([prompt, pdf_part])

    return chat

def send_message(message):
    if chat is None:
        raise Exception("Chat session not initialized")
    response = chat.send_message(message)
    return response.text