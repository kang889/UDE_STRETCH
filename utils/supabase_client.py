from supabase import create_client

SUPABASE_URL = "https://tmreriiigvnwllgbigtu.supabase.co"
SUPABASE_KEY = "sb_publishable_x1450ousExFiCLqS469NwQ_sjuE1tPB"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

