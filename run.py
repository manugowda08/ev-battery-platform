from app import create_app
from app.config import Config

app = create_app()
supabase = Config.get_supabase()

@app.route('/test-supabase')
def test_supabase():
    try:
        users = supabase.table('users').select('count').execute()
        return f"✅ Supabase Connected! {users} users found"
    except Exception as e:
        return f"❌ Supabase Error: {str(e)}"
