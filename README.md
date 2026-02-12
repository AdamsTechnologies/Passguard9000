# PassGuard

PassGuard is a desktop password manager built with Python and `ttkbootstrap`.
It stores credentials in an encrypted local database and provides a GUI for creating, updating, viewing, and deleting password records.

## Highlights

- Local-first vault: encrypted database file (`datastore.db`) stored on disk.
- Strong cryptography: Argon2id key derivation + AES-GCM authenticated encryption.
- Simple desktop UX: login dialog, password list/detail views, generator, and settings.
- Runtime configurability: theme, idle timeout, and list formatting are persisted.
- Pluggable storage shape: backend abstractions isolate business logic from database specifics.

## Project Layout

```text
passguard/
  main.py                    # app entry point
  passguard_app.py           # top-level window and login/session flow
  frontend/                  # UI pages/components
  backend/
    abstracts/abstract_methods.py        # storage and encryption interfaces
    controllers/
      password_manager.py                # domain logic for password records
      database_controller.py             # SQLite-backed storage controller
    databaseManager/
      sql.py                             # low-level SQLite wrapper
      sqlite_encrypto.py                 # encrypted DB context manager
    devsec/                             # crypto helpers (key derivation, encryption)
  settings_manager.py        # persisted app settings
```

## Requirements

- Python 3.13 (recommended to match existing virtual env and bytecode)
- Windows, macOS, or Linux with Tk support
- Dependencies:
  - `cryptography==44.0.0`
  - `ttkbootstrap==1.10.1`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

From repository root:

```bash
python -m passguard.main
```

or, after package install:

```bash
passguard
```

## How Security Works (Current Implementation)

1. User credentials are entered in the login dialog.
2. Inputs are deterministically hashed (`SHA-256`) before app-side handling.
3. A 256-bit key is derived using Argon2id (`passguard/backend/devsec/key_generator.py`).
4. The vault database file is decrypted into memory for active use.
5. On app close/logout, the in-memory DB is encrypted and written back to disk.

Notes:

- Vault encryption uses AES-GCM (`passguard/backend/devsec/encrypto.py`).
- Salt is persisted via app settings (`app_settings.db`) and reused for key derivation.

## Storage Abstraction and DB Flexibility

The project is intentionally structured so domain logic does not depend directly on SQLite details.

Core pieces:

- `BaseInterface` in `passguard/backend/abstracts/abstract_methods.py` defines storage operations (`set_item`, `get_item`, `get_record`, `get_all_items`, `remove`, etc.).
- `PasswordStorageInterface` and `KeyStorageInterface` provide schema + upsert-key contracts and delegate operations to a controller.
- `PasswordController` (`passguard/backend/controllers/password_manager.py`) depends on these interfaces, not raw SQL.
- `SQLiteController` is one concrete implementation that satisfies this contract.

### Why this matters

You can replace SQLite with another backend (for example PostgreSQL, SQL Server, or a service API adapter) by providing a controller that exposes the same operation surface used by the storage interfaces.

In practical terms, migration is mostly about implementing the controller methods expected by `BaseInterface` consumers:

- `create_if_not_exists`
- `set_item`
- `get_item`
- `get_record`
- `get_all_items`
- `remove`
- `execute_operation`

Because the UI and `PasswordController` work through these abstractions, most app logic can remain unchanged while swapping storage backends.

## Settings

Settings are stored in `app_settings.db` and managed through `SettingsManager`.
Current settings include:

- `theme`
- `idle_timeout`
- `passlist_case`
- registration/user metadata (`r`, `u`, `s`)

## Packaging

This repo includes:

- `setup.py` for Python package installation
- `passguard.spec` and `passguard.iss` for executable/installer workflows

## License

See the license files in repository root:

- `LICENSE.PASSGUARD`
- `LICENSE.APACHE`
- `LICENSE.CRYPTOGRAPHY`
- `LICENSE.TTKBOOTSTRAP`
