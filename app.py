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
        
        file_rename_prefix = st.text_input("Custom File Rename Prefix:", value="tiktok_report_")
        
        # Ensure this button is correctly indented under Tab 2
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
                with zipfile.ZipFile(zip_output_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                    for index, item_title in enumerate(titles_array, start=1):
                        # Always reload a fresh clone of the template for each iteration
                        gen_doc = fitz.open(stream=st.session_state.template_bytes, filetype="pdf")
                        
                        # Set internal PDF Title metadata (matches browser/tab title)
                        gen_doc.set_metadata({"title": item_title})
                        
                        target_page = gen_doc[0] # Stamp onto page 1 of template
                        page_rect = target_page.rect # Get full dimensions of the PDF page
                        
                        # Search for the exact existing title coordinates on the page
                        text_instances = target_page.search_for(search_query)
                        
                        if text_instances:
                            rect = text_instances[0]
                            
                            # Define a wide, secure layout box spanning across page margins
                            margin = 36
                            box_x0 = margin
                            box_x1 = page_rect.width - margin
                            box_y0 = rect.y0 - 5
                            box_y1 = rect.y1 + 55  # Vertical clearance for multi-line wrapping
                            
                            wide_rect = fitz.Rect(box_x0, box_y0, box_x1, box_y1)
                            
                            # Completely erase the old title area safely with a white block
                            target_page.draw_rect(wide_rect, color=(1, 1, 1), fill=(1, 1, 1))
                            
                            # Format text cleanly using HTML tags for absolute character safety and centering/bolding
                            html_content = f"""
                            <div style="text-align: center; font-size: {font_size}px; font-weight: bold; color: #1a1a33; font-family: Helvetica, sans-serif;">
                                {item_title}
                            </div>
                            """
                            
                            # Insert via htmlbox to ensure special symbols (&, %, [, ], etc.) parse and render 100% correctly
                            target_page.insert_htmlbox(wide_rect, html_content)
                        else:
                            # Fallback default box if text isn't found verbatim
                            fallback_rect = fitz.Rect(36, 150, page_rect.width - 36, 230)
                            html_fallback = f"""
                            <div style="text-align: center; font-size: {font_size}px; font-weight: bold; color: #1a1a33; font-family: Helvetica, sans-serif;">
                                {item_title}
                            </div>
                            """
                            target_page.insert_htmlbox(fallback_rect, html_fallback)
                        
                        compiled_pdf_bytes = gen_doc.write()
                        
                        # Clean naming convention for output files
                        sanitized_name = "".join(c if c.isalnum() else "_" for c in item_title)[:30]
                        final_file_name = f"{file_rename_prefix}{index}_{sanitized_name}.pdf"
                        
                        archive.writestr(final_file_name, compiled_pdf_bytes)
                
                zip_output_buffer.seek(0)
                st.success(f"Successfully generated {len(titles_array)} unique PDF files with matching tab titles!")
                
                st.download_button(
                    label="📦 Download All Bulk PDFs (ZIP)",
                    data=zip_output_buffer,
                    file_name="canva_style_bulk_outputs.zip",
                    mime="application/zip"
                )
