# Autonomous JDE Log Analyst & Triage Agent

An AI‑powered log analysis tool for Enterprise resource planning software (In the use case Oracle JD Edwards EnterpriseOne). Upload your log files and the agent extracts error snippets, performs a root cause analysis (RCA), and provides step‑by‑step remediation – all through a local web interface.

The agent uses a local LLM (Qwen3‑30B‑A3B) served via vLLM, with a Gradio frontend. It was originally built for AMD GPUs but works on any platform supported by vLLM.

----
## Demo  

https://github.com/user-attachments/assets/894fc985-db96-4897-9ae6-0c10e59f0947
*Attached above is a short video demonstrating the working of this project*

---
## Features

- **Error extraction** – scans logs for keywords (`SEVERE`, `ERROR`, `COB0000012`, `Zombie`, `Timeout`) and returns the error with surrounding context.
- **Root cause analysis** – uses a large language model which has strong performance in coding and debugging for Enterprise resource planning errors. 
- **Actionable remediation** – provides specific CNC steps using JDE Server Manager, SQL, Fast Path, or Fat Client.
- **Clean Markdown output** – easy to read with headers and bullet points.
- **Simple web UI** – built with Gradio; upload a file and get analysis instantly.
- **Local & private** – runs entirely on your hardware; no data leaves your environment.

---
## Prerequisites

- Python 3.10+
- vLLM (for serving the model)
- GPU with at least 24 GB VRAM (recommended for Qwen3‑30B‑A3B)
- Hugging Face access to download the model (`Qwen/Qwen3-30B-A3B`)

> **AMD GPU users**: set `VLLM_USE_TRITON_FLASH_ATTN=0` when starting vLLM (see launch command below).

---
## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/om-dhanve/Autonomous-ERP-Log-Analyst-Triage-Agent.git
   cd Autonomous-ERP-Log-Analyst-Triage-Agent
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   Create a `requirements.txt` file with:
   ```
   gradio
   openai
   ```
   Then run:
   ```bash
   pip install -r requirements.txt
   ```

   For production, it’s recommended to run vLLM in a separate environment to avoid dependency conflicts.

---
## Starting the vLLM Server

Launch the vLLM server with the following command (adjust `--api-key` as needed):

```bash
VLLM_USE_TRITON_FLASH_ATTN=0 \
vllm serve Qwen/Qwen3-30B-A3B \
    --served-model-name Qwen3-30B-A3B \
    --api-key Your desired api KEY \
    --port 8000 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --trust-remote-code
```

---
## Running the Gradio App

1. **Set the API key** (must match the one used in the vLLM server):
   ```bash
   export OPENAI_API_KEY=Your desired api KEY   # On Windows: set  OPENAI_API_KEY=default set as abc-123
   ```

2. **Run the app**:
   ```bash
   python app.py
   ```

3. Open the local URL (usually `http://127.0.0.1:7860`) in your browser. Upload a log file (`.txt` or `.log`) and click **“Analyze Log”**.

---
## Configuration

| Environment Variable | Description                                | Default                    |
| -------------------- | ------------------------------------------ | -------------------------- |
| `OPENAI_API_KEY`     | API key for vLLM authentication            | `abc-123`                  |
| `BASE_URL`           | vLLM server endpoint (hardcoded in app.py) | `http://localhost:8000/v1` |
You can also modify the `keywords` and `context_lines` inside the `extract_errors` function in `app.py`.

---
## Project Structure

```
jde-log-analyzer/
├── app.py                 # Main Gradio application
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---
## Troubleshooting

- **`OpenAIError: No API key provided`** – ensure `OPENAI_API_KEY` is set and matches `--api-key` in the vLLM command.
- **vLLM server not responding** – verify the server is running and port 8000 is accessible.
- **Out‑of‑memory errors** – Qwen3‑30B‑A3B requires ~24 GB VRAM; consider a smaller model or enable quantization.
- **`<think>` blocks in output** – the app strips them automatically; if you still see them, adjust the regex in `app.py`.

---
## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---
