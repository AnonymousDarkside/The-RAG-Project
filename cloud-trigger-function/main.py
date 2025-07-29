import functions_framework
from google.cloud import storage
import pymupdf
import io
from cloudevents.http import CloudEvent

@functions_framework.cloud_event
# This function is triggered by a change in a Cloud Storage bucket.
def process_research_paper(cloud_event: CloudEvent):

    storage_client = storage.Client()
    file_data = cloud_event.data

    bucket_name = file_data["bucket"]
    file_name = file_data["name"]

    # Ensure we only process files in the correct folder and they are PDFs
    if not file_name.startswith('research_papers/') or not file_name.lower().endswith('.pdf'):
        print(f"Skipping file {file_name} as it is not a target PDF.")
        return

    print(f"Processing PDF: {file_name}")

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # PDF content to memory download
    pdf_content = blob.download_as_bytes()

    # Open the PDF from memory
    doc = pymupdf.open(stream=pdf_content, filetype="pdf")

    full_text = ""
    for page in doc:
        full_text += page.get_text()

    doc.close()

    print(f"Extracted {len(full_text)} characters from {file_name}.")