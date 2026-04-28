import fitz

def locate_targets_globally(pdf_path, targets):
    doc = fitz.open(pdf_path)
    print(f"\n--- GLOBAL SURGICAL TARGETING ---")
    
    found_coords = {}

    for page_num in range(len(doc)):
        page = doc[page_num]
        for item in targets:
            instances = page.search_for(item)
            if instances:
                rect = instances[0]
                coords = (round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2))
                print(f"PAGE {page_num + 1} | TARGET: '{item}' | COORDS: {coords}")
                found_coords[item] = {"page": page_num, "rect": coords}
                
    return found_coords

my_targets = [
    "Academic Year: 2025-26", 
    "Semester: IV", 
    "Class / Div / Branch: S.E./ A / CSE(AI&ML)", 
    "Subject: Database Management System Lab", 
    "Name of Instructor: Prof. Susmitha Madineni",
    "Date of Performance:",
    "Date of Submission:",
    "Conclusion:"
]

locate_targets_globally(r"D:\Pdf_Editor\exp1.pdf", my_targets)