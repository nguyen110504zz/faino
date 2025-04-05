from weasyprint import HTML, CSS
import os
from typing import Optional
import logging
from urllib.parse import urljoin
from pathlib import Path

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_html_to_pdf(html_content: str, output_path: str, css_path: Optional[str] = None):
    """
    Convert HTML content to PDF using WeasyPrint with custom CSS
    """
    try:
        # Get the base directory for resolving relative paths
        base_dir = os.path.dirname(os.path.dirname(__file__))
        static_dir = os.path.join(base_dir, 'App', 'static')
        
        # Default CSS path if none provided
        if css_path is None:
            css_path = os.path.join(os.path.dirname(__file__), 'templates', 'pdf_styles.css')
        
        # Create CSS object
        css = None
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                css = CSS(string=f.read())
            logger.info(f"Loaded CSS from {css_path}")
        else:
            logger.warning(f"CSS file not found at {css_path}")

        # Fix image paths in HTML content
        html_content = html_content.replace('../static/', f'file:///{static_dir.replace(os.sep, "/")}/')
        
        # Create PDF from HTML with base URL for resolving relative paths
        HTML(
            string=html_content,
            base_url=f'file:///{base_dir.replace(os.sep, "/")}/'
        ).write_pdf(
            output_path,
            stylesheets=[css] if css else None
        )
        logger.info(f"PDF generated successfully at {output_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return False

def generate_pdf_report(html_content: str, output_path: str, css_path: Optional[str] = None):
    """
    Generate PDF report from HTML content with custom styling
    """
    try:
        # Convert to PDF
        success = convert_html_to_pdf(html_content, output_path, css_path)
        
        if success:
            logger.info(f"PDF report generated successfully at: {output_path}")
            return True
        else:
            logger.error("Failed to generate PDF report")
            return False
            
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        return False 