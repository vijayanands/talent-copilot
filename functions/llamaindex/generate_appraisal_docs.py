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


def json_to_html(json_file_path, html_file_path):
    # Read the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Create the HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Review</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2 {{
            color: #2c3e50;
        }}
        ul {{
            padding-left: 20px;
        }}
        .section {{
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>Performance Review</h1>

    <div class="section">
        <h2>Summary</h2>
        <p>{escape(data['Summary'])}</p>
    </div>

    <div class="section">
        <h2>Key Achievements</h2>
        <ul>
            {''.join(f'<li>{escape(achievement)}</li>' for achievement in data['Key Achievements'])}
        </ul>
    </div>

    <div class="section">
        <h2>Contributions</h2>

        {''.join(f'''
        <h3>{escape(platform)}</h3>
        <p>{escape(details['Description'])}</p>
        {'<ul>' + ''.join(f'<li><strong>{escape(name)}:</strong> <a href="#">{escape(link)}</a></li>' for name, link in details.get('Links', {}).items()) + '</ul>' if 'Links' in details else ''}
        ''' for platform, details in data['Contributions'].items())}
    </div>

    <div class="section">
        <h2>Learning Opportunities</h2>
        <ul>
            {''.join(f'<li>{escape(opportunity)}</li>' for opportunity in data['Learning Opportunities'])}
        </ul>
    </div>
</body>
</html>
    """

    # Write the HTML content to a file
    with open(html_file_path, 'w') as file:
        file.write(html_content)
    return html_content


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

    # Generate HTML
    html_output = json_to_html(json_file, html_file)

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
