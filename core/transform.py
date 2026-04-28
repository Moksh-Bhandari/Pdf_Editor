import fitz  # PyMuPDF

def transform_report(input_pdf, output_pdf, data):
    """
    Surgically updates the APSIT experiment template with new data.
    Uses 'tibo' (Times-Bold) for headers and 'tiro' (Times-Roman) for paragraphs.
    """
    try:
        doc = fitz.open(input_pdf)
        page1 = doc[0] 

        # --- DYNAMIC CONFIGURATION ---
        # We use the coordinates you sniped to build the replacement map.
        # Rect format: [x0, y0, x1, y1]
        CONFIG = {
            "Academic Year": {"rect": [40.68, 158.29, 200.0, 171.57], "val": f"Academic Year: {data['year']}"},
            "Semester":      {"rect": [40.68, 172.09, 150.0, 185.37], "val": f"Semester: {data['sem']}"},
            "Class":         {"rect": [40.68, 185.89, 310.0, 199.17], "val": f"Class / Div / Branch: {data['class']}"},
            "Subject":       {"rect": [40.68, 199.69, 310.0, 212.97], "val": f"Subject: {data['subject']}"},
            "Instructor":    {"rect": [40.68, 213.49, 320.0, 226.77], "val": f"Name of Instructor: {data['instructor']}"},
            "Perf_Date":     {"rect": [328.63, 199.69, 560.0, 212.97], "val": f"Date of Performance: {data['p_date']}"},
            "Sub_Date":      {"rect": [328.63, 213.49, 560.0, 226.77], "val": f"Date of Submission: {data['s_date']}"},
            "Name":          {"rect": [421.57, 158.29, 585.0, 171.57], "val": data['name']},
            "ID":            {"rect": [392.14, 172.94, 510.0, 185.16], "val": data['id']},
            "Roll":          {"rect": [328.75, 185.89, 450.0, 199.17], "val": f"Roll No: {data['roll']}"},
            
            # Paragraph Fields (Wiped and rewritten as wrapped textboxes)
            "Aim":           {"rect": [40.68, 280.84, 520.0, 315.0],  "val": data['aim']},
            "Outcomes":      {"rect": [40.68, 348.64, 520.0, 385.0],  "val": data['outcomes']}
        }

        # PHASE 1: THE ERASER (Redaction)
        # Clears all old content on Page 1 before writing new data
        for field in CONFIG.values():
            page1.add_redact_annot(fitz.Rect(field["rect"]), fill=(1, 1, 1))
        page1.apply_redactions()

        # PHASE 2: THE PAINTER (Insertion)
        for key, field in CONFIG.items():
            rect = fitz.Rect(field["rect"])
            if key in ["Aim", "Outcomes"]:
                # Use tiro (Regular) for wrapped paragraph blocks
                page1.insert_textbox(rect, field["val"], fontsize=11, fontname="tiro", color=(0,0,0))
            else:
                # Use tibo (Bold) for single-line headers
                page1.insert_text((rect.x0, rect.y1 - 1), field["val"], fontsize=12, fontname="tibo", color=(0,0,0))

        # PHASE 3: CONCLUSION (Page 2 Logic)
        if len(doc) > 1:
            page2 = doc[1]
            # Placeholder Rect - Update this once you have the Page 2 Sniper coords!
            conc_rect = fitz.Rect(40.68, 700.0, 520.0, 750.0) 
            
            page2.add_redact_annot(conc_rect, fill=(1,1,1))
            page2.apply_redactions()
            
            # FIXED: Corrected fontname to 'tiro' (Times-Roman)
            page2.insert_textbox(
                conc_rect, 
                f"Conclusion: {data['conclusion']}", 
                fontsize=11, 
                fontname="tiro", 
                color=(0,0,0)
            )

        # FINAL SAVE
        doc.save(output_pdf)
        print(f"\n--- BUILD SUCCESSFUL ---")
        print(f"File Saved: {output_pdf}")
        
    except Exception as e:
        print(f"\n--- BUILD FAILED ---")
        print(f"Error Detail: {e}")

# --- INPUT DATA MODULE ---
# This data will eventually come from your web form.
user_input = {
    "year": "2025-26",
    "sem": "IV",
    "class": "S.E./ A / CSE(AI&ML)",
    "subject": "Database Management System Lab",
    "instructor": "Moksh Bhandari",
    "p_date": "22/04/2026",
    "s_date": "26/04/2026",
    "name": "Siddharth Jain",
    "id": "24109999",
    "roll": "45",
    "aim": "become the beast version of mine .",
    "outcomes": "1. Identify the case study and detail statement of problem. 2. Design an Entity-Relationship (ER) / Extended Entity-Relationship (EER) Model.",
    "conclusion": "ER diagrams are essential for database design. They help identify entities, attributes, and relationships, providing a clear roadmap for creating the database schema."
}

# --- TRIGGER ---
transform_report("exp1.pdf", "exp1_final_complete.pdf", user_input)