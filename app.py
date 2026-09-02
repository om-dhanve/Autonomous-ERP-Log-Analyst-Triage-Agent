import gradio as gr
from openai import OpenAI
import os
import re

client = OpenAI (
    api_key = os.environ["OPENAI_API_KEY"],
    base_url = "http://localhost:8000/v1",
)
models = client.models.list()
print(f"Connected to : {models.data[0].id}")

###Extract error functions for extracting error snippet from log file
def extract_errors(path_logfile,keywords=["SEVERE","ERROR","COB0000012","Zombie","Timeout"],context_lines=10):
    try:
        with open(path_logfile,'r') as logfile : 
            log_lines = logfile.readlines()
    except Exception as ee : 
        return f"Error occured {ee}"

    for i,line in enumerate(log_lines) : 
        if any(keyword in line for keyword in keywords):
            first = max(0,i - context_lines)
            last = min(len(log_lines),i + context_lines)

            log_block = "".join(log_lines[first:last])
            return f"Error detected at line - {i} -- \n{log_block}"
    
    return f"No error found in file,last 100 lines : {log_lines[-30:]}" 

###Core Agent function
def analyze_jde_log(log_file):
    if log_file is None:
        return "Please upload a log file.","No file uploaded"

    log_content = extract_errors(log_file.name)


    ###System prompt for LLM
    system_prompt = """You are a very experienced and elite Oracle JD Edwards CNC administrator.
    Your responsibility is to read provided log files, pinpoint the exact location of errors/issues and provide a remediation plan.
    
    When analyzing the provided log snippet : 
    1. Identify the impacted JDE architecture component failing (eg.database,AIS Servers,Integrations,UBE Kernel)
    2. Provide the root cause of this error or failure. If unsure provide probable root cause. (eg.Expired password,Pending ESU Upgrade, Invalid connection, Server timeout)
    3. Provide a step by step action plan to fix the error from a CNC Admin perspective using JDE Servermanager, SQL, fast path, JDE Fatclient-webclient etc.
    
    Do not give generic IT advice. Be specific to JD Edwards Tools Release architecture.
    """
    ###Sending log file snippet to LLM for inference
    
    try:
        responses = client.chat.completions.create(
            model = models.data[0].id,
            messages = [
                {"role" : "system","content" : system_prompt},
                {"role" : "user" , "content" : f"Analyze the log file attached and perform In depth Root cause analysis \n\n{log_content}"},
            ],
            temperature = 0.3,    
        ) 
        raw = responses.choices[0].message.content
        analysis = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    except Exception as e : 
        analysis = f"Error during model inference: {e}"
    
    return log_content[50:],analysis
    ###Agent response

with gr.Blocks(theme=gr.Theme.from_hub("harsh8001/skymist")) as app:
    gr.HTML(value="<h1>Autonomous JDE Log Analyst & Triage Agent</h1>")
    gr.HTML(value="<h3>Upload your error log file. The AI Agent will isolate the errors and generate an RCA</h3>")

    with gr.Row():
        with gr.Column(scale=1):
            log_upload = gr.File(label="Upload JDE Log (.txt or .log)")
            analysis_button = gr.Button("Analyze Log",variant="primary")
            with gr.Accordion("View Raw Extracted Log content",open=False):
                content_output = gr.Textbox(label = "Extracted Error Snippet",lines=15)
                
        with gr.Column(scale=2):
            gr.HTML(value="<h3>Agent Root Cause analysis : </h3>")
            RCA_Output = gr.Markdown("*Waiting for log upload and analysis...*")
    
    analysis_button.click(
        fn=analyze_jde_log,
        inputs=log_upload,
        outputs=[content_output,RCA_Output]
    )

app.launch(inline=True, share=True)
