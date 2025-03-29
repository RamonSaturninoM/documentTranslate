from transformers import MarianMTModel, MarianTokenizer

# conda activate pdf-translator
# Load model and tokenizer
model_name = "AIzaSyCCg_Jp-4JiIbRTtB4JZUckW_y8wKjzmjs"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def translate(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    translated_tokens = model.generate(**inputs)
    return tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

def save_to_file(text, filename="translated_message.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    message = input("\nEnter message to translate: ")
    translation = translate(message)

    print("\nTranslated Message: ")
    print(translation)

    save_to_file(translation)
    print("Saved to translated_message.txt")

if __name__ == "__main__":
    main()