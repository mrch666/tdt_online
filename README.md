# Project Setup

## Environment Variables Configuration

1. Copy the example environment file:
```cmd
copy .env.example .env
```

2. Edit the `.env` file with your actual credentials:
```env
FIREBIRD_HOST=localhost         # Firebird server host
FIREBIRD_PORT=3055              # Firebird server port
FIREBIRD_DB=C:\path\to\db.fdb   # Path to database file
FIREBIRD_USER=your_username     # Database username
FIREBIRD_PASSWORD=your_password # Database password
```
