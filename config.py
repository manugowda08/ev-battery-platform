import os
from supabase import create_client, Client

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('sb_secret_umLsvBQc91dgOvZspodNtw_wUn4eIzQ') or 'dev-change-in-production'
    SUPABASE_URL = os.environ.get('https://ulyocqshdtqgwrcwgxik.supabase.co')
    SUPABASE_ANON_KEY = os.environ.get('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVseW9jcXNoZHRxZ3dyY3dneGlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE5NTAxNTUsImV4cCI6MjA4NzUyNjE1NX0.7JbBhOx_-8aznbzj2EEu5cMNPJ5c_J0r-UdRZlEUUOk')
    
    @staticmethod
    def get_supabase() -> Client:
        return create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
