import uuid
import string
import random
def generate_small_uuid():
        return str(uuid.uuid4())[:6]

def generate_unique_uid(length=4):
    """Generates a unique UID for any model that inherits from UidBaseModel."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))