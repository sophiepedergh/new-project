import streamlit as st
import fitz  # PyMuPDF
import os
import io
import zipfile

st.set_page_config(page_title="Advanced PDF Toolkit", layout="wide")

st.title("📄 Advanced PDF Editor & Bulk Generator Tool")
st.markdown("Upload, edit elements, add links/images, or generate bulk PDFs dynamically.")

# Sidebar navigation for features
option = st.sidebar.selectbox(
    "Choose Tool Mode", 
    ["Edit Uploaded PDF", "Bulk PDF Generator from Titles"]
)

# ==========================================
# MODE 1: EDIT UPLOADED PDF
# ==========================================
if option == "Edit Uploaded PDF":
    st.header("✏️ Interactive PDF Editor")
    
    uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        # Load PDF with PyMuPDF
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        page_num = st.number_input("Select Page Number", min_value=1, max_value=len(doc), value=1)
        page = doc[page_num - 1]
        
        st.subheader("Edit Page Elements")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 1. Edit / Replace Text")
            old_text = st.text_input("Find exact text to replace:")
            new_text = st.text_input("Replace with new text:")
            if st.button("Apply Text Replacement"):
                if old_text:
                    text_instances = page.search_for(old_text)
                    for inst in text_instances:
                        # Redact old text area and insert new text
                        page.add_redact_annot(inst, fill=(1, 1, 1))
                        page.apply_redactions()
                        page.insert_text(inst.tl, new_text, fontsize=11, color=(0, 0, 0))
                    st.success(f"Replaced '{old_text}' with '{new_text}'.")
                else:
                    st.error("Please enter text to find.")

            st.markdown("### 3. Anchor Link to Text/Image")
            link_text = st.text_input("Target text on page to turn into a link:")
            target_url = st.text_input("Enter URL (e.g., https://example.com):")
            if st.button("Add Hyperlink"):
                if link_text and target_url:
                    matches = page.search_for(link_text)
                    for rect in matches:
                        link_dict = {"kind": fitz.LINK_URI, "from": rect, "uri": target_url}
                        page.insert_link(link_dict)
                    st.success(f"Linked instances of '{link_text}' to {target_url}.")
                else:
                    st.error("Provide both link text and URL.")

        with col2:
            st.markdown("### 2. Upload & Insert Image")
            img_file = st.file_uploader("Upload Image (PNG/JPG)", type=["png", "jpg", "jpeg"])
            
            # Coordinates for image placement
            img_x = st.number_input("X Coordinate", value=100)
            img_y = st.number_input("Y Coordinate", value=100)
            img_w = st.number_input("Image Width", value=150)
            img_h = st.number_input("Image Height", value=150)
            
            if img_file is not None and st.button("Insert Image"):
                img_bytes = img_file.read()
                rect = fitz.Rect(img_x, img_y, img_x + img_w, img_y + img_h)
                page.insert_image(rect, stream=img_bytes)
                st.success("Image successfully inserted into the PDF!")

        # Save and Download Edited PDF
        st.markdown("---")
        if st.button("Save & Download Modified PDF"):
            output_stream = io.BytesIO()
            doc.save(output_stream)
            output_stream.seek(0)
            
            st.download_button(
                label="📥 Download Edited PDF",
                data=output_stream,
                file_name="edited_output.pdf",
                mime="application/pdf"
            )

# ==========================================
# MODE 2: BULK PDF GENERATOR FROM TITLES
# ==========================================
elif option == "Bulk PDF Generator from Titles":
    st.header("⚡ Bulk PDF Generator")
    st.markdown("Enter titles below (one per line). The tool will generate a custom PDF for each title with optional custom naming.")
    
    # Text box for bulk titles
    titles_input = st.text_area("Input Titles (One title per line):", height=150)
    
    file_prefix = st.text_input("Custom Rename Prefix for Files:", value="document_")
    
    if st.button("Generate Bulk PDFs"):
        if not titles_input.strip():
            st.error("Please enter at least one title.")
        else:
            titles = [t.strip() for t in titles_input.split("\n") if t.strip()]
            
            # Create an in-memory zip file to pack all generated PDFs
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for idx, title in enumerate(titles, start=1):
                    # Create a simple PDF for each title using PyMuPDF
                    new_doc = fitz.open()
                    page = new_doc.new_page()
                    
                    # Add Title text styling onto the generated page
                    page.insert_text((72, 100), title, fontsize=24, color=(0.1, 0.2, 0.4))
                    page.insert_text((72, 140), "Generated automatically via Bulk PDF Tool.", fontsize=11, color=(0.4, 0.4, 0.4))
                    
                    pdf_output = new_doc.write()
                    
                    # Custom safe filename creation
                    safe_title = "".join(c if c.isalnum() else "_" for c in title)[:30]
                    filename = f"{file_prefix}{idx}_{safe_title}.pdf"
                    
                    zip_file.writestr(filename, pdf_output)
            
            zip_buffer.seek(0)
            st.success(f"Successfully generated {len(titles)} PDFs!")
            
            st.download_button(
                label="📦 Download All Generated PDFs (ZIP)",
                data=zip_buffer,
                file_name="bulk_generated_pdfs.zip",
                mime="application/zip"
            )