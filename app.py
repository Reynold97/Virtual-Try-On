import gradio as gr
import replicate
import requests
from PIL import Image
from dotenv import load_dotenv
import io
import os
import tempfile

load_dotenv()

def process_virtual_tryon(garment_image, human_image, description, category,
                         crop, seed, steps, force_dc, mask_only):
    try:
        # Create temporary files with unique names
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_garment:
            garment_path = temp_garment.name
            if isinstance(garment_image, str):
                response = requests.get(garment_image)
                temp_garment.write(response.content)
            else:
                Image.fromarray(garment_image).save(garment_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_human:
            human_path = temp_human.name
            if isinstance(human_image, str):
                response = requests.get(human_image)
                temp_human.write(response.content)
            else:
                Image.fromarray(human_image).save(human_path)

        # Prepare input for Replicate
        with open(garment_path, 'rb') as garm_file, open(human_path, 'rb') as human_file:
            input_data = {
                "garm_img": garm_file,
                "human_img": human_file,
                "garment_des": description,
                "category": category,
                "crop": crop,
                "seed": seed,
                "steps": steps,
                "force_dc": force_dc,
                "mask_only": mask_only
            }

            # Run the model
            output = replicate.run(
                "cuuupid/idm-vton:c871bb9b046607b680449ecbae55fd8c6d945e0a1948644bf2361b3d021d3ff4",
                input=input_data
            )

            # Save the result to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_output:
                result_path = temp_output.name
                temp_output.write(output.read())

        # Clean up temporary files
        try:
            os.unlink(garment_path)
            os.unlink(human_path)
        except Exception as e:
            print(f"Warning: Could not delete temporary files: {e}")

        # Return the result
        result_image = Image.open(result_path)
        try:
            os.unlink(result_path)
        except Exception as e:
            print(f"Warning: Could not delete result file: {e}")
            
        return result_image

    except Exception as e:
        print(f"Error in process_virtual_tryon: {str(e)}")
        return f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Virtual Try-On Demo")
    
    # First Row: Input Images
    with gr.Row():
        garment_input = gr.Image(label="Upload Garment Image", type="numpy")
        human_input = gr.Image(label="Upload Human Image", type="numpy")
    
    # Second Row: Configuration
    with gr.Row():
        with gr.Column():
            # Basic settings
            description_input = gr.Textbox(
                label="Garment Description", 
                placeholder="Enter garment description...",
                scale=2
            )
            category_input = gr.Dropdown(
                choices=["upper_body", "lower_body", "dress"],
                value="upper_body",
                label="Category",
                scale=1
            )
            
            # Advanced settings in a collapsible section
            with gr.Accordion("Advanced Settings", open=False):
                with gr.Row():
                    crop_input = gr.Checkbox(label="Crop", value=False)
                    force_dc_input = gr.Checkbox(label="Force DC", value=False)
                    mask_only_input = gr.Checkbox(label="Mask Only", value=False)
                with gr.Row():
                    seed_input = gr.Number(label="Seed", value=42, precision=0)
                    steps_input = gr.Slider(
                        minimum=1, 
                        maximum=40, 
                        value=40, 
                        step=1, 
                        label="Steps"
                    )
    
    # Third Row: Generate Button and Result
    with gr.Row():
        with gr.Column(scale=1):
            submit_btn = gr.Button("Generate Try-On", size="lg")
        with gr.Column(scale=4):
            output_image = gr.Image(label="Result")
    
    submit_btn.click(
        fn=process_virtual_tryon,
        inputs=[
            garment_input,
            human_input,
            description_input,
            category_input,
            crop_input,
            seed_input,
            steps_input,
            force_dc_input,
            mask_only_input
        ],
        outputs=output_image
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        enable_queue=False,  # Disable queue
        show_api=False,      # Disable API interface
        show_tips=False      # Disable tips
    )