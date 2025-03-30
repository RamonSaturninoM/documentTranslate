Inspiration
Growing up as first-generation Americans, we often had to translate important documents for our parents - a task that was both stressful and confusing at such young age. That experience inspired us to create a tool that eases this burden for first gen children, empowering families through accessible communication and understanding of legal documents.

What it does
Our tool allows the user to upload a fillable pdf and instantly receive a translated summary. It generates a step-by-step action list, translating each section of the form and allowing users to modify the PDF directly. The finalized form will also be available for download. Users can interact with a chatbot that answers questions about the PDF and will provide helpful resources, all in Spanish.

How we built it
We utilized Gradio to build the frontend and display the uploaded PDFs. We used a variety of Python PDF libraries, such as PyMuPDF, to scan the PDFs to detect and extract fillable form fields. We primarily utilized Gemini for translation and document question and answering, enabling seamless support and useful responses.

Challenges we ran into
We heavily struggled at first with parsing a variety of PDFs. We used a multitude of open source tools and some with a free trial from Apryes SDK, LAyout parser, Amazon Textract etc. All of these solutions varied from local deployment to setting up our very own hugging face endpoints. None of them accurately detected the layout of the PDF. We eventaully found out that flat PDFs are really hard to detect the structure of, with Acroform PDFs being the easiest to detect. We also struggled to visualize the PDFs and modifying them since Gradio does not provide web support for viewing PDFs like many Javascript libraries do.

Accomplishments that we're proud of
We are proud to be able to provide real time translation for documents in the form of action steps, helping the user fill out the form on the go, as well as accurate translation for interfacing with the AI model on document questions and answering.

What we learned
We gained hands-on experience using Gradio as both a frontend and backend framework, along with learning about its ease of integration and limitations with PDF visualization. We also learned the differences found in PDF forms and though critically on how to approach these conflicts. Additionally, we learned how to leverage language models effectively for translation and document-based question answering.

What's next for DocuChisme
Broader support for all PDF types, cleaner PDF modification (click on the file itself)
