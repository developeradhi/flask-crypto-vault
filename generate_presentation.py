from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def apply_styling(slide, prs):
    # Set dark background
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(15, 23, 42) # Dark Slate

    # Style all text shapes on the slide
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.name = 'Century Gothic'
                # If it's a title (usually the first shape or large text)
                if shape == slide.shapes[0]:
                    run.font.color.rgb = RGBColor(6, 182, 212) # Cyan Accent
                    run.font.bold = True
                else:
                    run.font.color.rgb = RGBColor(248, 250, 252) # White text

def create_presentation():
    prs = Presentation()
    
    # 1. Title Slide
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = "Ultimate Security Suite"
    subtitle.text = "Next-Generation Local Data Protection\nPresented by: The Development Team"
    
    # Manually style the title slide
    apply_styling(slide, prs)
    for p in subtitle.text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = RGBColor(148, 163, 184) # Muted Text

    # 2. Project Overview
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "Project Overview"
    
    content = slide.placeholders[1]
    tf = content.text_frame
    tf.text = "A 100% offline, zero-trust cybersecurity web application."
    p = tf.add_paragraph()
    p.text = "Designed for military-grade data protection without relying on cloud services."
    p = tf.add_paragraph()
    p.text = "All encryption and processing happen locally on the user's CPU."
    p = tf.add_paragraph()
    p.text = "Protected by a Master Password and AES-256 Key infrastructure."
    apply_styling(slide, prs)

    # 3. Core Feature: File Vault
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "Core Feature: The File Vault"
    
    content = slide.placeholders[1]
    tf = content.text_frame
    tf.text = "Encrypts files of any type (PDF, Images, Documents) using AES-256."
    p = tf.add_paragraph()
    p.text = "Secure Shredder: Replaces deleted files with random data bytes to prevent forensic recovery."
    p = tf.add_paragraph()
    p.text = "Batch Processing: Drag and drop capabilities."
    apply_styling(slide, prs)

    # 4. Core Feature: Secret Chat
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "Core Feature: Secret Chat"
    
    content = slide.placeholders[1]
    tf = content.text_frame
    tf.text = "Encrypts raw text messages into a secure ciphertext block."
    p = tf.add_paragraph()
    p.text = "Perfect for sending sensitive data (passwords, bank info) over email or WhatsApp."
    p = tf.add_paragraph()
    p.text = "Decryption requires the exact local key."
    apply_styling(slide, prs)



    # 6. Technical Stack
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "Technical Architecture"
    
    content = slide.placeholders[1]
    tf = content.text_frame
    tf.text = "Backend: Python, Flask (Web Framework)"
    p = tf.add_paragraph()
    p.text = "Security: Cryptography (Fernet AES), Hashlib (SHA-256)"

    p = tf.add_paragraph()
    p.text = "Frontend: HTML, CSS, JavaScript (Glassmorphism aesthetics)"
    apply_styling(slide, prs)

    # 7. Security Philosophy
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "Security Philosophy"
    
    content = slide.placeholders[1]
    tf = content.text_frame
    tf.text = "No 'Forgot Password' backdoor: Enforces strict user responsibility."
    p = tf.add_paragraph()
    p.text = "Offline by Default: Zero risk of cloud data breaches."
    p = tf.add_paragraph()
    p.text = "Zero-Trust: The application requires authentication even for local access."
    apply_styling(slide, prs)

    prs.save('Ultimate_Security_Suite_Presentation.pptx')
    print("Attractive presentation saved successfully.")

if __name__ == '__main__':
    create_presentation()
