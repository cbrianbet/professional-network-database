# ENCRYPT-01: Encrypt Admin CSV Exports - Implementation Summary

## Overview
This implementation adds encryption to the admin CSV export endpoints (`/api/admin/export/members` and `/api/admin/export/users`) to enhance data security when exporting sensitive information.

## Changes Made

### 1. Dependencies
- Added `cryptography==44.0.0` to `requirements.txt`

### 2. Settings Configuration (`settings.py`)
- Added `CSV_ENCRYPTION_KEY` configuration using environment variable
- In development, automatically generates a key if not set (with warning)
- In production, requires explicit `CSV_ENCRYPTION_KEY` environment variable
- Added proper imports for `ImproperlyConfigured`

### 3. Views Implementation (`api/views.py`)
- Added imports: `io`, `cryptography.fernet.Fernet`
- Added encryption utility functions:
  - `get_encryption_cipher()`: Gets Fernet cipher from settings
  - `encrypt_csv_data()`: Encrypts bytes using Fernet symmetric encryption
  - `decrypt_csv_data()`: Decrypts bytes using Fernet symmetric encryption
- Replaced `_stream_csv` function with `_encrypt_and_stream_csv` that:
  - Generates CSV in memory using `io.StringIO`
  - Encrypts the CSV data using Fernet (AES-128 in CBC mode with HMAC)
  - Returns `HttpResponse` with encrypted data
  - Sets appropriate headers:
    - `Content-Type: application/octet-stream`
    - `Content-Disposition: attachment; filename="filename.enc"`
    - `X-Content-Encrypted: true`
    - `X-Encryption-Algorithm: Fernet (AES-128 in CBC mode with HMAC)`
- Updated `export_members` and `export_users` views to use the new encrypted function
- File extensions changed from `.csv` to `.enc` to indicate encryption

### 4. Testing (`api/tests/test_file_resources.py`)
- Added `test_encrypted_csv_exports()` method to `FileResourceTestCase`
- Tests both members and users export endpoints
- Verifies:
  - HTTP 200 status code
  - Correct content type (`application/octet-stream`)
  - Proper file extension (`.enc`)
  - Presence of security headers (`X-Content-Encrypted: true`)
  - Ability to decrypt and parse the CSV content
  - Correct data integrity after decryption

## Security Implementation Details

### Encryption Algorithm
- Uses Fernet symmetric encryption (via cryptography library)
- AES-128 in CBC mode with HMAC-SHA256 for authentication
- Provides both confidentiality and integrity protection

### Key Management
- Encryption key configurable via `CSV_ENCRYPTION_KEY` environment variable
- In development: Auto-generates key if not set (with security warning)
- In production: Requires explicit key setting (fails with ImproperlyConfigured if missing)
- Key must be a valid Fernet key (32-url-safe base64-encoded bytes)

### API Changes
- Response Content-Type changed from `text/csv` to `application/octet-stream`
- File extension changed from `.csv` to `.enc`
- Added security headers to indicate encryption:
  - `X-Content-Encrypted: true`
  - `X-Encryption-Algorithm: Fernet (AES-128 in CBC mode with HMAC)`

## Usage
Client applications need to:
1. Detect encryption via `X-Content-Encrypted: true` header
2. Decrypt the response body using the shared Fernet key
3. Process the decrypted CSV data as normal

## Testing
To run the encryption tests:
```bash
python manage.py test api.tests.test_file_resources.FileResourceTestCase.test_encrypted_csv_exports
```

To run all tests:
```bash
python manage.py test
```

## Backward Compatibility
This change breaks backward compatibility for clients expecting unencrypted CSV:
- Content type and `Content-Type`: Changed from `text/csv` to `application/octet-stream`
- File extension: Changed from `.csv` to `.enc`
- Response body: Now encrypted instead of plain CSV

Clients must be updated to handle the encryption as described in the Usage section.