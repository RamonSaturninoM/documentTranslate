import argparse
from transformers import MarianMTModel, MarianTokenizer

# Load model and tokenizer
model_name = "Helsinki-NLP/opus-mt-en-es"
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
    parser = argparse.ArgumentParser(description="Translate text from a file using Helsinki-NLP.")
    parser.add_argument("input_file", help="Path to the input .txt file")
    parser.add_argument("-o", "--output", help="Output file name (default: translated_message.txt)", default="translated_message.txt")
    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as f:
        input_text = f.read()

    translated = translate(input_text)

    print("\n Translated Message:")
    print(translated) 

    save_to_file(translated, args.output)
    print(f"\n Full translation saved to: {args.output}")

if __name__ == "__main__":
    main()

