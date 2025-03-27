import qrcode
import streamlit as st
from PIL import Image
import io

def generate_qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    return img

# Streamlit UI
st.title("QR Code Generator")
url = st.text_input("Enter the URL:")

if st.button("Generate QR Code"):
    if url:
        qr_image = generate_qr(url)
        img_bytes = io.BytesIO()
        qr_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        st.image(img_bytes, caption="Your QR Code", use_container_width=True)
        
        if st.checkbox("Do you want to save the QR code?"):
            filename = st.text_input("Enter filename (without .png):", "qrcode")
            if st.button("Save QR Code"):
                file_path = f"{filename}.png"
                qr_image.save(file_path)
                st.success(f'QR code saved as {file_path}')
    else:
        st.error("Please enter a valid URL")
