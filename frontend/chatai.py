from google import genai

client = genai.Client(api_key="AIzaSyCdnFgHTZ6aZpg2QB6qmQ6Rsnwje4U5Klo")

chat = genai.GenerativeModel("gemini-1.5-flash").start_chat()

print("🤖 Gemini Chat (type 'exit' to quit)\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in {"exit", "quit"}:
        print("👋 Goodbye!")
        break

    response = chat.send_message(user_input, stream=True)

    print("Gemini: ", end="", flush=True)
    for chunk in response:
        print(chunk.text, end="", flush=True)
    print("\n")