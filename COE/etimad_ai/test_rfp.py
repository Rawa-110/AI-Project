from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

file_name = "test_rfp.pdf"

c = canvas.Canvas(file_name, pagesize=A4)

text = c.beginText(50, 800)
text.setFont("Helvetica", 11)

lines = [
    "Etimad AI - TEST RFP",
    "",
    "Government Digital Transformation Project",
    "",
    "Project Scope:",
    "The supplier shall provide a digital transformation solution",
    "including implementation, technical support and training.",
    "",
    "Submission Deadline: 30 September 2026",
    "",
    "Required Documents:",
    "- Company profile",
    "- Previous experience",
    "- Technical proposal",
    "- Implementation plan",
    "",
    "Evaluation Criteria:",
    "- Technical proposal: 60%",
    "- Previous experience: 20%",
    "- Implementation plan: 20%",
    "",
    "Initial Guarantee: 50,000 SAR",
]

for line in lines:
    text.textLine(line)

c.drawText(text)
c.save()

print(f"Created: {file_name}")