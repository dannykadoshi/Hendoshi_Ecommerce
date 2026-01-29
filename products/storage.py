import os
import cloudinary.uploader
import cloudinary.utils
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.conf import settings


@deconstructible
class HybridCloudinaryStorage(Storage):
    """
    Hybrid storage that uploads to Cloudinary, falls back to local storage.
    Stores the full Cloudinary public_id (with folder) in the database.
    """

    def __init__(self):
        from django.core.files.storage import FileSystemStorage
        self.local_storage = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)

    def _save(self, name, content):
        """
        Save file to Cloudinary.
        `name` is the path Django wants to save to (e.g., 'products/filename.png')
        """
        try:
            # Use the full path as public_id (e.g., 'products/gallery/filename')
            # Remove extension for Cloudinary public_id
            public_id = os.path.splitext(name)[0]
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                content,
                public_id=public_id,
                overwrite=True,
                resource_type='auto'
            )

            # Return the public_id (without extension) which Cloudinary uses
            return result['public_id']
        except Exception as e:
            # If Cloudinary fails, fall back to local storage
            print(f"Cloudinary upload failed: {e}, falling back to local storage")
            return self.local_storage._save(name, content)

    def url(self, name):
        """
        Return the URL for the file.
        `name` is what's stored in the database - could be:
        - Cloudinary public_id (e.g., 'products/filename') - no extension
        - Local path (e.g., 'products/filename.png') - has extension
        """
        if not name:
            return ''

        try:
            # Check if this is a local file (has common image extension)
            ext = os.path.splitext(name)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg']:
                # This is a local file path with extension
                return f"{settings.MEDIA_URL}{name}"
            else:
                # This is a Cloudinary public_id (no extension)
                # Use Cloudinary's URL generation
                import cloudinary.utils
                cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME']
                url = cloudinary.utils.cloudinary_url(name, cloud_name=cloud_name, format='auto', quality='auto')[0]
                return url
        except Exception:
            # Fallback to local
            return f"{settings.MEDIA_URL}{name}"

    def exists(self, name):
        """
        Check if file exists in Cloudinary or locally.
        """
        if not name:
            return False

        try:
            ext = os.path.splitext(name)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg']:
                # Local file
                return self.local_storage.exists(name)
            else:
                # Cloudinary - check via API
                import cloudinary.api
                try:
                    cloudinary.api.resource(name)
                    return True
                except cloudinary.exceptions.NotFound:
                    return False
        except Exception:
            return self.local_storage.exists(name)

    def delete(self, name):
        """
        Delete file from Cloudinary or local storage.
        """
        if not name:
            return

        try:
            ext = os.path.splitext(name)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg']:
                # Local file
                self.local_storage.delete(name)
            else:
                # Cloudinary
                cloudinary.uploader.destroy(name)
        except Exception:
            pass

    def size(self, name):
        """
        Get file size.
        """
        if not name:
            return 0

        try:
            ext = os.path.splitext(name)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg']:
                return self.local_storage.size(name)
            else:
                import cloudinary.api
                result = cloudinary.api.resource(name)
                return result.get('bytes', 0)
        except Exception:
            return 0

    def accessed_time(self, name):
        from datetime import datetime
        return datetime.now()

    def created_time(self, name):
        from datetime import datetime
        return datetime.now()

    def modified_time(self, name):
        from datetime import datetime
        return datetime.now()
