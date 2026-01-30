import os
import logging
import cloudinary
import cloudinary.uploader
import cloudinary.utils
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.conf import settings

logger = logging.getLogger(__name__)


def _ensure_cloudinary_configured():
    """Ensure cloudinary is configured from environment."""
    if not cloudinary.config().cloud_name:
        # Try to configure from CLOUDINARY_URL environment variable
        cloudinary_url = os.environ.get('CLOUDINARY_URL', '')
        if cloudinary_url:
            cloudinary.config(cloudinary_url=cloudinary_url)
            logger.info(f"Cloudinary configured with cloud: {cloudinary.config().cloud_name}")
        else:
            logger.error("CLOUDINARY_URL environment variable not set!")


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
        # Ensure cloudinary is configured
        _ensure_cloudinary_configured()

        try:
            # Reset file position to beginning (Django may have read it already)
            if hasattr(content, 'seek'):
                content.seek(0)

            # Use the full path as public_id (e.g., 'products/gallery/filename')
            # Remove extension for Cloudinary public_id
            public_id = os.path.splitext(name)[0]

            logger.info(f"Uploading to Cloudinary: {public_id} (cloud: {cloudinary.config().cloud_name})")

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

        # Ensure cloudinary is configured
        _ensure_cloudinary_configured()

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

            # Check if cloudinary is configured
            cloud_name = cloudinary.config().cloud_name
            if not cloud_name:
                logger.error(f"Cloudinary not configured! Cannot generate URL for {name}")
                if settings.DEBUG:
                    return f"{settings.MEDIA_URL}{name}"
                return ''

            # Generate Cloudinary URL
            url, _ = cloudinary.utils.cloudinary_url(
                public_id,
                format='auto',
                quality='auto'
            )

            logger.debug(f"Generated Cloudinary URL for {public_id}: {url}")

            if url:
                return url

            # Fallback to local URL (only useful in development)
            if settings.DEBUG:
                return f"{settings.MEDIA_URL}{name}"

            # In production without Cloudinary, log error
            logger.error(f"Could not generate URL for {name}: cloudinary_url returned empty")
            return ''

        except Exception as e:
            logger.error(f"Error generating URL for {name}: {e}", exc_info=True)
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
