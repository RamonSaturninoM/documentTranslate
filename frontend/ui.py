import gradio as gr
import fitz  # PyMuPDF for PDF handling
from gemini import get_summary, open_chat, send_message
import uuid

class PDFState:
    def __init__(self):
        self.current_page = 0
        self.doc = None
        self.total_pages = 0
        self.highlight_mode = False
        self.summary = ""

pdf_state = PDFState()
chat = None  # Persistent Gemini chat session

counter = 0

def process_pdf(pdf_file, highlight_fields):
    global chat
    if pdf_file is None:
        return None, None, "Por favor, cargue un archivo PDF", ""
    
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
        
        pdf_state.summary = get_summary(pdf_file.name)
        chat = open_chat(pdf_file.name)
        
        # Display the first page
        img_path, page_info, status = display_page(0)
        return img_path, page_info, status, pdf_state.summary
    except Exception as e:
        return None, None, f"Error processing PDF: {str(e)}"

def display_page(page_num):
    try:
        if pdf_state.doc is None:
            return None, None, "No hay PDF cargado"
        
        # Get the requested page and convert it to an image
        page = pdf_state.doc[page_num]
        pix = page.get_pixmap()
        img_path = "temp_page.png"
        pix.save(img_path)
        
        page_info = f"Página {page_num + 1} of {pdf_state.total_pages}"
        return img_path, page_info, f"Mostrando página {page_num + 1}"
    except Exception as e:
        return None, None, f"Error al mostrar la página: {str(e)}"

def next_page():
    if pdf_state.doc is None:
        return None, None, "No hay PDF cargado"
    
    pdf_state.current_page = min(pdf_state.current_page + 1, pdf_state.total_pages - 1)
    return display_page(pdf_state.current_page)

def prev_page():
    if pdf_state.doc is None:
        return None, None, "No hay PDF cargado"
    
    pdf_state.current_page = max(pdf_state.current_page - 1, 0)
    return display_page(pdf_state.current_page)

def handle_user_message(user_message, chat_history):
    response = send_message(user_message)
    chat_history = chat_history or []
    chat_history.append((user_message, response))
    return chat_history

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
    


def update_field_text(pdf_file, text_input, field_name):
    """
    Updates a specific field in the PDF with user input text.
    
    Args:
        pdf_file: The uploaded PDF file
        field_name: The name of the field to update
        text_input: Text to insert into the field
    
    Returns:
        Updated image, page info, status message
    """
    if pdf_file is None:
        return None, None, "Please upload a PDF file first"
    
    try:
        # Get the widget by field name
        

        widget, msg = get_widget_by_field_name(pdf_file, field_name)
        
        if widget is None:
            return None, None, f"Field not found: {msg}"
        
        # Open the PDF document
        doc = pdf_state.doc
        
        # Find the page that contains this widget
        target_page = None
        for page_num, page in enumerate(doc):
            widgets = page.widgets()
            if widgets:
                for w in widgets:
                    if w.field_name == field_name:
                        target_page = page
                        break
                if target_page:
                    break
        
        if not target_page:
            doc.close()
            return None, None, f"Could not find page for widget {field_name}"
            
        # Get the widget's rectangle
        rect = widget.rect
        
        # Calculate appropriate font size and position
        available_width = rect.width
        available_height = rect.height
        
        # Start with max font size, but constrain by the available height
        fontsize = min(12, available_height)
        
        # Measure the text width at this font size
        text_width = fitz.get_text_length(text_input, fontname="helv", fontsize=fontsize)
        
        # If the text is too wide, scale the font size down proportionally
        if text_width > available_width:
            fontsize = fontsize * (available_width / text_width)
            # Also ensure we don't exceed the height
            fontsize = min(fontsize, available_height)
        
        # Ensure the font size is not below the minimum
        if fontsize < 4:
            fontsize = 4
        
        # Calculate text position (centered vertically in the field)
        center_y = (rect.y0 + rect.y1) / 2
        adjusted_point = fitz.Point(rect.x0, center_y + fontsize/3)
        
        # Add text to the form field
        target_page.insert_text(
            adjusted_point,
            text_input,
            fontname="helv",
            fontsize=fontsize,
            color=(0, 0, 0)
        )
        
       
        
        # Save the modified PDF
        output_path = f"updated_pdf_{uuid.uuid4().hex}.pdf"
        doc.save(output_path)
        doc.close()
        
        # Update global PDF state with the modified document
        pdf_state.doc = fitz.open(output_path)
        pdf_state.current_page = 0  # Reset to first page
        
        # Display the updated PDF
        img_path, page_info, msg = display_page(0)

        
        return img_path, page_info, f"Field '{field_name}' updated successfully"
        
    except Exception as e:
        return None, None, f"Error updating field: {str(e)}"


def extract_field_names(pdf_file):
    if pdf_file is None:
        return None, "Please upload a PDF file"
    
    try:
        doc = fitz.open(pdf_file.name)
        field_data = {}
        # Iterate over each page in the document
        for page_num, page in enumerate(doc):
            page_fields = []
            widgets = page.widgets()  # Get widget annotations on the page
            if widgets:
                for widget in widgets:
                    # Access the field name via widget.field_name
                    field_name = widget.field_name
                    page_fields.append(field_name)
            # Store the field names for the page (pages are 1-indexed for user clarity)
            field_data[page_num + 1] = page_fields
        
        doc.close()
        return field_data, "Field names extracted successfully!"
    
    except Exception as e:
        return None, f"Error extracting field names: {str(e)}"
    
def get_widget_by_field_name(pdf_file, target_field_name):
    if pdf_file is None:
        return None, "No PDF file provided"
    
    try:
        doc = fitz.open(pdf_file.name)
        for page in doc:
            widgets = page.widgets()
            if widgets:
                for widget in widgets:
                    if widget.field_name == target_field_name:
                        doc.close()
                        return widget, f"Widget '{target_field_name}' found."
        doc.close()
        return None, f"Widget '{target_field_name}' not found."
    except Exception as e:
        return None, f"Error accessing widget: {str(e)}"
    
def get_field_name_by_index(pdf_file, index):
    field_data, _ = extract_field_names(pdf_file)
    all_fields = []
    for page_fields in field_data.values():
        all_fields.extend(page_fields)

    if index < len(all_fields):
        return all_fields[index]
    else:
        return None

# def load_field_label(pdf_file):
#     global counter
#     field_name = get_field_name_by_index(pdf_file, counter)
#     new_direction = send_message(f"The user is trying to fill out a document in english when they dont know english. Create a direction in spanish using the field {field_name} telling the user to fill in whatever needs to go in the field. It might be shortned, this is mostly liekly for a legal document.")
#     if field_name:
#         counter += 1
#         return gr.update(label=f"Update the field '{field_name}' ↓"), field_name
#     else:
#         return gr.update(label="No more fields!"), ""
def load_field_label(pdf_file):
    global counter
    field_name = get_field_name_by_index(pdf_file, counter)

    if field_name:
        # Use Gemini to generate a Spanish instruction
        new_direction = send_message(
            f"The user is trying to fill out a document in English when they don't know English. "
            f"Create a direction in Spanish using the field name '{field_name}', telling the user what to fill in. "
            f"Keep it short, since this is likely a legal document."
        )

        counter += 1
        return gr.update(label=new_direction), field_name
    else:
        return gr.update(label="No more fields!"), ""
    


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# Visor de PDF con resumen automático + Gemini Chat")
    
    with gr.Row():
        # Left column for PDF handling
        with gr.Column(scale=2):
            gr.Markdown("### Visor de PDF")
            with gr.Row():
                file_input = gr.File(label="Subir PDF", file_types=[".pdf"])
                highlight_checkbox = gr.Checkbox(label="Resaltar campos de formulario (temporalmente)", value=False)
            
            image_output = gr.Image(label="Vista previa de página")
            
            with gr.Row():
                prev_button = gr.Button("← Página anterior")
                page_info = gr.Textbox(label="Información de la página", interactive=False)
                next_button = gr.Button("Página siguiente →")
            
            status_text = gr.Textbox(label="Estado", interactive=False)
        
        with gr.Column(scale=1):
            gr.Markdown("### Resumen automático")
            summary_output = gr.Textbox(label="Resumen de Gemini", lines=20, interactive=False)

            # 🔽 Update Fields UI goes here
            gr.Markdown("### Rellena los espacios en blanco")
            with gr.Row():
                field_text_input = gr.Textbox(label="Update the field ↓")
                field_name_state = gr.State("")
            with gr.Row():
                load_field_button = gr.Button(" Ir al siguiente espacio")
                update_field_button = gr.Button("Guardar cambios en el espacio")

            gr.Markdown("### Gemini Chat")
            chatbot = gr.Chatbot(label="Pregúntale a Gemini sobre el PDF")
            with gr.Row():
                user_msg = gr.Textbox(placeholder="Haz una pregunta...")
                send_btn = gr.Button("Enviar")
            
            # Button to permanently modify and save the PDF with highlights
            modify_button = gr.Button("Modificar PDF (Guardar resaltes)")
            
            # Download component for the modified PDF
            download_file = gr.File(label="Descargar PDF modificado")
    
   

    # Load next field and update label/state
    load_field_button.click(
        fn=load_field_label,
        inputs=[file_input],
        outputs=[field_text_input, field_name_state]
    )

    # Update the field with user input and field name from state
    update_field_button.click(
        fn=update_field_text,
        inputs=[file_input, field_text_input, field_name_state],
        outputs=[image_output, page_info, status_text]
    )

    # Add the click event handler
#     update_field_button.click(
#         fn=update_field_text,
#         inputs=[file_input, field_text_input, field_name],
#         outputs=[image_output, page_info, status_text]
# )


        
        # # Right column for Chat
        # with gr.Column(scale=1):
        #     gr.Markdown("### Chat")
        #     chatbot = gr.Chatbot(
        #         label="Historial de chat",
        #         height=400,
        #         container=True,
        #         type="messages",
        #         show_label=True
        #     )
        #     with gr.Row():
        #         msg = gr.Textbox(
        #             label="Mensaje",
        #             placeholder="Escribe tu mensaje aquí...",
        #             container=True,
        #             scale=4
        #         )
        #         clear = gr.Button("Limpiar", scale=1)
    
    # PDF processing when file is uploaded

    


    file_input.change(
        fn=process_pdf,
        inputs=[file_input, highlight_checkbox],
        outputs=[image_output, page_info, status_text, summary_output]
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

    send_btn.click(
        fn=handle_user_message,
        inputs=[user_msg, chatbot],
        outputs=[chatbot]
    )
    
    # Chat handling
    # msg.submit(
    #     fn=chat_response,
    #     inputs=[msg, chatbot],
    #     outputs=[chatbot]
    # )
    # clear.click(lambda: None, None, chatbot, queue=False)

    

if __name__ == "__main__":
    demo.launch()
