import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile

st.set_page_config(page_title="Ultimate PDF Generator & Editor Tool", layout="wide")

st.title("🛠️ Ultimate PDF Generator & Editor Suite")
st.markdown("Easily edit an uploaded PDF template or batch-generate bulk PDFs from a list of titles.")

# Navigation Tabs
tab1, tab2 = st.tabs(["📝 Upload & Edit PDF", "⚡ Bulk PDF Generator"])

# =====================================================================
# TAB 1: UPLOAD & EDIT PDF (Text changes, Image insertion, Hyperlinks)
# =====================================================================
with tab1:
    st.header("Interactive PDF Editor Suite")
    st.markdown("Upload a sample PDF, navigate pages, modify content, add images, and embed links.")

    uploaded_pdf = st.file_uploader("Upload your sample PDF file", type=["pdf"], key="editor_upload")

    if uploaded_pdf is not None:
        pdf_bytes = uploaded_pdf.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        total_pages = len(doc)
        st.info(f"Loaded successfully! Total Pages in PDF: {total_pages}")
        
        # Select page to view/edit
        page_idx = st.number_input("Select Page Number to Edit", min_value=1, max_value=total_pages, value=1) - 1
        page = doc[page_idx]

        # Layout columns for tools
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("1. Text Editor & Search-Replace")
            old_search_text = st.text_input("Exact text to locate:")
            new_replace_text = st.text_input("New replacement text:")
            
            if st.button("Apply Text Replacement"):
                if old_search_text:
                    instances = page.search_for(old_search_text)
                    if instances:
                        for inst in instances:
                            # Erase old text block and write replacement text
                            page.add_redact_annot(inst, fill=(1, 1, 1))
                            page.apply_redactions()
                            page.insert_text(inst.tl, new_replace_text, fontsize=11, color=(0, 0, 0))
                        st.success(f"Successfully replaced '{old_search_text}' with '{new_replace_text}'!")
                    else:
                        st.warning("Could not find the specified text on this page.")
                else:
                    st.error("Please provide text to search.")

            st.markdown("---")
            st.subheader("3. Anchor Hyperlinks")
            link_anchor_text = st.text_input("Target text/word on page to anchor link:")
            target_url = st.text_input("Destination URL (e.g., https://yourwebsite.com):")
            
            if st.button("Insert Hyperlink to Text"):
                if link_anchor_text and target_url:
                    matches = page.search_for(link_anchor_text)
                    if matches:
                        for rect in matches:
                            link_dict = {"kind": fitz.LINK_URI, "from": rect, "uri": target_url}
                            page.insert_link(link_dict)
                        st.success(f"Linked all occurrences of '{link_anchor_text}' to {target_url}!")
                    else:
                        st.warning("Target text not found on this page.")
                else:
                    st.error("Please fill out both the anchor text and URL.")

        with col_right:
            st.subheader("2. Upload & Insert Image")
            uploaded_image = st.file_uploader("Upload Image File (PNG / JPG)", type=["png", "jpg", "jpeg"])
            
            # Coordinate controls for positioning image precisely
            img_x = st.number_input("X Coordinate (Left position)", value=100)
            img_y = st.number_input("Y Coordinate (Top position)", value=100)
            img_w = st.number_input("Image Width", value=150)
            img_h = st.number_input("Image Height", value=150)
            
            if uploaded_image is not None and st.button("Insert Image into PDF"):
                img_data = uploaded_image.read()
                image_rect = fitz.Rect(img_x, img_y, img_x + img_w, img_y + img_h)
                page.insert_image(image_rect, stream=img_data)
                st.success("Image successfully injected into the PDF editor canvas!")

        st.markdown("---")
        st.subheader("Download Edited PDF")
        if st.button("Save & Prepare Download"):
            output_buffer = io.BytesIO()
            doc.save(output_buffer)
            output_buffer.seek(0)
            
            st.download_button(
                label="📥 Download Your Edited PDF",
                data=output_buffer,
                file_name="modified_document.pdf",
                mime="application/pdf"
            )

# =====================================================================
# TAB 2: BULK PDF GENERATOR FROM TITLES BOX
# =====================================================================
with tab2:
    st.header("⚡ Bulk PDF Generator Engine")
    st.markdown("Input a massive collection of titles below (one title per row). The system will automatically compile a distinct PDF file for every single line.")

    # Main text input box for bulk titles
    bulk_titles_box = st.text_area(
        "Enter Titles (Type or paste multiple lines, one title per file):",
        height=200,
        placeholder="Example Title 1\nExample Title 2\nExample Title 3"
    )

    # File renaming custom prefix configuration
    rename_prefix = st.text_input("Custom File Rename Prefix:", value="generated_file_")

    if st.button("Generate Bulk PDFs Now"):
        if not bulk_titles_box.strip():
            st.error("The titles box is empty! Please insert at least one title.")
        else:
            # Parse titles line by line
            titles_list = [t.strip() for t in bulk_titles_box.split("\n") if t.strip()]
            
            # Pack generated PDFs into a compressed ZIP archive in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_archive:
                for idx, title in enumerate(titles_list, start=1):
                    # Build a fresh single-page document for each title
                    batch_doc = fitz.open()
                    batch_page = batch_doc.new_page()
                    
                    # Layout text structure inside generated page
                    batch_page.insert_text((72, 100), title, fontsize=22, color=(0.1, 0.1, 0.3))
                    batch_page.insert_text((72, 140), "Auto-compiled via Bulk Generator Tool.", fontsize=10, color=(0.5, 0.5, 0.5))
                    
                    pdf_data = batch_doc.write()
                    
                    # Format clean file names
                    clean_title_string = "".join(c if c.isalnum() else "_" for c in title)[:35]
                    file_name = f"{rename_prefix}{idx}_{clean_title_string}.pdf"
                    
                    zip_archive.writestr(file_name, pdf_data)
            
            zip_buffer.seek(0)
            st.success(f"Successfully compiled {len(titles_list)} individual PDF files!")
            
            # Download button for bulk output archive
            st.download_button(
                label="📦 Download All Generated PDFs (ZIP Package)",
                data=zip_buffer,
                file_name="bulk_generated_pdfs.zip",
                mime="application/zip"
            )
