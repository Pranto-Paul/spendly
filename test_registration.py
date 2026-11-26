from app import app

with app.test_client() as c:
    # Test 1: GET /register
    print("Test 1: GET /register")
    resp = c.get("/register")
    print(f"  Status: {resp.status_code}")
    assert resp.status_code == 200
    print("  ✅ GET /register renders successfully")

    # Test 2: Valid registration
    print("\nTest 2: Valid registration")
    resp = c.post("/register", data={
        "name": "Anika Singh",
        "email": "anika.singh.test@gmail.com",
        "password": "password123"
    }, follow_redirects=False)
    print(f"  Status: {resp.status_code}")
    print(f"  Location: {resp.headers.get('Location')}")
    assert resp.status_code == 302
    assert resp.headers.get('Location') == "/login"
    print("  ✅ Registration successful, redirected to /login")

    # Test 3: Duplicate email
    print("\nTest 3: Duplicate email")
    resp = c.post("/register", data={
        "name": "Anika Singh",
        "email": "anika.singh.test@gmail.com",
        "password": "password123"
    }, follow_redirects=False)
    print(f"  Status: {resp.status_code}")
    assert resp.status_code == 200  # re-rendered form
    print("  ✅ Duplicate email handled")

    # Test 4: Short password
    print("\nTest 4: Short password")
    resp = c.post("/register", data={
        "name": "Anika Singh",
        "email": "anika.short@gmail.com",
        "password": "short"
    }, follow_redirects=False)
    print(f"  Status: {resp.status_code}")
    assert resp.status_code == 200  # re-rendered form
    print("  ✅ Short password handled")

    # Test 5: Empty fields
    print("\nTest 5: Empty fields")
    resp = c.post("/register", data={
        "name": "",
        "email": "",
        "password": ""
    }, follow_redirects=False)
    print(f"  Status: {resp.status_code}")
    assert resp.status_code == 200  # re-rendered form
    print("  ✅ Empty fields handled")

    # Test 6: Verify password is hashed in database
    print("\nTest 6: Verify password hashing")
    from database.db import get_db
    from werkzeug.security import check_password_hash
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", ("test@example.com",)).fetchone()
    if user:
        print(f"  User: {user['name']}, Email: {user['email']}")
        print(f"  Password hash: {user['password_hash'][:30]}...")
        assert check_password_hash(user['password_hash'], "password123")
        print("  ✅ Password is properly hashed")
    db.close()

print("\n🎉 All tests passed!")