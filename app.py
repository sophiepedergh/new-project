zip_output_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_output_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                    for item_title in titles_array:
                        # Always reload a fresh clone of the template for each iteration
                        gen_doc = fitz.open(stream=st.session_state.template_bytes, filetype="pdf")
                        
                        # 1. Force internal document metadata to match the exact title
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
                            
                            # Insert via htmlbox to ensure special symbols parse and render 100% correctly
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
                        
                        # 2. Use the exact replaced title for the file name (sanitized for file system safety)
                        sanitized_name = "".join(c if c.isalnum() or c in (' ', '-', '_', '[', ']', '(', ')') else "_" for c in item_title).strip()
                        final_file_name = f"{sanitized_name}.pdf"
                        
                        archive.writestr(final_file_name, compiled_pdf_bytes)
