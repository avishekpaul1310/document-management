from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

def validate_file_type(value):
    # Get the file extension
    ext = os.path.splitext(value.name)[1]
    # Define valid file extensions
    valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.png', '.jpg', '.jpeg']
    
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file type. Allowed types: PDF, Word, Excel, and Images')

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to='documents/',
        validators=[validate_file_type]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_private = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        # Delete the file from storage when deleting the document
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def send_upload_notification(self):
        if not self.owner.email:
            logger.warning(f"No email address for user {self.owner.username}")
            return

        site_domain = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')
        document_url = f"http://{site_domain}/document/{self.pk}/"

        subject = f'New Document Uploaded: {self.title}'
        message = f"""
        Hello {self.owner.username},

        A new document has been uploaded to your account:

        Title: {self.title}
        Category: {self.category}
        Upload Date: {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}
        Privacy: {'Private' if self.is_private else 'Public'}

        You can view it on your dashboard at:
        {document_url}

        Best regards,
        Document Management System
        """
        
        try:
            sent = send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.owner.email],
                fail_silently=False,
            )
            if sent:
                logger.info(f"Email notification sent for document {self.title} to {self.owner.email}")
            else:
                logger.error(f"Failed to send email notification for document {self.title}")
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.send_upload_notification()