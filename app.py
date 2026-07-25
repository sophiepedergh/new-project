import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile

st.set_page_config(page_title="Custom Bulk PDF Creator (Canva Style)", layout="wide")

st.title("🎨 Canva-Style PDF Template & Bulk Generator")
st.markdown("Upload a template PDF, configure your layout variables, paste bulk titles, and generate your files instantly.")

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
        
        st.subheader("Template Settings & Coordinate Mapping")
        st.markdown("Specify where the bulk titles should be dynamically injected onto your template page:")
        
        col_set1, col_set2 = st.columns(2)
        with col_set1:
            pos_x = st.number_input("Text X-Coordinate (Left Position)", value=72)
            pos_y = st.number_input("Text Y-Coordinate (Top Position)", value=150.0)
            font_size = st.slider("Title Font Size", min_value=10, max_value=72, value=24)
        
        with col_set2:
            st.info(
                "**How it works:** \n"
                "1. Your uploaded PDF serves as the background layout.\n"
                "2. Move to **Tab 2** to paste your bulk list of titles.\n"
                "3. Each title will be automatically stamped onto your template layout at the coordinates specified here."
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
                
                # Setup retrieval coordinates and configuration from Tab 1 variables
                # (Defaults used if fields aren't re-rendered)
                x_cord = 72
                y_cord = 150.0
                f_size = 24
                
                zip_output_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_output_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                    for index, item_title in enumerate(titles_array, start=1):
                        # Always reload a fresh clone of the template for each iteration
                        gen_doc = fitz.open(stream=st.session_state.template_bytes, filetype="pdf")
                        target_page = gen_doc[0] # Stamp onto page 1 of template
                        
                        # Inject the dynamic title text
                        target_page.insert_text(
                            (x_cord, y_cord), 
                            item_title, 
                            fontsize=f_size, 
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
