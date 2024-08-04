import json
from html import escape
import os

# Add error handling for pdfkit import
try:
    import pdfkit

    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False
    print("pdfkit is not installed. PDF generation will be unavailable.")


def json_to_html(json_data):
    def parse_section(data, level=2):
        html = ""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "content":
                    html += f"<p>{escape(value)}</p>\n"
                elif key == "items":
                    html += "<ul>\n"
                    for item in value:
                        html += f"<li>{escape(item)}</li>\n"
                    html += "</ul>\n"
                else:
                    html += f"<h{level}>{escape(key)}</h{level}>\n"
                    html += parse_section(value, level + 1)
        return html

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JSON Visualization</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            h2 { color: #2980b9; }
            h3 { color: #27ae60; }
            ul { margin-bottom: 20px; }
            li { margin-bottom: 5px; }
        </style>
    </head>
    <body>
    """

    for key, value in json_data.items():
        html += f"<h1>{escape(key)}</h1>\n"
        html += parse_section(value)

    html += """
    </body>
    </html>
    """

    return html


def create_pdf(html_content, output_file):
    """
    Create a PDF file from HTML content.

    :param html_content: String containing HTML content
    :param output_file: String, path to the output PDF file
    :return: Boolean indicating success or failure
    """
    if not PDFKIT_AVAILABLE:
        print("Cannot create PDF: pdfkit is not installed.")
        return False

    try:
        pdfkit.from_string(html_content, output_file)
        if os.path.exists(output_file):
            print(f"PDF file generated successfully: {output_file}")
            return True
        else:
            print(f"PDF file was not created at the specified location: {output_file}")
            return False
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        print("Make sure wkhtmltopdf is installed on your system.")
        return False


def process_json_to_html_and_pdf(json_file, html_file, pdf_file):
    """
    Process JSON file to HTML and PDF.

    :param json_file: Path to the input JSON file
    :param html_file: Path to the output HTML file
    :param pdf_file: Path to the output PDF file
    """
    # Load JSON data
    try:
        with open(json_file, "r") as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"JSON file not found: {json_file}")
        return
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {json_file}")
        return

    # Generate HTML
    html_output = json_to_html(json_data)

    # Save HTML file
    try:
        with open(html_file, "w") as f:
            f.write(html_output)
        print(f"HTML file generated successfully: {html_file}")
    except IOError as e:
        print(f"Error writing HTML file: {str(e)}")
        return

    # Create PDF
    pdf_created = create_pdf(html_output, pdf_file)

    if pdf_created:
        print("Both HTML and PDF files have been generated.")
    else:
        print("HTML file was generated, but there was an issue with PDF creation.")


def generate_appraisal_docs(input_json_file:str):
    # Use the current working directory
    current_dir = os.getcwd()

    # Define input and output file paths
    html_file = os.path.join(current_dir, "appraisal.html")
    pdf_file = os.path.join(current_dir, "appraisal.pdf")

    process_json_to_html_and_pdf(input_json_file, html_file, pdf_file)

    print(f"Current working directory: {current_dir}")
    print(f"JSON file path: {input_json_file}")
    print(f"HTML file path: {html_file}")
    print(f"PDF file path: {pdf_file}")


# Example usage
if __name__ == "__main__":
    generate_appraisal_docs()
