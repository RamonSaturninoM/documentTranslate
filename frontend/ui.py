import gradio as gr
import fitz  # PyMuPDF for PDF handling

class PDFState:
    def __init__(self):
        self.current_page = 0
        self.doc = None
        self.total_pages = 0
        self.highlight_mode = False

pdf_state = PDFState()

def process_pdf(pdf_file, highlight_fields):
    if pdf_file is None:
        return None, None, "Please upload a PDF file"
    
    try:
        # Open the PDF file and store it in state
        pdf_state.doc = fitz.open(pdf_file.name)
        pdf_state.total_pages = pdf_state.doc.page_count
        pdf_state.current_page = 0
        
        if highlight_fields:
            # Temporary highlight: draw a red rectangle around each widget on every page
            for page in pdf_state.doc:
                widgets = page.widgets()
                if widgets:
                    for widget in widgets:
                        rect = widget.rect
                        page.draw_rect(rect, color=(1, 0, 0), width=2)
        
        # Display the first page
        return display_page(0)
    except Exception as e:
        return None, None, f"Error processing PDF: {str(e)}"

def display_page(page_num):
    try:
        if pdf_state.doc is None:
            return None, None, "No PDF loaded"
        
        # Get the requested page and convert it to an image
        page = pdf_state.doc[page_num]
        pix = page.get_pixmap()
        img_path = "temp_page.png"
        pix.save(img_path)
        
        page_info = f"Page {page_num + 1} of {pdf_state.total_pages}"
        return img_path, page_info, f"Displaying page {page_num + 1}"
    except Exception as e:
        return None, None, f"Error displaying page: {str(e)}"

def next_page():
    if pdf_state.doc is None:
        return None, None, "No PDF loaded"
    
    pdf_state.current_page = min(pdf_state.current_page + 1, pdf_state.total_pages - 1)
    return display_page(pdf_state.current_page)

def prev_page():
    if pdf_state.doc is None:
        return None, None, "No PDF loaded"
    
    pdf_state.current_page = max(pdf_state.current_page - 1, 0)
    return display_page(pdf_state.current_page)

def modify_pdf(pdf_file):
    """
    Opens a PDF, highlights form fields by drawing yellow highlights around
    widgets and widget annotations, saves the modified PDF, and updates the viewer.
    """
    if pdf_file is None:
        return None, None, "Please upload a PDF file", None
    
    try:
        # Open the original PDF
        doc = fitz.open(pdf_file.name)
        
        # Process each page: highlight form fields from widgets and annotations
        for page in doc:
            # Highlight from widgets
            widgets = page.widgets()
            if widgets:
                for widget in widgets:
                    rect = widget.rect
                    highlight = page.add_rect_annot(rect)
                    highlight.set_colors(fill=(1, 1, 0))   # Yellow fill
                    highlight.set_border(width=1)
                    highlight.set_colors(stroke=(1, 0, 0))  # Red stroke
                    highlight.set_opacity(0.3)
                    highlight.update()
            
            # Highlight from annotations (if they are form fields)
            annots = page.annots()
            if annots:
                for annot in annots:
                    if annot.type[0] == fitz.PDF_ANNOT_WIDGET:
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
        
        # Update global PDF state with the modified document
        pdf_state.doc = fitz.open(output_path)
        pdf_state.total_pages = pdf_state.doc.page_count
        pdf_state.current_page = 0

        # Generate preview for the first page of the modified PDF
        img_path, page_info, msg = display_page(0)
        return img_path, page_info, "PDF modified and highlighted successfully!", output_path
    
    except Exception as e:
        return None, None, f"Error modifying PDF: {str(e)}", None

def chat_response(message, history):
    if history is None:
        history = []
    history.append({"role": "user", "content": message})
    bot_message = f"You asked: {message}"
    history.append({"role": "assistant", "content": bot_message})
    return history

with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# PDF Uploader and Viewer with Chat")
    
    with gr.Row():
        # Left column for PDF handling
        with gr.Column(scale=2):
            gr.Markdown("### PDF Viewer")
            with gr.Row():
                file_input = gr.File(label="Upload PDF", file_types=[".pdf"])
                highlight_checkbox = gr.Checkbox(label="Highlight Form Fields (temporary)", value=False)
            
            image_output = gr.Image(label="Page Preview")
            
            with gr.Row():
                prev_button = gr.Button("← Previous Page")
                page_info = gr.Textbox(label="Page Information", interactive=False)
                next_button = gr.Button("Next Page →")
            
            status_text = gr.Textbox(label="Status", interactive=False)
            
            # Button to permanently modify and save the PDF with highlights
            modify_button = gr.Button("Modify PDF (Save Highlights)")
            
            # Download component for the modified PDF
            download_file = gr.File(label="Download Modified PDF")
        
        # Right column for Chat
        with gr.Column(scale=1):
            gr.Markdown("### Chat")
            chatbot = gr.Chatbot(
                label="Chat History",
                height=400,
                container=True,
                type="messages",
                show_label=True
            )
            with gr.Row():
                msg = gr.Textbox(
                    label="Message",
                    placeholder="Type your message here...",
                    container=True,
                    scale=4
                )
                clear = gr.Button("Clear", scale=1)
    
    # PDF processing when file is uploaded
    file_input.change(
        fn=process_pdf,
        inputs=[file_input, highlight_checkbox],
        outputs=[image_output, page_info, status_text]
    )
    
    # Page navigation
    prev_button.click(
        fn=prev_page,
        inputs=[],
        outputs=[image_output, page_info, status_text]
    )
    
    next_button.click(
        fn=next_page,
        inputs=[],
        outputs=[image_output, page_info, status_text]
    )
    
    # Modify PDF: update the preview and provide a download file
    modify_button.click(
        fn=modify_pdf,
        inputs=[file_input],
        outputs=[image_output, page_info, status_text, download_file]
    )
    
    # Chat handling
    msg.submit(
        fn=chat_response,
        inputs=[msg, chatbot],
        outputs=[chatbot]
    )
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch()
