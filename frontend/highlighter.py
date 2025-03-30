import fitz  # PyMuPDF
import gradio as gr

def modify_pdf(pdf_file):
    if pdf_file is None:
        return None, "Please upload a PDF file"
    
    try:
        # Open the PDF
        doc = fitz.open(pdf_file.name)
        
        # Process each page
        for page in doc:
            # Get form fields using widgets and annotations
            widgets = page.widgets()
            annots = page.annots()
            
            # Highlight form fields from widgets
            if widgets:
                for widget in widgets:
                    rect = widget.rect
                    highlight = page.add_rect_annot(rect)
                    highlight.set_colors(fill=(1, 1, 0))  # Yellow fill
                    highlight.set_border(width=1)  # Only set width
                    highlight.set_colors(stroke=(1, 0, 0))  # Set stroke color separately
                    highlight.set_opacity(0.3)
                    highlight.update()
            
            # Highlight form fields from annotations
            if annots:
                for annot in annots:
                    if annot.type[0] == fitz.PDF_ANNOT_WIDGET:  # Check if it's a form field
                        rect = annot.rect
                        highlight = page.add_rect_annot(rect)
                        highlight.set_colors(fill=(1, 1, 0))
                        highlight.set_border(width=1, color=(1, 0, 0))
                        highlight.set_opacity(0.3)
                        highlight.update()

        # Save the modified PDF
        output_path = "modified_pdf.pdf"
        doc.save(output_path)
        doc.close()
        
        return output_path, "PDF form fields highlighted successfully!"
    
    except Exception as e:
        return None, f"Error modifying PDF: {str(e)}"

# Create Gradio interface
demo = gr.Interface(
    fn=modify_pdf,
    inputs=[
        gr.File(label="Upload PDF")
    ],
    outputs=[
        gr.File(label="Modified PDF"),
        gr.Textbox(label="Status")
    ],
    title="PDF Form Field Highlighter",
    description="Upload a PDF and the tool will highlight all form fields in the document."
)

if __name__ == "__main__":
    demo.launch()
