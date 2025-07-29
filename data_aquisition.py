import arxiv
import os
import re
import time

# --- Config ---
# Directory to save the downloaded PDF's
OUTPUT_DIR = "research_papers"

# Topics to search for. Use arXiv's query format.
# 'ti' for title, 'au' for author, 'abs' for abstract, 'cat' for category.
# 'cs.LG' is "Computer Science - Learning"
# 'cs.DC' is "Computer Science - Distributed, Parallel, and Cluster Computing"
SEARCH_QUERIES = [
    '"Transformer model" AND cat:cs.LG',
    '"feature store" AND cat:cs.LG',
    '"Docker" AND cat:cs.LG',
    '"Python" AND cat:cs.LG',
    '"Kubernetes for machine learning" AND cat:cs.DC',
    '"Diffusion model" AND cat:cs.LG'
]

# Max number of papers to download per query
MAX_RESULTS_PER_QUERY = 50

# --- Script Logic ---

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

for query in SEARCH_QUERIES:
    print(f"--- Searching for: '{query}' ---")
    
    search = arxiv.Search(
      query = query,
      max_results = MAX_RESULTS_PER_QUERY,
      sort_by = arxiv.SortCriterion.Relevance
    )
    
    for result in search.results():
        try:
            # Create a clean filename
            # Example: 2106.07447v1-Self-Supervised-Learning-with-SwAV.pdf
            paper_id = result.entry_id.split('/')[-1]
            # Sanitize title by removing invalid filename characters
            paper_title = re.sub(r'[<>:"/\\|?*]', '', result.title).replace(" ", "-")
            filename = f"{paper_id}-{paper_title[:50]}.pdf" # Truncate long titles
            filepath = os.path.join(OUTPUT_DIR, filename)

            if not os.path.exists(filepath):
                print(f"Downloading: {result.title}")
                result.download_pdf(dirpath=OUTPUT_DIR, filename=filename)
                
                # IMPORTANT: Be a good citizen and don't spam the API
                # A 3-5 second delay between downloads is polite
                time.sleep(3) 
            else:
                print(f"Skipping (already exists): {result.title}")

        except Exception as e:
            print(f"An error occurred while downloading '{result.title}': {e}")
            
    print(f"--- Finished query: '{query}' ---\n")

print("All downloads complete.")