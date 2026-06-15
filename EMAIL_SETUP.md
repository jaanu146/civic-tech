## 📧 Email Configuration Guide

### Fix OTP Email Issue

If OTP is not being received, follow these steps:

---

### Step 1: Get Gmail App Password

1. Go to: https://myaccount.google.com/
2. Click **Security** (left menu)
3. Enable 2-Step Verification if not already enabled
4. Go to **App passwords** (at bottom)
5. Select: **Mail** and **Windows Computer**
6. Copy the **16-character password** (without spaces)

Example: `abcd efgh ijkl mnop` → Use as `abcdefghijklmnop`

---

### Step 2: Update app.py

Replace these lines:

```python
app.config['MAIL_USERNAME'] = 'YOUR_GMAIL_HERE@gmail.com'
app.config['MAIL_PASSWORD'] = 'YOUR_APP_PASSWORD_HERE'
```

Example:
```python
app.config['MAIL_USERNAME'] = 'myemail@gmail.com'
app.config['MAIL_PASSWORD'] = 'abcdefghijklmnop'
```

---

### Step 3: Test Email

1. Start app: `python app.py`
2. Open browser: `http://localhost:5000/test-email/youremail@gmail.com`
3. Check if you received the test email

---

### Step 4: If Still Not Working

Check console output when you login (the errors will show WHY email failed):

Examples you might see:
- `❌ Email sending FAILED to ...`
- `Error: [Errno -3] Temporary failure in name resolution` → Network issue
- `Error: 535 5.7.8 Username and password not accepted` → Wrong credentials
- `Error: 535 5.7.9 Application-specific password required` → Need app password, not regular password

---

### Alternative: Use Different Email (Optional)

If Gmail is problematic, use **outlook.com**:

```python
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'youremail@outlook.com'
app.config['MAIL_PASSWORD'] = 'your_outlook_password'
```

Or **SendGrid** (free tier):
```python
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = 'SG.YOUR_API_KEY_HERE'
```

---

### Verify in Database

User data IS saved even if email fails:

```sql
psql -d civic_db
SELECT email, name FROM users;
```

You'll see registered users regardless of email status.
