from app.backend import create_app

app = create_app()

@app.route('/test-supabase')
def test_supabase():
    try:
        # Use app.supabase (set in create_app)
        users = app.supabase.table('users').select('count').execute()
        return f"✅ Supabase Connected! {len(users.data)} users found"
    except Exception as e:
        return f"❌ Supabase Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
