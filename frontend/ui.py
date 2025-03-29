import gradio as gr
import fitz  # PyMuPDF for PDF handling

def process_pdf(pdf_file):
    if pdf_file is None:
        return "Please upload a PDF file"
    
    try:
        # Open the PDF file
        doc = fitz.open(pdf_file.name)
        # Get the first page
        page = doc[0]
        # Convert the page to an image
        pix = page.get_pixmap()
        # Save the image temporarily
        img_path = "temp_page.png"
        pix.save(img_path)
        return img_path
    except Exception as e:
        return f"Error processing PDF: {str(e)}"
    
history = [
    {"role": "assistant", "content": "I am happy to provide you that report and plot."},
    {"role": "assistant", "content": gr.Plot(value=make_plot_from_file('quaterly_sales.txt'))}
]

# Create the Gradio interface
demo = gr.Interface(
    fn=process_pdf,
    inputs=gr.File(label="Upload PDF", file_types=[".pdf"]),
    outputs=gr.Image(label="PDF Preview"),
    title="PDF Uploader and Viewer",
    description="Upload a PDF file to view its first page",
    chat=gr.ChatInterface(
        process_pdf,
        title="PDF Uploader and Viewer",
        description="Upload a PDF file to view its first page"
    )
)

if __name__ == "__main__":
    demo.launch()
