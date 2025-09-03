from application.models import Application
from django.core.files.base import ContentFile
from PIL import Image
import io

# Get the first Application without a profile pic
app = Application.objects.filter(profile_pic="").first()

# Create a simple image with Pillow
img = Image.new("RGB", (200, 200), color="blue")

# Save image to a BytesIO buffer
buffer = io.BytesIO()
img.save(buffer, format="PNG")

# Save to model's ImageField
app.profile_pic.save("profile.png", ContentFile(buffer.getvalue()), save=True)
