# views.py

from django.http import JsonResponse
from dmep.services.supabase_client import supabase

def test_supabase(request):
    data = supabase.table("todos").select("*").execute()
    return JsonResponse(data.data, safe=False)
    