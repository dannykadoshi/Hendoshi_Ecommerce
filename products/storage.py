import os
import cloudinary.uploader
from django.core.files.storage import Storage, default_storage
from django.core.files.base import File
from django.utils.deconstruct import deconstructible
from django.conf import settings


@deconstructible
class HybridCloudinaryStorage(Storage):
    """
    Hybrid storage that tries Cloudinary first, falls back to local storage
    """

    def __init__(self):
        from django.core.files.storage import FileSystemStorage
        self.local_storage = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)

    def _save(self, name, content):
        """
        Save file to Cloudinary
        """
        try:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                content,
                folder='products',  # Default folder
                public_id=name.split('/')[-1].split('.')[0],  # Extract filename without extension
                overwrite=True,
                resource_type='auto'
            )
            # Return the public_id which will be stored in the database
            return result['public_id']
        except Exception as e:
            # If Cloudinary fails, fall back to local storage
            print(f"Cloudinary upload failed: {e}, falling back to local storage")
            return self.local_storage._save(name, content)

    def url(self, name):
        """
        Return the URL for the file - Cloudinary for new uploads, local for existing
        """
        try:
            # If name has a file extension, it's a local file path
            if '.' in name and name.split('.')[-1].lower() in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                # Local file path - return local URL
                return f"{settings.MEDIA_URL}{name}"
            else:
                # Cloudinary public_id
                cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME']
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{name}.png"
        except:
            # Fallback to local
            return f"{settings.MEDIA_URL}{name}"

    def exists(self, name):
        """
        Check if file exists in Cloudinary or locally
        """
        try:
            # Try Cloudinary first
            if '/' not in name or name.startswith('products/'):
                # Check Cloudinary
                result = cloudinary.api.resource(name)
                return result is not None
            else:
                # Check local
                return self.local_storage.exists(name)
        except:
            # Check local as fallback
            return self.local_storage.exists(name)

    def delete(self, name):
        """
        Delete file from Cloudinary or local
        """
        try:
            if '/' not in name or name.startswith('products/'):
                cloudinary.uploader.destroy(name)
            else:
                self.local_storage.delete(name)
        except:
            pass

    def size(self, name):
        """
        Get file size
        """
        try:
            if '/' not in name or name.startswith('products/'):
                result = cloudinary.api.resource(name)
                return result.get('bytes', 0)
            else:
                return self.local_storage.size(name)
        except:
            return self.local_storage.size(name)

    def accessed_time(self, name):
        """
        Get accessed time
        """
        from datetime import datetime
        return datetime.now()

    def created_time(self, name):
        """
        Get created time
        """
        from datetime import datetime
        return datetime.now()

    def modified_time(self, name):
        """
        Get modified time
        """
        from datetime import datetime
        return datetime.now()