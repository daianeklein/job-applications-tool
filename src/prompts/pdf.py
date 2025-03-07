from fpdf import FPDF
# from job_description import job_description_text as file
from job_description import job_description_text as file


# Extract the text variable
docstring_text = file.strip()

# Initialize PDF object
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)

# Add text to PDF
pdf.multi_cell(0, 10, docstring_text)

# Save PDF
pdf.output("docstring_output.pdf")

print("PDF saved successfully as 'docstring_output.pdf'")
