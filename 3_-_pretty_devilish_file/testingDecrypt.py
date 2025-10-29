from pypdf import PdfReader, PdfWriter

reader = PdfReader("pretty_devilish_file.pdf")
if reader.is_encrypted:
    reader.decrypt("N0t_a_flag_but_just_a_line_comment")

writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)

with open("decrypted-pdf.pdf", "wb") as f:
    writer.write(f)