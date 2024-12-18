import gradio as gr
from helpers.extractor import Website
from validator.validator import validate_url
from helpers.openai import OpenApi
from helpers.ollama import Ollama

openAI = OpenApi()
llama = Ollama()

def generateWebsiteSummary(name, url, model, tone):
    print("Started")
    if(not name or not url or not model or not tone):
        return "Please Select all the options"
    if not validate_url(url):
        return "Please Enter the Correct URL"
    
    website_details = Website(url)
    openai_details = "<span style='color: orange;'>Hope You liked the response Llama Gave!</span>"
    llama_details = "<span style='color: orange;'>Hope You liked the response OpenAPI Gave!</span>"

    if model == "OpenAI":
        openai_details = "# <span style='color: orange;'>OpenAI Response:</span> \n\n\n" + openAI.create_brochure(name, website_details, tone == "Casual")
        return openai_details

    if model == "Llama":
        llama_details = "# <span style='color: orange;'>Llama Response:</span> \n\n\n" + llama.create_brochure(name, website_details, tone == "Casual")
        return llama_details
    # # print(openai_details)
    # return openai_details, llama_details

# def build_ui():
#     print("here")
#     demo = gr.Interface(
#         fn=generateWebsiteSummary,
#         inputs=["text"],
#         outputs="markdown",
#         title="Website Summary",
#         description="Website Summarizer!"
#     )
#     return demo

def build_ui():
    print("Initializing the UI...")
    with gr.Blocks() as demo:
        # Add a title and description
        gr.Markdown("# Website Summary\n\n### Summarize your favorite websites in seconds!")
        
        with gr.Row():
            # Input and output side by side
            with gr.Column():
                name_input = gr.Textbox(
                    label="Enter Website Name",
                    placeholder="Paste the name of the website here...",
                    lines=1
                )
                link_input = gr.Textbox(
                    label="Enter Website Link",
                    placeholder="Paste the link of the website here...",
                    lines=1
                )
                model_radio = gr.Radio(
                    choices=["OpenAI", "Llama"],
                    label="Select which Model to Use"
                )
                tone_radio = gr.Radio(
                    choices=["Formal", "Casual"],
                    label="Select which Tone to Use"
                )
                # openAI_checkbox = gr.Checkbox(label="Use OpenAI")
                # llama_checkbox = gr.Checkbox(label="Use Llama")
            with gr.Column():
                markdown_output = gr.Markdown(label="Summary Output", value="Response will show here!")
        
        # Submit button to trigger function
        submit_btn = gr.Button("Generate Summary")
        
        # Link the input and output to the function
        submit_btn.click(fn=generateWebsiteSummary, inputs=[name_input, link_input, model_radio, tone_radio], outputs=[markdown_output], show_progress='full')

    return demo


    