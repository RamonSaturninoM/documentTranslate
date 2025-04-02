# DocuChisme (spoiler: we got first place!)

DocuChisme is a translation tool designed to ease the burden of understanding and completing legal documents for first-generation families. Inspired by personal experiences, our tool empowers users with accessible communication and efficient document handling.

---

## Inspiration

Growing up as first-generation Americans, we often had to translate important documents for our parents—a task that was both stressful and confusing at a young age. This experience inspired us to create a tool that lightens the load for first-gen children, empowering families through accessible communication and a better understanding of legal documents.

---

## What It Does

- **Instant Translation:** Upload a fillable PDF and receive a translated summary immediately.
- **Actionable Steps:** Generates a step-by-step action list by translating each section of the form.
- **Editable PDFs:** Enables direct modifications to the PDF, with the finalized form available for download.
- **Interactive Chatbot:** Provides a chatbot that answers questions about the PDF and offers helpful resources—all in Spanish.

---

## How We Built It

- **Frontend:** Built with [Gradio](https://gradio.app/) to showcase and interact with uploaded PDFs.
- **PDF Processing:** Leveraged Python libraries such as [PyMuPDF](https://pymupdf.readthedocs.io/) for scanning PDFs and extracting fillable form fields.
- **Translation & Q&A:** Utilized Gemini to power translation and document-based question answering, ensuring seamless support and useful responses.

---

## Challenges We Ran Into

- **Parsing Varied PDFs:** 
  - We experimented with multiple open source tools and free trials (e.g., Apryes SDK, LAyout Parser, Amazon Textract) to parse different PDF formats.
  - Found that flat PDFs are especially challenging for detecting structure, whereas Acroform PDFs are easier to handle.
- **Visualization & Modification:** 
  - Struggled with visualizing PDFs and modifying them within Gradio, which lacks the web support provided by many JavaScript libraries.

---

## Accomplishments We're Proud Of

- **Real-Time Translation:** Offering live translation of documents into actionable steps to assist users in filling out forms on the go.
- **Accurate AI Integration:** Achieving precise translation and effective document question answering through our AI model integration.

---

## What We Learned

- **Gradio’s Versatility:** Gained hands-on experience using Gradio as both a frontend and backend framework, along with an understanding of its PDF visualization limitations.
- **Understanding PDF Forms:** Learned about the differences among PDF forms and developed strategies to address their unique challenges.
- **Effective Use of Language Models:** Explored how to leverage language models for accurate translation and efficient document-based Q&A.

---

## What's Next for DocuChisme

- **Enhanced PDF Support:** Expanding to support all types of PDFs.
- **Improved Editing:** Developing a cleaner PDF modification experience, including direct interaction with the file itself.

---
