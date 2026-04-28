import fitz # This is the PyMuPDF library we installed

def get_coordinates(pdf_path):
    try:
        # Step A: Open the PDF file
        doc = fitz.open("exp1.pdf")
        
        # Step B: Select the first page (index 0)
        page = doc[0] 
        
        # Step C: Extract text blocks (this includes content and position)
        blocks = page.get_text("blocks")
        
        print(f"\n--- COORDINATE MAP FOR {pdf_path} ---")
        print(f"{'Text Found':<35} | {'(x0, y0, x1, y1)':<30}")
        print("-" * 75)
        
        for b in blocks:
            # b[4] is the text content
            # b[0:4] are the coordinates (Left, Top, Right, Bottom)
            text_content = b[4].strip().replace('\n', ' ')
            coords = tuple(round(c, 2) for c in b[0:4])
            
            # We only want to see lines that actually have text
            if text_content:
                print(f"{text_content[:33]:<35} | {coords}")
                
    except Exception as e:
        print(f"Error: Could not find the file. Make sure it's in the same folder. Detail: {e}")

# Trigger the function
get_coordinates("exp1.pdf")
