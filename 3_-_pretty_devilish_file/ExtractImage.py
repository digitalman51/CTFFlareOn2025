import fitz  # PyMuPDF
import os

def extract_images_from_pdf(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    pdf = fitz.open(pdf_path)
    print(f"[+] Opened {pdf_path} with {len(pdf)} pages")

    count = 0
    for page_index in range(len(pdf)):
        page = pdf[page_index]
        images = page.get_images(full=True)

        print(f"[*] Page {page_index+1}: {len(images)} images found")

        for img_index, img in enumerate(images, start=1):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_name = f"page{page_index+1}_img{img_index}.{image_ext}"

            image_path = os.path.join(output_folder, image_name)
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            print(f"    → Saved {image_name} ({len(image_bytes)} bytes)")
            count += 1

    pdf.close()
    print(f"\n[+] Done! Extracted {count} images to: {output_folder}")

# Example usage:
# extract_images_from_pdf("repair.pdf", "extracted_images")
