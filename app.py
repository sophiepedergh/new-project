import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile

st.set_page_config(page_title="Custom Bulk PDF Creator (Canva Style)", layout="wide")

st.title("🎨 Canva-Style PDF Template & Bulk Generator")
st.markdown("Upload a template PDF, specify the existing title to target, paste your bulk titles in double quotes, and generate your files instantly.")

# Initialize Tabs properly at the top level
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

    # Initialize target_text_to_replace safely at root/tab1 scope
    target_text_to_replace = "Boost Your Instagram Profile: Get Free Ig Likes in 2026 [CxD+9JH]"
    font_size = 15

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
            font_size = st.slider("Replacement Font Size (Optional adjustment)", min_value=10, max_value=48, value=15)
        
        with col_set2:
            st.info(
                "**How it works:** \n"
                "1. The tool locates your target title position vertically.\n"
                "2. It uses an HTML-enabled rendering box that fully supports special characters like %, &, [, ], etc.\n"
                "3. It replaces your text cleanly **once**, bolding and center-aligning your literal titles."
            )

with tab2:
    st.header("⚡ Bulk Title Processing Engine")
    
    if st.session_state.template_bytes is None:
        st.warning("⚠️ Please upload a template PDF in **Tab 1** first before generating bulk files.")
    else:
        st.markdown("Enter your bulk titles below. Wrap each title in **double quotes** (one per line):")
        
        bulk_input_box = st.text_area(
            "Paste Bulk Titles Here (with double quotes):",
            height=220,
            placeholder="\"Instantly Views In A Click - Free TikTok Followers & Likes 2026 (Boost Guide) [QJ5))]\"\n\"100%-SAFE! Free TikTok Followers in 5 Minutes! Boost 1000 Likes & Views [8DJTG]\""
        )
        
        if st.button("🚀 Generate Bulk PDFs"):
            if not bulk_input_box.strip():
                st.error("Please provide at least one title in the box.")
            else:
                raw_lines = [t.strip() for t in bulk_input_box.split("\n") if t.strip()]
                titles_array = []
                
                # Extract text precisely from inside double quotes if present
                for line in raw_lines:
                    if line.startswith('"') and line.endswith('"') and len(line) >= 2:
                        titles_array.append(line[1:-1])
                    else:
                        titles_array.append(line)
                
                search_query = target_text_to_replace if 'target_text_to_replace' in locals() and target_text_to_replace else "Boost Your Instagram Profile: Get Free Ig Likes in 2026 [CxD+9JH]"
                
                zip_output_buffer = io.BytesIO()
                success_count = 0
                
                with zipfile.ZipFile(zip_output_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                    for item_title in titles_array:
                        try:
                            # Always reload a fresh clone of the template for each iteration
                            gen_doc = fitz.open(stream=st.session_state.template_bytes, filetype="pdf")
                            
                            # Set internal PDF metadata to match the exact replaced title
                            gen_doc.set_metadata({
                                "title": item_title,
                                "subject": item_title,
                                "keywords": item_title
                            })
                            
                            target_page = gen_doc[0] # Stamp onto page 1 of template
                            page_rect = target_page.rect # Get full dimensions of the PDF page
                            
                            # Search for the exact existing title coordinates on the page
                            text_instances = target_page.search_for(search_query)
                            
                            if text_instances:
                                rect = text_instances[0]
                                
                                # Define a wide layout box with clear padding
                                margin = 36
                                box_x0 = margin
                                box_x1 = page_rect.width - margin
                                box_y0 = rect.y0 - 15
                                box_y1 = rect.y1 + 90
                                
                                wide_rect = fitz.Rect(box_x0, box_y0, box_x1, box_y1)
                                
                                # Completely erase old text area with an opaque white block
                                target_page.draw_rect(wide_rect, color=(1, 1, 1), fill=(1, 1, 1))
                                
                                # Format text cleanly using HTML tags
                                html_content = f"""
                                <div style="text-align: center; font-size: {font_size}px; font-weight: bold; color: #1a1a33; font-family: Helvetica, sans-serif; background-color: #ffffff;">
                                    {item_title}
                                </div>
                                """
                                target_page.insert_htmlbox(wide_rect, html_content)
                            else:
                                # Fallback default box if text isn't found verbatim
                                fallback_rect = fitz.Rect(36, 150, page_rect.width - 36, 250)
                                target_page.draw_rect(fallback_rect, color=(1, 1, 1), fill=(1, 1, 1))
                                
                                html_fallback = f"""
                                <div style="text-align: center; font-size: {font_size}px; font-weight: bold; color: #1a1a33; font-family: Helvetica, sans-serif; background-color: #ffffff;">
                                    {item_title}
                                </div>
                                """
                                target_page.insert_htmlbox(fallback_rect, html_fallback)
                            
                            compiled_pdf_bytes = gen_doc.write()
                            
                            # Format file name cleanly using the exact title text
                            sanitized_name = "".join(c if c.isalnum() or c in (' ', '-', '_', '[', ']', '(', ')') else "_" for c in item_title).strip()
                            final_file_name = f"{sanitized_name}.pdf"
                            
                            archive.writestr(final_file_name, compiled_pdf_bytes)
                            success_count += 1
                        except Exception as e:
                            # Catch any loop-level exceptions so one bad title doesn't break the whole batch
                            continue
                
                zip_output_buffer.seek(0)
                
                if success_count > 0:
                    st.success(f"Successfully generated and packaged {success_count} of {len(titles_array)} PDF files into the ZIP archive!")
                    st.download_button(
                        label="📦 Download All Bulk PDFs (ZIP)",
                        data=zip_output_buffer,
                        file_name="canva_style_bulk_outputs.zip",
                        mime="application/zip"
                    )
                else:
                    st.error("Generation failed. Please verify that your template PDF is uploaded correctly and your target text string matches what's written on the document.")
