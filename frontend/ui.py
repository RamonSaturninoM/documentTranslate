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
        # Open the PDF file and store in state
        pdf_state.doc = fitz.open(pdf_file.name)
        pdf_state.total_pages = pdf_state.doc.page_count
        pdf_state.current_page = 0
        
        if highlight_fields:
            # Highlight form fields if requested
            for page in pdf_state.doc:
                widgets = page.widgets()
                if widgets:
                    for widget in widgets:
                        rect = widget.rect
                        page.draw_rect(rect, color=(1, 0, 0), width=2)
        
        # Get the first page
        return display_page(0)
    except Exception as e:
        return None, None, f"Error processing PDF: {str(e)}"

def display_page(page_num):
    try:
        if pdf_state.doc is None:
            return None, None, "No PDF loaded"
        
        # Get the requested page
        page = pdf_state.doc[page_num]
        # Convert the page to an image
        pix = page.get_pixmap()
        # Save the image temporarily
        img_path = "temp_page.png"
        pix.save(img_path)
        
        # Update page info
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

def chat_response(message, history):
    # Format the response as a list of message dictionaries
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
        # Left column for PDF
        with gr.Column(scale=2):
            gr.Markdown("### PDF Viewer")
            with gr.Row():
                file_input = gr.File(label="Upload PDF", file_types=[".pdf"])
                highlight_checkbox = gr.Checkbox(label="Highlight Form Fields", value=False)
            
            image_output = gr.Image(label="Page Preview")
            
            with gr.Row():
                prev_button = gr.Button("← Previous Page")
                page_info = gr.Textbox(label="Page Information", interactive=False)
                next_button = gr.Button("Next Page →")
            
            status_text = gr.Textbox(label="Status", interactive=False)
        
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
    
    # PDF handling
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
    
    # Chat handling
    msg.submit(
        fn=chat_response,
        inputs=[msg, chatbot],
        outputs=[chatbot]
    )
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch()