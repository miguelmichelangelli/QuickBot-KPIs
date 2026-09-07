import uuid

def generate_uuid():
    id = str(uuid.uuid4())[24:]
    return id