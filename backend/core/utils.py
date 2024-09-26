import uuid

def generate_small_uuid():
        return str(uuid.uuid4())[:6]