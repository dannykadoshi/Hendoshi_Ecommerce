import cloudinary.uploader
from django.core.files.storage import Storage
from django.core.files.base import File
from django.utils.deconstruct import deconstructible


@deconstructible
class CloudinaryStorage(Storage):
    """
    Custom Cloudinary storage backend for Django
    """

    def __init__(self):
        pass

    def _save(self, name, content):
        """
        Save file to Cloudinary
        """
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

    def url(self, name):
        """
        Return the URL for the file
        """
        from django.conf import settings
        cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME']
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{name}.png"

    def exists(self, name):
        """
        Check if file exists (not implemented for Cloudinary)
        """
        return False

    def delete(self, name):
        """
        Delete file from Cloudinary
        """
        try:
            cloudinary.uploader.destroy(name)
        except:
            pass

    def size(self, name):
        """
        Get file size (not implemented)
        """
        return 0

    def accessed_time(self, name):
        """
        Get accessed time (not implemented)
        """
        from datetime import datetime
        return datetime.now()

    def created_time(self, name):
        """
        Get created time (not implemented)
        """
        from datetime import datetime
        return datetime.now()

    def modified_time(self, name):
        """
        Get modified time (not implemented)
        """
        from datetime import datetime
        return datetime.now()