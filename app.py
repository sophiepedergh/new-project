import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile

st.set_page_config(page_title="Custom Bulk PDF Creator (Canva Style)", layout="wide")

st.title("🎨 Canva-Style PDF Template & Bulk Generator")
st.markdown("Upload a template PDF, configure your replacement tag, paste bulk titles, and generate your files instantly.")

tab1, tab2 = st.tabs(["1. Template Editor & Setup", "2. Bulk Title Generator Box"])

# Store template in session state so both tabs can access it
if "template_bytes" not in st.session_state:
    st.session_state.template_bytes = None

with tab1:
    st.header("Upload & Configure Base PDF Template")
    uploaded_file = st.file_uploader("Upload a sample PDF to use as your design template", type=["pdf"])
    
    if uploaded_file is not None:
        st.session_state.template_bytes = uploaded_file.read()
        st.success("Template uploaded successfully!")

    if st.session_state.template_bytes:
        doc = fitz.open(stream=st.session_state.template_bytes, filetype="pdf")
        page = doc[0] # Preview first page
        
        st.subheader("Template Settings & Placeholder Mapping")
        st.markdown("Specify the placeholder text in your template that should be replaced with your bulk titles:")
        
        col_set1, col_set2 = st.columns(2)
        with col_set1:
            placeholder_text = st.text_input(
                "Placeholder Variable to Find", 
                value="{{TITLE}}", 
                help="Enter the exact text string currently on your PDF template that you want to replace dynamically."
            )
            font_size = st.slider("Title Font Size (if new insertion)", min_value=10, max_value=72, value=24)
        
        with col_set2:
            st.info(
                "**How it works:** \n"
                "1. Your uploaded PDF serves as the background layout.\n"
                "2. The app searches for your **Placeholder Variable** on page 1.\n"
                "3. It removes the placeholder and injects each bulk title from **Tab 2** at that exact location."
            )

with tab2:
    st.header("⚡ Bulk Title Processing Engine")
    
    if st.session_state.template_bytes is None:
        st.warning("⚠️ Please upload a template PDF in **Tab 1** first before generating bulk files.")
    else:
        st.markdown("Enter your bulk titles below. Put **one title per line**, exactly like a data spreadsheet column.")
        
        bulk_input_box = st.text_area(
            "Paste Bulk Titles Here:",
            height=220,
            placeholder="Chapter 1: Introduction\nChapter 2: Advanced Guide\nChapter 3: Conclusion"
        )
        
        file_rename_prefix = st.text_input("Custom File Rename Prefix:", value="custom_report_")
        
        if st.button("🚀 Generate Bulk PDFs"):
            if not bulk_input_box.strip():
                st.error("Please provide at least one title in the box.")
            else:
                titles_array = [t.strip() for t in bulk_input_box.split("\n") if t.strip()]
                target_tag = placeholder_text if 'placeholder_text' in locals() and placeholder_text else "{{TITLE}}"
                
                zip_output_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_output_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                    for index, item_title in enumerate(titles_array, start=1):
                        # Always reload a fresh clone of the template for each iteration
                        gen_doc = fitz.open(stream=st.session_state.template_bytes, filetype="pdf")
                        target_page = gen_doc[0] # Stamp onto page 1 of template
                        
                        # Search for the placeholder text coordinates on the page
                        text_instances = target_page.search_for(target_tag)
                        
                        if text_instances:
                            # Use the first occurrence found
                            rect = text_instances[0]
                            
                            # Optional: Redact/Cover up the original placeholder tag area with white
                            target_page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                            
                            # Insert the dynamic title text at the top-left of the found rectangle
                            target_page.insert_text(
                                (rect.x0, rect.y1), 
                                item_title, 
                                fontsize=font_size, 
                                color=(0.1, 0.1, 0.2)
                            )
                        else:
                            # Fallback default coordinates if placeholder text isn't found on the page
                            target_page.insert_text(
                                (72, 150.0), 
                                item_title, 
                                fontsize=font_size, 
                                color=(0.1, 0.1, 0.2)
                            )
                        
                        compiled_pdf_bytes = gen_doc.write()
                        
                        # Clean naming convention
                        sanitized_name = "".join(c if c.isalnum() else "_" for c in item_title)[:30]
                        final_file_name = f"{file_rename_prefix}{index}_{sanitized_name}.pdf"
                        
                        archive.writestr(final_file_name, compiled_pdf_bytes)
                
                zip_output_buffer.seek(0)
                st.success(f"Successfully generated {len(titles_array)} unique PDF files based on your template!")
                
                st.download_button(
                    label="📦 Download All Bulk PDFs (ZIP)",
                    data=zip_output_buffer,
                    file_name="canva_style_bulk_outputs.zip",
                    mime="application/zip"
                )
