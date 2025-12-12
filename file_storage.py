import os
from supabase import create_client, Client
from config import settings

UPLOAD_DIR = "uploads"
supabase: Client = create_client(str(settings.SUPABASE_URL), settings.SUPABASE_KEY)

def upload_file(bucket_name, path, contents, content_type):
  if settings.PRODUCTION:
    response = supabase.storage.from_(bucket_name) \
                .upload(path, contents, {"content-type": content_type})
    return f"{str(settings.SUPABASE_URL)}/storage/v1/object/public/{response.full_path}"
  else:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, bucket_name, path)
    with open(file_path, "wb") as f:
        f.write(contents)
    return f"/{UPLOAD_DIR}/{bucket_name}/{path}"