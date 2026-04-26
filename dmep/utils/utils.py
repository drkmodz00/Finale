import uuid

def get_guest_id(request):
    guest_id = request.COOKIES.get('guest_id')

    if not guest_id:
        guest_id = str(uuid.uuid4())

    return guest_id