# First-Time User Creation - Quick Start

## 🚀 30-Second Setup

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Run migrations (creates database schema)
flask db upgrade

# 3. Create admin user (interactive)
python3 create_user.py
```

Choose: Use default admin? **[Y/n]:** → Press Enter (or 'n' for custom)

Done! ✅

---

## 📋 Three Ways to Create Users

### Way 1: Interactive Script (Recommended)
```bash
python3 create_user.py
```
- User-friendly prompts
- Validation included
- Best for first-time setup

### Way 2: Flask CLI (For Administration)
```bash
flask create-user              # Interactive
flask create-user --username john --email john@company.com --password Pass123
```

### Way 3: List & Manage Users
```bash
flask list-users               # See all users
flask reset-password           # Change password
flask delete-user             # Remove user
```

---

## 💡 Common Tasks

| Task | Command |
|------|---------|
| Create admin (default) | `python3 create_user.py` then press Enter |
| Create admin (custom) | `python3 create_user.py` then 'n' for custom details |
| Create regular user | `flask create-user --username alice --email alice@co.com` |
| See all users | `flask list-users` |
| Change password | `flask reset-password --username admin` |
| Remove user | `flask delete-user --username olduser` |

---

## ✅ After Creating Users

1. Start app: `flask run`
2. Login: http://127.0.0.1:9191
3. Change password at `/security` page
4. Create todo items
5. Explore features

---

## 🔐 Security Tips

- ✅ Use strong passwords (12+ chars, mix of types)
- ✅ Change default credentials immediately
- ✅ Don't commit `.flaskenv` to git
- ✅ Protect database credentials
- ✅ Review users regularly: `flask list-users`

---

## 🐛 Quick Troubleshooting

| Error | Solution |
|-------|----------|
| "User already exists" | Use different name or `flask delete-user` first |
| "Database not found" | Run `flask db upgrade` first |
| "Permission denied" | Check file permissions with `ls -la` |
| "Invalid email" | Use format: `user@domain.com` |

---

**Full Guide:** See `USER_CREATION.md` for complete documentation  
**Version:** 1.0 | **Updated:** November 25, 2025
