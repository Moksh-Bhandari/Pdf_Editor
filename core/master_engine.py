import fitz  # PyMuPDF

def finalize_portfolio_report(input_pdf, output_pdf, data, image_paths):
    """
    Surgical Block-Wipe Engine. 
    Vaporizes background artifacts and rebuilds the report with total precision,
    ensuring all headings and data are restored after the wipe.
    """
    try:
        doc = fitz.open(input_pdf)
        
        # --- CONSTANTS & BOUNDARIES ---
        HEADER_FLOOR = 155  # We never touch anything above this line 
        FOOTER_CEILING = 750 # We never touch anything below this line
        
        # --- 1. DATA REBUILD MAP (Labels + Values) ---
        # We manually re-inject the static labels so they are never missing.
        TEXT_CONFIG = {
            # Institutional Block (Left side)
            "Year":       {"r": [40.68, 158.29, 210, 171.57], "v": f"Academic Year: {data['year']}", "f": "tibo", "s": 12},
            "Sem":        {"r": [40.68, 172.09, 150, 185.37], "v": f"Semester: {data['sem']}", "f": "tibo", "s": 12},
            "Class":      {"r": [40.68, 185.89, 315, 199.17], "v": f"Class / Div / Branch: {data['class']}", "f": "tibo", "s": 12},
            "Subj":       {"r": [40.68, 199.69, 315, 212.97], "v": f"Subject: {data['subject']}", "f": "tibo", "s": 12},
            "Inst":       {"r": [40.68, 213.49, 325, 226.77], "v": f"Name of Instructor: {data['instructor']}", "f": "tibo", "s": 12},
            
            # Institutional Block (Right side)
            "P_Date":     {"r": [328.63, 199.69, 565, 212.97], "v": f"Date of Performance: {data['p_date']}", "f": "tibo", "s": 12},
            "S_Date":     {"r": [328.63, 213.49, 565, 226.77], "v": f"Date of Submission: {data['s_date']}", "f": "tibo", "s": 12},
            "Roll":       {"r": [328.75, 185.89, 460, 199.17], "v": f"Roll No: {data['roll']}", "f": "tibo", "s": 12},

            # IDENTITY LABELS + VALUES (Restoring headings for Student Name and ID) 
            "L_Name":     {"r": [328.75, 158.29, 430, 171.57], "v": "Name of Student:", "f": "tibo", "s": 12},
            "Val_Name":   {"r": [420, 158.29, 595, 171.57], "v": data['name'], "f": "tibo", "s": 12},

            "L_ID":       {"r": [328.75, 172.94, 405, 185.16], "v": "Student ID:", "f": "tibo", "s": 12},
            "Val_ID":     {"r": [390, 172.94, 530, 185.16], "v": data['id'], "f": "tibo", "s": 12},
            
            # Content Block Labels + Values
            "Exp_No": {"r": [217
            , 232, 455, 248], "v": f"Experiment No. {data['exp_no']}", "f": "tibo", "s": 13},
            "L_Aim": {"r": [40.68, 260, 100, 275], "v": "Aim:", "f": "tibo", "s": 12},
            "Val_Aim": {"r": [40.68, 276, 540, 305], "v": data['aim'], "f": "tiro", "s": 11},
            "L_Outcomes": {"r": [40.68, 312, 200, 327], "v": "Lab Outcomes:", "f": "tibo", "s": 12},
            "Val_Outcomes": {"r": [40.68, 328, 540, 372], "v": data['outcomes'], "f": "tiro", "s": 11},
            "L_Output": {"r": [40.68, 378, 150, 395], "v": "Output:", "f": "tibo", "s": 12}
        }

        # --- 2. THE VAPORIZER (Redaction) ---
        for i in range(len(doc)):
            page = doc[i]
            page.clean_contents()
            
            if i == 0:
                # WIPE 1: Identity Area
                page.add_redact_annot(fitz.Rect(35, 155, 600, 230), fill=(1,1,1))
                # WIPE 2: Content Area (Removes Duplicate labels/Artifacts)
                page.add_redact_annot(fitz.Rect(35, 230, 600, 420), fill=(1,1,1))
                # WIPE 3: Output Area
                page.add_redact_annot(fitz.Rect(35, 430, 600, FOOTER_CEILING), fill=(1,1,1))
            else:
                page.add_redact_annot(fitz.Rect(35, 155, 600, FOOTER_CEILING), fill=(1,1,1))
            
            page.apply_redactions()

        # --- 3. REBUILDING PAGE 1 ---
        page1 = doc[0]
        # Draw the anchor line
        page1.draw_line(fitz.Point(35, 228), fitz.Point(565, 228), color=(0,0,0), width=1.5)
        
        for key, f in TEXT_CONFIG.items():
            rect = fitz.Rect(f["r"])
            # Use textbox for multiline, text for single line alignment
            if key in ["Val_Aim", "Val_Outcomes"]:
                page1.insert_textbox(rect, f["v"], fontsize=f["s"], fontname=f["f"])
            else:
                page1.insert_text((rect.x0, rect.y1 - 1), f["v"], fontsize=f["s"], fontname=f["f"])

        # --- 4. DYNAMIC IMAGE & CLONING ENGINE ---
        current_y = 440  # Under 'Output:'
        curr_p_idx = 0
        
        for img_path in image_paths:
            if current_y + 280 > FOOTER_CEILING:
                curr_p_idx += 1
                if curr_p_idx >= len(doc): doc.fullcopy_page(1)
                target = doc[curr_p_idx]
                target.clean_contents()
                target.add_redact_annot(fitz.Rect(35, 155, 600, FOOTER_CEILING), fill=(1,1,1))
                target.apply_redactions()
                current_y = 165
            
            img_rect = fitz.Rect(50, current_y, 540, current_y + 280)
            doc[curr_p_idx].insert_image(img_rect, filename=img_path, keep_proportion=True)
            current_y = img_rect.y1 + 15

        # --- 5. THE FLOATING CONCLUSION ---
        if current_y + 60 > FOOTER_CEILING:
            curr_p_idx += 1
            if curr_p_idx >= len(doc): doc.fullcopy_page(1)
            target_page = doc[curr_p_idx]
            target_page.clean_contents()
            target_page.add_redact_annot(fitz.Rect(35, 155, 600, FOOTER_CEILING), fill=(1,1,1))
            target_page.apply_redactions()
            current_y = 165
        else:
            target_page = doc[curr_p_idx]

        final_y = max(current_y, 165)
        conc_rect = fitz.Rect(40.68, final_y, 550, final_y + 80)
        target_page.insert_textbox(conc_rect, f"Conclusion:\n{data['conclusion']}", fontsize=11, fontname="tiro")

        # --- 6. PRODUCTION SAVE ---
        doc.save(output_pdf, clean=True, deflate=True)
        print(f"\n--- BUILD SUCCESSFUL: {output_pdf} ---")

    except Exception as e:
        print(f"\n--- BUILD FAILED ---")
        print(f"Error Detail: {e}")

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    user_data = {
        "exp_no": "1",
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
        "aim": "To identify the case study and detail statement of problem. Design an ER Model.",
        "outcomes": "1. Identify entities. 2. Establish relationships.",
        "conclusion": "i think its working."
    }

    # Pass an image here to see the layout adjust
    user_images = ["my_image.jpg","my_image.jpg" ] 

    finalize_portfolio_report("exp1.pdf", "Final_Submission.pdf", user_data, user_images)