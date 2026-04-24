"""Mermaid diagram rendering service using Playwright."""
import asyncio
import base64
from pathlib import Path
from typing import Optional
import hashlib
from datetime import datetime
from playwright.async_api import async_playwright
from ..config import settings
from ..models.schemas import RenderFormat, Theme, RenderResponse
from ..utils.logging import logger


class RenderService:
    """Service for rendering Mermaid diagrams to images."""
    
    def __init__(self):
        """Initialize rendering service."""
        self.output_dir = settings.diagrams_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def render(
        self,
        mermaid_code: str,
        format: RenderFormat = RenderFormat.PNG,
        theme: Theme = Theme.DEFAULT,
        background: str = "white",
        width: int = 1920,
        height: int = 1080,
        return_base64: bool = False
    ) -> RenderResponse:
        """
        Render Mermaid diagram to image.
        
        Args:
            mermaid_code: Mermaid diagram code
            format: Output format (png, svg, pdf)
            theme: Mermaid theme
            background: Background color
            width: Output width
            height: Output height
            return_base64: Return base64 encoded image
            
        Returns:
            RenderResponse with file path or base64 image
        """
        logger.info(f"Rendering diagram to {format.value}")
        
        try:
            # Generate unique filename
            code_hash = hashlib.md5(mermaid_code.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagram_{timestamp}_{code_hash}.{format.value}"
            output_path = self.output_dir / filename
            
            # Render using Playwright
            await self._render_with_playwright(
                mermaid_code=mermaid_code,
                output_path=output_path,
                format=format,
                theme=theme,
                background=background,
                width=width,
                height=height
            )
            
            # Return base64 if requested
            if return_base64:
                with open(output_path, 'rb') as f:
                    image_data = f.read()
                    b64_image = base64.b64encode(image_data).decode('utf-8')
                
                logger.info("Successfully rendered diagram (base64)")
                return RenderResponse(
                    success=True,
                    base64_image=b64_image,
                    format=format.value
                )
            
            logger.info(f"Successfully rendered diagram: {output_path}")
            return RenderResponse(
                success=True,
                file_path=str(output_path),
                format=format.value,
                download_url=f"/download/{filename}"
            )
            
        except Exception as e:
            logger.error(f"Failed to render diagram: {e}")
            return RenderResponse(
                success=False,
                format=format.value,
                error=str(e)
            )
    
    async def _render_with_playwright(
        self,
        mermaid_code: str,
        output_path: Path,
        format: RenderFormat,
        theme: Theme,
        background: str,
        width: int,
        height: int
    ):
        """Render diagram using Playwright browser automation."""
        
        # Create HTML with Mermaid
        html_content = self._create_html(mermaid_code, theme, background)
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                viewport={'width': width, 'height': height}
            )
            
            try:
                # Load HTML content
                await page.set_content(html_content)
                
                # Wait for Mermaid to render
                await page.wait_for_selector('#mermaid-diagram svg', timeout=30000)
                
                # Add small delay to ensure complete rendering
                await asyncio.sleep(0.5)
                
                # Get the SVG element
                svg_element = await page.query_selector('#mermaid-diagram svg')
                
                if not svg_element:
                    raise Exception("Failed to render Mermaid diagram")
                
                # Render based on format
                if format == RenderFormat.SVG:
                    # Get SVG content
                    svg_content = await page.evaluate('''
                        () => {
                            const svg = document.querySelector('#mermaid-diagram svg');
                            return svg.outerHTML;
                        }
                    ''')
                    
                    with open(output_path, 'w') as f:
                        f.write(svg_content)
                
                elif format == RenderFormat.PNG:
                    # Screenshot the SVG element
                    await svg_element.screenshot(path=str(output_path))
                
                elif format == RenderFormat.PDF:
                    # Print to PDF
                    await page.pdf(path=str(output_path), format='A4')
                
            finally:
                await browser.close()
    
    def _create_html(
        self,
        mermaid_code: str,
        theme: Theme,
        background: str
    ) -> str:
        """Create HTML wrapper for Mermaid rendering."""
        
        # Escape mermaid code for JavaScript
        escaped_code = mermaid_code.replace('`', '\\`').replace('$', '\\$')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background-color: {background};
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        #mermaid-diagram {{
            display: inline-block;
        }}
    </style>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: '{theme.value}',
            flowchart: {{
                useMaxWidth: false,
                htmlLabels: true
            }},
            sequence: {{
                useMaxWidth: false
            }}
        }});
        
        window.addEventListener('load', () => {{
            mermaid.run();
        }});
    </script>
</head>
<body>
    <div id="mermaid-diagram" class="mermaid">
{escaped_code}
    </div>
</body>
</html>
"""
        return html
    
    async def cleanup_old_files(self, max_age_days: int = 7):
        """
        Clean up old rendered diagrams.
        
        Args:
            max_age_days: Maximum age of files to keep
        """
        logger.info(f"Cleaning up diagrams older than {max_age_days} days")
        
        cutoff_time = datetime.now().timestamp() - (max_age_days * 86400)
        cleaned_count = 0
        
        for file_path in self.output_dir.glob('diagram_*'):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} old diagram files")