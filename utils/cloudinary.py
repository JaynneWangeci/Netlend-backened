import cloudinary
import cloudinary.uploader
from config import Config

cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)

def upload_images(image_files):
    """Upload multiple images to Cloudinary and return URLs"""
    uploaded_urls = []
    
    for image_file in image_files:
        try:
            result = cloudinary.uploader.upload(
                image_file,
                folder="netlend/properties",
                resource_type="image"
            )
            uploaded_urls.append(result['secure_url'])
        except Exception as e:
            print(f"Error uploading image: {e}")
            continue
    
    return uploaded_urls

def upload_document(document_file, folder="netlend/documents"):
    """Upload a single document to Cloudinary"""
    try:
        result = cloudinary.uploader.upload(
            document_file,
            folder=folder,
            resource_type="auto"
        )
        return result['secure_url']
    except Exception as e:
        print(f"Error uploading document: {e}")
        return None