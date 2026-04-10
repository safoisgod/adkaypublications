"""
Reusable image utilities:
- Convert any uploaded image to WebP before sending to Cloudinary
- Delete old Cloudinary asset when image is replaced
- Delete Cloudinary asset when model instance is deleted
"""
import io
import logging
from PIL import Image as PillowImage
from django.core.files.uploadedfile import InMemoryUploadedFile
import cloudinary.uploader

logger = logging.getLogger('apps.core')


def convert_to_webp(image_file):
    """
    Convert any uploaded image file to WebP format.
    Preserves transparency (RGBA). Returns an InMemoryUploadedFile.
    Returns the original file unchanged if conversion fails.
    """
    try:
        img = PillowImage.open(image_file)

        # Preserve transparency for PNG/GIF; convert others to RGBA safely
        if img.mode in ('RGBA', 'LA'):
            mode = 'RGBA'
        elif img.mode == 'P' and 'transparency' in img.info:
            img = img.convert('RGBA')
            mode = 'RGBA'
        else:
            img = img.convert('RGB')
            mode = 'RGB'

        output = io.BytesIO()
        img.save(output, format='WEBP', quality=85, method=6)
        output.seek(0)

        original_name = getattr(image_file, 'name', 'image')
        webp_name = original_name.rsplit('.', 1)[0] + '.webp'

        return InMemoryUploadedFile(
            file=output,
            field_name=None,
            name=webp_name,
            content_type='image/webp',
            size=output.getbuffer().nbytes,
            charset=None,
        )
    except Exception as e:
        logger.warning(f"WebP conversion failed, using original: {e}")
        return image_file


def delete_cloudinary_resource(public_id):
    """
    Delete a single asset from Cloudinary by public_id.
    Silently logs errors — never raises.
    """
    if not public_id:
        return
    try:
        cloudinary.uploader.destroy(str(public_id))
        logger.info(f"Deleted Cloudinary asset: {public_id}")
    except Exception as e:
        logger.warning(f"Could not delete Cloudinary asset {public_id}: {e}")


class CloudinaryImageMixin:
    """
    Mixin for Django models with CloudinaryField images.

    Usage:
        class MyModel(CloudinaryImageMixin, TimeStampedModel):
            CLOUDINARY_IMAGE_FIELDS = ['cover_image']  # list your field names
            ...

    Provides:
        - Auto WebP conversion before save
        - Old asset cleanup when image is replaced
        - Asset cleanup when instance is deleted
    """

    # Subclasses must declare which fields to manage
    CLOUDINARY_IMAGE_FIELDS = []

    def save(self, *args, **kwargs):
        # Convert new uploads to WebP and track replaced assets for cleanup
        old_public_ids = []

        for field_name in self.CLOUDINARY_IMAGE_FIELDS:
            new_file = self._get_new_file(field_name)
            if new_file is None:
                continue

            # Convert to WebP
            converted = convert_to_webp(new_file)
            # Replace the file on the field before Cloudinary uploads it
            self._set_field_file(field_name, converted)

            # Collect old public_id for cleanup after save
            old_id = self._get_current_public_id(field_name)
            if old_id:
                old_public_ids.append(old_id)

        super().save(*args, **kwargs)

        # Clean up replaced assets after successful save
        for public_id in old_public_ids:
            delete_cloudinary_resource(public_id)

    def delete(self, *args, **kwargs):
        # Collect public_ids before deletion
        public_ids = [
            self._get_current_public_id(f)
            for f in self.CLOUDINARY_IMAGE_FIELDS
        ]
        super().delete(*args, **kwargs)
        for public_id in public_ids:
            delete_cloudinary_resource(public_id)

    # ── Internal helpers ──────────────────────────────────────────────────

    def _get_new_file(self, field_name):
        """
        Return the raw uploaded file object if a new file is being set,
        otherwise None.
        """
        field_file = getattr(self, field_name, None)
        if field_file is None:
            return None
        # CloudinaryField stores a CloudinaryResource after upload.
        # During a form POST, the underlying file is attached here:
        raw = getattr(field_file, 'file', None)
        if raw and hasattr(raw, 'read'):
            # Check it's a real upload (not a cached Cloudinary URL object)
            if hasattr(raw, 'name') or hasattr(raw, 'size'):
                return raw
        return None

    def _set_field_file(self, field_name, new_file):
        """Replace the file on a CloudinaryField before upload."""
        field_file = getattr(self, field_name)
        if hasattr(field_file, 'file'):
            field_file.file = new_file
        else:
            setattr(self, field_name, new_file)

    def _get_current_public_id(self, field_name):
        """
        Get the current Cloudinary public_id stored in the DB for this field,
        so we can delete it after replacement.
        """
        if not self.pk:
            return None
        try:
            db_instance = self.__class__.objects.get(pk=self.pk)
            field_val = getattr(db_instance, field_name)
            # CloudinaryField value is a CloudinaryResource with public_id
            public_id = getattr(field_val, 'public_id', None) or str(field_val or '')
            return public_id if public_id else None
        except self.__class__.DoesNotExist:
            return None