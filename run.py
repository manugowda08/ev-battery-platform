from app.backend import create_app
from app.backend.config import Config

app = create_app()

# Test Supabase connection route
@app.route('/test-supabase')
def test_supabase():
    try:
        supabase = Config.get_supabase()
        users = supabase.table('users').select('count').execute()
        return f"✅ Supabase Connected! {len(users.data)} users found"
    except Exception as e:
        return f"❌ Supabase Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
