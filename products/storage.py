import os
import logging
import cloudinary.uploader
import cloudinary.utils
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.conf import settings

logger = logging.getLogger(__name__)


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
            # Reset file position to beginning (Django may have read it already)
            if hasattr(content, 'seek'):
                content.seek(0)

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

            logger.info(f"Cloudinary upload successful: {result['public_id']}")
            # Return the public_id (without extension) which Cloudinary uses
            return result['public_id']
        except Exception as e:
            # Log the error with full details
            logger.error(f"Cloudinary upload failed for {name}: {e}", exc_info=True)

            # In production (DEBUG=False), don't fall back to local storage
            # because Render's filesystem is ephemeral and files won't persist
            if not settings.DEBUG:
                raise Exception(f"Cloudinary upload failed: {e}. Local fallback disabled in production.")

            # In development, fall back to local storage
            logger.warning(f"Falling back to local storage for {name}")
            return self.local_storage._save(name, content)

    def url(self, name):
        """
        Return the URL for the file.
        `name` is what's stored in the database - could be:
        - Cloudinary public_id (e.g., 'products/filename') - no extension
        - Local path (e.g., 'products/filename.png') - has extension (legacy/dev)
        """
        if not name:
            return ''

        try:
            ext = os.path.splitext(name)[1].lower()
            image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg']

            # Determine the public_id for Cloudinary
            if ext in image_extensions:
                # Has extension - could be legacy local file or incorrectly stored
                # Strip extension to get Cloudinary public_id
                public_id = os.path.splitext(name)[0]
            else:
                # No extension - this is a proper Cloudinary public_id
                public_id = name

            # Always try to generate Cloudinary URL first (works in production)
            # Use cloudinary's built-in config (from CLOUDINARY_URL or explicit config)
            url, _ = cloudinary.utils.cloudinary_url(
                public_id,
                format='auto',
                quality='auto'
            )
            if url:
                return url

            # Fallback to local URL (only useful in development)
            if settings.DEBUG:
                return f"{settings.MEDIA_URL}{name}"

            # In production without Cloudinary, log error
            logger.error(f"Could not generate URL for {name}: Cloudinary not configured")
            return ''

        except Exception as e:
            logger.error(f"Error generating URL for {name}: {e}")
            # Fallback to local in development only
            if settings.DEBUG:
                return f"{settings.MEDIA_URL}{name}"
            return ''

    def exists(self, name):
        """
        Check if file exists in Cloudinary or locally.
        """
        if not name:
            return False

        try:
            import cloudinary.api
            ext = os.path.splitext(name)[1].lower()
            image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg']

            # Get the public_id (strip extension if present)
            public_id = os.path.splitext(name)[0] if ext in image_extensions else name

            # Try Cloudinary first
            try:
                cloudinary.api.resource(public_id)
                return True
            except cloudinary.exceptions.NotFound:
                pass

            # Fall back to local check in development
            if settings.DEBUG:
                return self.local_storage.exists(name)

            return False
        except Exception as e:
            logger.error(f"Error checking existence for {name}: {e}")
            if settings.DEBUG:
                return self.local_storage.exists(name)
            return False

    def delete(self, name):
        """
        Delete file from Cloudinary or local storage.
        """
        if not name:
            return

        try:
            ext = os.path.splitext(name)[1].lower()
            image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg']

            # Get the public_id (strip extension if present)
            public_id = os.path.splitext(name)[0] if ext in image_extensions else name

            # Try to delete from Cloudinary
            result = cloudinary.uploader.destroy(public_id)
            logger.info(f"Cloudinary delete for {public_id}: {result}")

            # Also try to delete locally in development
            if settings.DEBUG:
                try:
                    self.local_storage.delete(name)
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Error deleting {name}: {e}")

    def size(self, name):
        """
        Get file size.
        """
        if not name:
            return 0

        try:
            import cloudinary.api
            ext = os.path.splitext(name)[1].lower()
            image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg']

            # Get the public_id (strip extension if present)
            public_id = os.path.splitext(name)[0] if ext in image_extensions else name

            # Try Cloudinary first
            try:
                result = cloudinary.api.resource(public_id)
                return result.get('bytes', 0)
            except cloudinary.exceptions.NotFound:
                pass

            # Fall back to local in development
            if settings.DEBUG:
                return self.local_storage.size(name)

            return 0
        except Exception as e:
            logger.error(f"Error getting size for {name}: {e}")
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
