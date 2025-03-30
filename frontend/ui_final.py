import gradio as gr
import fitz  # PyMuPDF for PDF handling
from gemini import get_summary, open_chat, send_message

class PDFState:
    def __init__(self):
        self.current_page = 0
        self.doc = None
        self.total_pages = 0
        self.summary = ""

pdf_state = PDFState()
chat = None  # Persistent Gemini chat session

def process_pdf(pdf_file, highlight_fields):
    global chat

    if pdf_file is None:
        return None, None, "Por favor, cargue un archivo PDF", ""

    try:
        pdf_state.doc = fitz.open(pdf_file.name)
        pdf_state.total_pages = pdf_state.doc.page_count
        pdf_state.current_page = 0

        if highlight_fields:
            for page in pdf_state.doc:
                widgets = page.widgets()
                if widgets:
                    for widget in widgets:
                        rect = widget.rect
                        page.draw_rect(rect, color=(1, 0, 0), width=2)

        pdf_state.summary = get_summary(pdf_file.name)
        chat = open_chat(pdf_file.name)

        img_path, page_info, status = display_page(0)
        return img_path, page_info, status, pdf_state.summary

    except Exception as e:
        return None, None, f"Error: {str(e)}", ""

def display_page(page_num):
    if pdf_state.doc is None:
        return None, None, "No hay PDF cargado"

    try:
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

with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# Visor de PDF con resumen automático + Gemini Chat")

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### Visor de PDF")
            with gr.Row():
                file_input = gr.File(label="Subir PDF", file_types=[".pdf"])
                highlight_checkbox = gr.Checkbox(label="Resaltar campos de formulario", value=False)

            image_output = gr.Image(label="Vista previa de página")

            with gr.Row():
                prev_button = gr.Button("← Página anterior")
                page_info = gr.Textbox(label="Información de la página", interactive=False)
                next_button = gr.Button("Página siguiente →")

            status_text = gr.Textbox(label="Estado", interactive=False)

        with gr.Column(scale=1):
            gr.Markdown("### Resumen automático")
            summary_output = gr.Textbox(label="Resumen de Gemini", lines=20, interactive=False)

            gr.Markdown("### Gemini Chat")
            chatbot = gr.Chatbot(label="Pregúntale a Gemini sobre el PDF")
            with gr.Row():
                user_msg = gr.Textbox(placeholder="Haz una pregunta...")
                send_btn = gr.Button("Enviar")

    file_input.change(
        fn=process_pdf,
        inputs=[file_input, highlight_checkbox],
        outputs=[image_output, page_info, status_text, summary_output]
    )

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

    send_btn.click(
        fn=handle_user_message,
        inputs=[user_msg, chatbot],
        outputs=[chatbot]
    )

if __name__ == "__main__":
    demo.launch()