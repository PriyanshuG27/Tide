import os
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    docs_dir = Path(__file__).parent.resolve()
    html_path = docs_dir / "report_template.html"
    pdf_path = docs_dir / "Tide_CN_PBL_Project_Report.pdf"
    
    print(f"Loading: {html_path}")
    print(f"Output target: {pdf_path}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="networkidle")
        
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        )
        browser.close()
        
    print(f"Successfully generated PDF: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")

if __name__ == "__main__":
    main()
