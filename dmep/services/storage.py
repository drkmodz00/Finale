import uuid
from dmep.services.supabase import supabase

def upload_to_supabase(file, folder="products"):
    file_path = f"{folder}/{uuid.uuid4()}_{file.name}"

    supabase.storage.from_("media").upload(
        file_path,
        file.read(),
        {"content-type": file.content_type}
    )

    return supabase.storage.from_("media").get_public_url(file_path)