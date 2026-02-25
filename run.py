from app import create_app  

app = create_app()

@app.route('/test-supabase')
def test_supabase():
    try:
        users = app.supabase.table('users').select('count').execute()
        count = users.data[0]['count'] if users.data else 0
        return f"✅ Supabase Connected! {count} users found"
    except Exception as e:
        return f"❌ Supabase Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
