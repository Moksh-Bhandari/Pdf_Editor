import fitz  # PyMuPDF


def finalize_portfolio_report(input_pdf, output_pdf, data, image_paths):
    """
    APSIT Report Builder
    Dynamic Aim + Outcomes + Output shifting
    Inline labels formatting
    """
    try:
        doc = fitz.open(input_pdf)

        HEADER_FLOOR = 155
        FOOTER_CEILING = 750

        # =====================================================
        # change1.3 -> Reliable wrapping helper
        # =====================================================
        def wrap_text(text, max_chars):
            words = str(text).split()
            lines = []
            current = ""

            for word in words:
                trial = word if current == "" else current + " " + word

                if len(trial) <= max_chars:
                    current = trial
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

            return lines

        # =====================================================
        # STATIC TEXT CONFIG
        # =====================================================
        TEXT_CONFIG = {
            "Year": {
                "r": [40.68, 158.29, 210, 171.57],
                "v": f"Academic Year: {data['year']}",
                "f": "tibo",
                "s": 12,
            },
            "Sem": {
                "r": [40.68, 172.09, 150, 185.37],
                "v": f"Semester: {data['sem']}",
                "f": "tibo",
                "s": 12,
            },
            "Class": {
                "r": [40.68, 185.89, 315, 199.17],
                "v": f"Class / Div / Branch: {data['class']}",
                "f": "tibo",
                "s": 12,
            },
            "Subj": {
                "r": [40.68, 199.69, 315, 212.97],
                "v": f"Subject: {data['subject']}",
                "f": "tibo",
                "s": 12,
            },
            "Inst": {
                "r": [40.68, 213.49, 325, 226.77],
                "v": f"Name of Instructor: {data['instructor']}",
                "f": "tibo",
                "s": 12,
            },
            "P_Date": {
                "r": [328.63, 199.69, 565, 212.97],
                "v": f"Date of Performance: {data['p_date']}",
                "f": "tibo",
                "s": 12,
            },
            "S_Date": {
                "r": [328.63, 213.49, 565, 226.77],
                "v": f"Date of Submission: {data['s_date']}",
                "f": "tibo",
                "s": 12,
            },
            "Roll": {
                "r": [328.75, 185.89, 460, 199.17],
                "v": f"Roll No: {data['roll']}",
                "f": "tibo",
                "s": 12,
            },
            "L_Name": {
                "r": [328.75, 158.29, 430, 171.57],
                "v": "Name of Student:",
                "f": "tibo",
                "s": 12,
            },
            "Val_Name": {
                "r": [420, 158.29, 595, 171.57],
                "v": data["name"],
                "f": "tibo",
                "s": 12,
            },
            "L_ID": {
                "r": [328.75, 172.94, 405, 185.16],
                "v": "Student ID:",
                "f": "tibo",
                "s": 12,
            },
            "Val_ID": {
                "r": [390, 172.94, 530, 185.16],
                "v": data["id"],
                "f": "tibo",
                "s": 12,
            },
            "Exp_No": {
                "r": [217, 232, 455, 248],
                "v": f"Experiment No. {data['exp_no']}",
                "f": "tibo",
                "s": 13,
            },
        }

        # =====================================================
        # REDACTION ENGINE
        # =====================================================
        for i in range(len(doc)):
            page = doc[i]
            page.clean_contents()

            if i == 0:
                page.add_redact_annot(
                    fitz.Rect(35, 155, 600, 230),
                    fill=(1, 1, 1),
                )

                page.add_redact_annot(
                    fitz.Rect(35, 230, 600, 420),
                    fill=(1, 1, 1),
                )

                page.add_redact_annot(
                    fitz.Rect(35, 430, 600, FOOTER_CEILING),
                    fill=(1, 1, 1),
                )
            else:
                page.add_redact_annot(
                    fitz.Rect(35, 155, 600, FOOTER_CEILING),
                    fill=(1, 1, 1),
                )

            page.apply_redactions()

        # =====================================================
        # PAGE 1 REBUILD
        # =====================================================
        page1 = doc[0]

        page1.draw_line(
            fitz.Point(35, 228),
            fitz.Point(565, 228),
            color=(0, 0, 0),
            width=1.5,
        )

        for _, f in TEXT_CONFIG.items():
            rect = fitz.Rect(f["r"])

            page1.insert_text(
                (rect.x0, rect.y1 - 1),
                f["v"],
                fontsize=f["s"],
                fontname=f["f"],
            )

        # =====================================================
        # change1.3 -> Inline Aim / Outcomes / Output
        # =====================================================
        current_y = 272

        # AIM
        page1.insert_text(
            (40.68, current_y),
            "Aim:",
            fontsize=12,
            fontname="tibo",
        )

        aim_lines = wrap_text(data["aim"], 78)

        first_line = True
        for line in aim_lines:
            x_pos = 78
            page1.insert_text(
                (x_pos, current_y),
                line,
                fontsize=11,
                fontname="tiro",
            )
            current_y += 15
            first_line = False

        current_y += 8

        # LAB OUTCOMES
        page1.insert_text(
            (40.68, current_y),
            "Lab Outcomes:",
            fontsize=12,
            fontname="tibo",
        )

        out_lines = wrap_text(data["outcomes"], 66)

        for line in out_lines:
            page1.insert_text(
                (130, current_y),
                line,
                fontsize=11,
                fontname="tiro",
            )
            current_y += 15

        current_y += 10

        # OUTPUT
        page1.insert_text(
            (40.68, current_y),
            "Output:",
            fontsize=12,
            fontname="tibo",
        )

        current_y += 25

        # =====================================================
        # IMAGE ENGINE
        # =====================================================
        curr_p_idx = 0

        for img_path in image_paths:
            if current_y + 280 > FOOTER_CEILING:
                curr_p_idx += 1

                if curr_p_idx >= len(doc):
                    doc.fullcopy_page(1)

                target = doc[curr_p_idx]
                target.clean_contents()

                target.add_redact_annot(
                    fitz.Rect(35, 155, 600, FOOTER_CEILING),
                    fill=(1, 1, 1),
                )

                target.apply_redactions()

                current_y = 165

            img_rect = fitz.Rect(
                50,
                current_y,
                540,
                current_y + 280,
            )

            doc[curr_p_idx].insert_image(
                img_rect,
                filename=img_path,
                keep_proportion=True,
            )

            current_y = img_rect.y1 + 15

        # =====================================================
        # CONCLUSION
        # =====================================================
        if current_y + 60 > FOOTER_CEILING:
            curr_p_idx += 1

            if curr_p_idx >= len(doc):
                doc.fullcopy_page(1)

            target_page = doc[curr_p_idx]
            target_page.clean_contents()

            target_page.add_redact_annot(
                fitz.Rect(35, 155, 600, FOOTER_CEILING),
                fill=(1, 1, 1),
            )

            target_page.apply_redactions()

            current_y = 165

        else:
            target_page = doc[curr_p_idx]

        final_y = max(current_y, 165)

        # Bold label
        target_page.insert_text(
            (40.68, final_y + 12),
            "Conclusion:",
            fontsize=11,
            fontname="tibo"
        )

        # Normal text
        conc_rect = fitz.Rect(
            110,
            final_y,
            550,
            final_y + 80
        )

        target_page.insert_textbox(
            conc_rect,
            data["conclusion"],
            fontsize=11,
            fontname="tiro"
        )
        
        # ==================================================
        # change 1.4
        # Remove blank pages after conclusion page
        # ==================================================
        while len(doc) - 1 > curr_p_idx:
            doc.delete_page(len(doc) - 1)

        # ======================================================
        # change 4.3
        # ADVANCED PDF COMPRESSION
        # ======================================================
        doc.save(
        output_pdf,
        garbage=4,
        clean=True,
        deflate=True,
        deflate_images=True,
        deflate_fonts=True
    )
        

        # change 4.2
        # CLOSE PDF DOCUMENT PROPERLY
        # ======================================================
        doc.close()

        print(f"\n--- BUILD SUCCESSFUL: {output_pdf} ---")

    except Exception as e:
        print("\n--- BUILD FAILED ---")
        print(f"Error Detail: {e}")