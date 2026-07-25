import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile

st.set_page_config(page_title="Custom Bulk PDF Creator (Canva Style)", layout="wide")

st.title("🎨 Canva-Style PDF Template & Bulk Generator")
st.markdown("Upload a template PDF, specify the existing title to target, paste your bulk titles, and generate your files instantly.")

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
        
        st.subheader("Target Text Replacement Setup")
        st.markdown("Enter the **exact text string** currently written inside your uploaded PDF template that you want the tool to find and swap out:")
        
        col_set1, col_set2 = st.columns(2)
        with col_set1:
            target_text_to_replace = st.text_input(
                "Existing Title to Find & Replace in PDF", 
                value="Boost Your Instagram Profile: Get Free Ig Likes in 2026 [CxD+9JH]", 
                help="Paste the exact title text currently sitting on your PDF design template."
            )
            font_size = st.slider("Replacement Font Size (Optional adjustment)", min_value=10, max_value=72, value=18)
        
        with col_set2:
            st.info(
                "**How it works:** \n"
                "1. The tool searches your uploaded PDF for the exact text specified on the left.\n"
                "2. It locates its precise coordinates on the page.\n"
                "3. It covers up the old title and swaps it out with each new item from **Tab 2** one by one."
            )

with tab2:
    st.header("⚡ Bulk Title Processing Engine")
    
    if st.session_state.template_bytes is None:
        st.warning("⚠️ Please upload a template PDF in **Tab 1** first before generating bulk files.")
    else:
        st.markdown("Enter your bulk titles below. Put **one title per line**:")
        
        bulk_input_box = st.text_area(
            "Paste Bulk Titles Here:",
            height=220,
            placeholder="Free Tiktok Followers Generator 2026: Boost Your Presence Instantly [ptiz]\nFree Tiktok Followers Generator 2026: Boost Your Presence Instantly [E7WW4w]"
        )
        
        file_rename_prefix = st.text_input("Custom File Rename Prefix:", value="tiktok_report_")
        
        if st.button("🚀 Generate Bulk PDFs"):
            if not bulk_input_box.strip():
                st.error("Please provide at least one title in the box.")
            else:
                titles_array = [t.strip() for t in bulk_input_box.split("\n") if t.strip()]
                search_query = target_text_to_replace if 'target_text_to_replace' in locals() and target_text_to_replace else "Boost Your Instagram Profile: Get Free Ig Likes in 2026 [CxD+9JH]"
                
                zip_output_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_output_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                    for index, item_title in enumerate(titles_array, start=1):
                        # Always reload a fresh clone of the template for each iteration
                        gen_doc = fitz.open(stream=st.session_state.template_bytes, filetype="pdf")
                        target_page = gen_doc[0] # Stamp onto page 1 of template
                        
                        # Search for the exact existing title coordinates on the page
                        text_instances = target_page.search_for(search_query)
                        
                        if text_instances:
                            # Loop through instances found (usually 1) and replace them
                            for rect in text_instances:
                                # Draw a white rectangle over the old title to hide/erase it completely
                                target_page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                                
                                # Insert the new bulk title directly into that exact coordinate space
                                target_page.insert_text(
                                    (rect.x0, rect.y1), 
                                    item_title, 
                                    fontsize=font_size, 
                                    color=(0.1, 0.1, 0.2)
                                )
                        else:
                            # Fallback if the target text string wasn't found verbatim in the PDF
                            target_page.insert_text(
                                (72, 150.0), 
                                item_title, 
                                fontsize=font_size, 
                                color=(0.1, 0.1, 0.2)
                            )
                        
                        compiled_pdf_bytes = gen_doc.write()
                        
                        # Clean naming convention for output files
                        sanitized_name = "".join(c if c.isalnum() else "_" for c in item_title)[:30]
                        final_file_name = f"{file_rename_prefix}{index}_{sanitized_name}.pdf"
                        
                        archive.writestr(final_file_name, compiled_pdf_bytes)
                
                zip_output_buffer.seek(0)
                st.success(f"Successfully generated {len(titles_array)} unique PDF files by replacing the target title!")
                
                st.download_button(
                    label="📦 Download All Bulk PDFs (ZIP)",
                    data=zip_output_buffer,
                    file_name="canva_style_bulk_outputs.zip",
                    mime="application/zip"
                )
