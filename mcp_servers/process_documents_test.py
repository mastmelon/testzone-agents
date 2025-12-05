# test_process_documents.py
from mcp_server_2 import process_documents, mcp_log

if __name__ == "__main__":
    mcp_log("INFO", "test_process_documents.py", "Running process_documents directly")
    process_documents()
    mcp_log("INFO", "test_process_documents.py", "process_documents finished successfully")
