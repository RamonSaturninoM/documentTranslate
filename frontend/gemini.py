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

def get_summary(pdf_file_path, language = "español"):
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
        contents = [summary_prompt, pdf_part]

    )
    # for chunk in response:
        # print(chunk.text, end="")

    return response



response = get_summary("./32912.pdf")

for chunk in response:
    print(chunk.text, end="")

# content = input().strip().lower()
# while content != "exit":
#     response = chat.send_message_stream(content, config=GLOBAL_CONFIG)
#     for chunk in response:
#         print(chunk.text, end="")
#     content = input().strip()
#
# for message in chat.get_history():
#     print(f'role - {message.role}', end=": ")
#     print(message.parts[0].text)