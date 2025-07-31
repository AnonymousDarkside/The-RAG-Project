import functions_framework
import pymupdf
from google.cloud import storage
from sentence_transformers import SentenceTransformer
from cloudevents.http import CloudEvent
import os

# --- Global Initialization ---
# storage client and embedding model
storage_client = storage.Client()

# load the model once and reuse it.
# model will be downloaded to the /tmp directory in the Cloud Function environment.
print("Initializing SentenceTransformer model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model initialized successfully.")


@functions_framework.cloud_event
def process_pdf_and_embed(cloud_event: CloudEvent):
    """
    This Cloud Function is triggered by a file upload to a Google Cloud Storage bucket(research-papers-arxiv).
    It performs the following steps:
    1. Validates that the uploaded file is a PDF in the correct directory.
    2. Downloads the PDF file from the bucket.
    3. Extracts the full text content from the PDF.
    4. Chunks the extracted text into smaller, manageable pieces.
    5. Generates vector embeddings for each text chunk using a SentenceTransformer model.
    6. (to be added)The next step would be to store these embeddings in a vector database.
    """
    # --- 1. Event Data Extraction ---
    try:
        file_data = cloud_event.data
        bucket_name = file_data["bucket"]
        file_name = file_data["name"]
    except KeyError as e:
        print(f"Error: Missing expected key in CloudEvent data: {e}")
        return f"Bad request: missing {e}", 400

    # --- 2. File Validation ---
    # Ensure we only process PDF files in the 'research_papers/' folder.
    # This prevents the function from triggering on other file types or in other folders.
    if not file_name.startswith('research_papers/') or not file_name.lower().endswith('.pdf'):
        print(f"Skipping file '{file_name}' as it is not a target PDF in the 'research_papers/' directory.")
        return 
    print(f"Processing PDF: gs://{bucket_name}/{file_name}")

    # --- 3. PDF Download and Text Extraction ---
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Download PDF content into memory as bytes.
        pdf_content = blob.download_as_bytes()

        # Open the PDF from the in-memory bytes.
        doc = pymupdf.open(stream=pdf_content, filetype="pdf")

        full_text = ""
        for page_num, page in enumerate(doc):
            full_text += page.get_text()
        doc.close()

        if not full_text.strip():
            print(f"Warning: No text could be extracted from {file_name}.")
            return

        print(f"Extracted {len(full_text)} characters from {file_name}.")

    except Exception as e:
        print(f"Error processing PDF {file_name}: {e}")
        return # Exit on error

    # --- 4. Text Chunking ---
    # Split the extracted text into chunks based on double newlines.
    chunks = full_text.split('\n\n')
    
    # Filter out very small or empty chunks to reduce noise.
    chunks = [chunk.strip() for chunk in chunks if len(chunk.strip()) > 100]
    
    if not chunks:
        print(f"Could not create any valid text chunks from {file_name}.")
        return

    print(f"Split text into {len(chunks)} chunks.")

    # --- 5. Create Embeddings ---
    try:
        print("Generating embeddings for text chunks...")
        embeddings = embedding_model.encode(chunks)
        print(f"Successfully created {len(embeddings)} embeddings of shape {embeddings.shape}.")

        # --- 6. Store Embeddings (Next Step) ---
        # Here you would add the code to connect to your vector database (e.g., Milvus, Pinecone, Vertex AI Vector Search)
        # and store the 'chunks' along with their corresponding 'embeddings'.
        # For example: vector_db.insert(collection_name="papers", texts=chunks, embeddings=embeddings)
        print("Next step: Store these chunks and embeddings in a vector database.")

    except Exception as e:
        print(f"Error generating or storing embeddings: {e}")