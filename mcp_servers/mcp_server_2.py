import hashlib
import json
import os.path
import re
import signal
import sys
from pathlib import Path

import faiss
import pymupdf4llm
from mcp.server import FastMCP


def handle_signal(signum, frame):
    mcp_log("ERROR", "mcp_server_2.py", f"Received signal {signum} in PID {os.getpid()}")
    sys.exit(1)


for sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, handle_signal)

from models import FilePathInput, MarkdownOutput

mcp = FastMCP("Documents")

EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_URL = "http://localhost:11434/api/generate"
EMBED_MODEL = "nomic-embed-text"
GEMMA_MODEL = "gemma3:12b"
PHI_MODEL = "phi4:latest"
QWEN_MODEL = "qwen2.5:32b-instruct-q4_0 "
CHUNK_SIZE = 256
CHUNK_OVERLAP = 40
MAX_CHUNK_LENGTH = 512  # characters
TOP_K = 3  # FAISS top-K matches
ROOT = Path(__file__).parent.resolve()


@mcp.tool()
def extract_pdf(input: FilePathInput) -> MarkdownOutput:
    """Convert PDF to markdown."""

    if not os.path.exists(input.file_path):
        return MarkdownOutput(markdown=f"File not found: {input.file_path}")

    ROOT = Path(__file__).parent.resolve()
    global_image_dir = ROOT / "documents" / "images"
    global_image_dir.mkdir(parents=True, exist_ok=True)

    # Actual markdown with relative image paths
    markdown = pymupdf4llm.to_markdown(
        input.file_path,
        write_images=True,
        image_path=str(global_image_dir)
    )

    # Re-point image links in the markdown
    markdown = re.sub(
        r'!\[\]\((.*?/images/)([^)]+)\)',
        r'![](images/\2)',
        markdown.replace("\\", "/")
    )

    markdown = replace_images_with_captions(markdown)
    return MarkdownOutput(markdown=markdown)


def replace_images_with_captions(markdown: str) -> str:
    """How it works

    Finds all markdown images: uses regex r'!\[(.*?)\]\((.*?)\)' to match ![alt text](image_path_or_url).
    For each match:
    Extracts the alt text and image source (path or URL).
    Calls caption_image() to generate a caption via the Gemma model.
    If the image is local (not a URL), deletes the file after captioning.
    Replaces the image markdown with **Image:** {caption}.
    Returns the modified markdown with images replaced by captions."""

    def replace(match):
        alt, src = match.group(1), match.group(2)
        try:
            caption = caption_image(src)
            # Attempt to delete only if local and file exists
            if not src.startswith("http"):
                img_path = Path(__file__).parent / "documents" / src
                if img_path.exists():
                    img_path.unlink()
                    mcp_log("INFO", "mcp_server_2.py", f"🗑️ Deleted image after captioning: {img_path}")
            return f"**Image:** {caption}"
        except Exception as e:
            mcp_log("WARN", "mcp_server_2.py" f"Image deletion failed: {e}")
            return f"[Image could not be processed: {src}]"

    return re.sub(r'!\[(.*?)\]\((.*?)\)', replace, markdown)


def caption_image(img_url_or_path: str) -> str:
    mcp_log("INFO", "mcp_server_2.py", f"Attempting to caption image: {img_url_or_path}")
    # TODO - Complete method
    return "dummy caption"


def mcp_log(level: str, filename: str, message: str) -> None:
    sys.stderr.write(f"{level}: {filename}: {message}\n")
    sys.stderr.flush()


def process_documents():
    """Process documents and create FAISS index using unified multimodal strategy."""
    mcp_log("INFO", "mcp_server_2.py", "Indexing documents with unified RAG pipeline...")
    DOC_PATH = ROOT / "documents"
    INDEX_CACHE = ROOT / "faiss_index"
    INDEX_CACHE.mkdir(exist_ok=True)
    INDEX_FILE = INDEX_CACHE / "index.bin"
    METADATA_FILE = INDEX_CACHE / "metadata.json"  # chuck details
    CACHE_FILE = INDEX_CACHE / "doc_index_cache.json"

    def file_hash(path):
        return hashlib.md5(Path(path).read_bytes()).hexdigest()


    index = faiss.read_index(str(INDEX_FILE)) if INDEX_FILE.exists() else {}
    metadata = json.loads(METADATA_FILE.read_text()) if METADATA_FILE.exists() else []
    CACHE_META = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}

    if not DOC_PATH.exists() or not DOC_PATH.is_dir():
        raise FileNotFoundError(
            f"Documents directory not found: {DOC_PATH}\n"
            f"Please create the directory or check the path."
        )

    for file in DOC_PATH.glob("*"):
        if not file.is_file():
            mcp_log("INFO", "mcp_server_2.py", f"here: {file.name}")
            continue

        try:
            fhash = file_hash(file)
            if file.name in CACHE_META and CACHE_META[file.name] == fhash:
                mcp_log("INFO", "mcp_server_2.py", f"Skipping embedding for unchanged file: {file.name}")
                continue

            mcp_log("INFO", "mcp_server_2.py", f"Embedding file: {file.name}")

            file_extension = file.suffix.lower()
            markdown = ""

            if file_extension == ".pdf":
                mcp_log("INFO", "mcp_server_2.py", f"Using MuPDF4LLM to extract {file.name}")
                markdown = extract_pdf(FilePathInput(file_path=str(file))).markdown

            # TODO - add rest of the conditions here and complete embedding logic

        except Exception as e:
            mcp_log("ERROR", "mcp_server_2.py", f"Failed to extract and embed {file.name}: {e}")


if __name__ == "__main__":
    mcp_log("INFO", "mcp_server_2.py", "Starting mcp_server_2 server...")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="stdio")
        mcp_log("INFO", "mcp_server_2.py", "Shutting down mcp_server_2 server")
        # Start the server in a separate thread
        # import threading
        #
        # server_thread = threading.Thread(target=lambda: mcp.run(transport="stdio"))
        # server_thread.daemon = True
        # server_thread.start()

        # Wait a moment for the server to start
        # time.sleep(2)

        # Process documents after server is running
        # process_documents()

        # try:
        #     while True:
        #         time.sleep(1)
        # except KeyboardInterrupt:
        #     print("\nShutting down mcp_server_2...")
