from django.db import models
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
from django.templatetags.static import static


# Create your models here.
class Category(models.Model):
    """
    Represents a group of animals kept or rescued by the farm.
    Categories allow visitors to browse animals by type
    (e.g., Horses, Poultry, Wildlife).

    Relationships:
        - One Category can have many Animals (related_name="animals").
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Animal(models.Model):
    """
    Represents an individual rescued animal.

    Key features:
        - Linked to a Category (optional: if Category deleted, animal is kept).
        - Automatically generates a unique slug based on the name.
        - Stores optional Cloudinary image.
        - Provides a fallback local static placeholder if no image exists.
        - Includes story, breed and activity status.
        - Tracks creation and update timestamps.

    Relationships:
        - Each Animal belongs to one Category (ForeignKey).
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="animals"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    species = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    story = models.TextField(blank=True, null=True)

    image = CloudinaryField(
        'animal_image',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    date_deceased = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def image_or_placeholder(self):
        """
        Returns the Cloudinary image URL if available,
        otherwise returns a local static placeholder image.

        Use this in templates:
            <img src="{{ animal.image_or_placeholder }}" ...>
        """
        if self.image and getattr(self.image, 'url', None):
            return self.image.url
        return static('images/animal_placeholder.jpg')

    def save(self, *args, **kwargs):
        """
        Auto-generate a unique slug from the name if not provided.
        Ensures slugs remain unique even when names repeat.
        """
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Animal.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)
