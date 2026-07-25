# Search for the exact existing title coordinates on the page
                        text_instances = target_page.search_for(search_query)
                        
                        if text_instances:
                            rect = text_instances[0]
                            
                            # Define a wide, secure layout box spanning across page margins with extra vertical padding
                            margin = 36
                            box_x0 = margin
                            box_x1 = page_rect.width - margin
                            box_y0 = rect.y0 - 10  # Expanded top clearance to catch any lingering text
                            box_y1 = rect.y1 + 80  # Expanded bottom clearance for multi-line protection
                            
                            wide_rect = fitz.Rect(box_x0, box_y0, box_x1, box_y1)
                            
                            # Completely erase the old title area safely with a solid opaque white block
                            target_page.draw_rect(wide_rect, color=(1, 1, 1), fill=(1, 1, 1))
                            
                            # Format text cleanly using HTML tags for absolute character safety and centering/bolding
                            html_content = f"""
                            <div style="text-align: center; font-size: {font_size}px; font-weight: bold; color: #1a1a33; font-family: Helvetica, sans-serif; background-color: #ffffff;">
                                {item_title}
                            </div>
                            """
                            
                            # Insert via htmlbox to ensure special symbols parse and render 100% correctly
                            target_page.insert_htmlbox(wide_rect, html_content)
                        else:
                            # Fallback default box if text isn't found verbatim
                            fallback_rect = fitz.Rect(36, 150, page_rect.width - 36, 250)
                            
                            # Erase fallback area just in case
                            target_page.draw_rect(fallback_rect, color=(1, 1, 1), fill=(1, 1, 1))
                            
                            html_fallback = f"""
                            <div style="text-align: center; font-size: {font_size}px; font-weight: bold; color: #1a1a33; font-family: Helvetica, sans-serif; background-color: #ffffff;">
                                {item_title}
                            </div>
                            """
                            target_page.insert_htmlbox(fallback_rect, html_fallback)
