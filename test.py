import shelve
from accounts.PWID import PWID
from accounts.Caretaker import Caretaker

ADMIN_SHELVE_NAME = 'admin_accounts.db'  # adjust to your actual file name

with shelve.open(ADMIN_SHELVE_NAME, writeback=True) as db:
    # Clear existing data (optional for fresh start)

    # Add multiple PWIDs
    for i in range(1, 4):  # creates 3 PWIDs
        username = f"pwid{i}"
        db[username] = PWID(username, f"{username}@example.com", "password123", job='Teacher')

    # Add multiple Caretakers
    for i in range(1, 3):  # creates 2 Caretakers
        username = f"caretaker{i}"
        db[username] = Caretaker(username, f"{username}@example.com", "password123", job="Nurse")

    print(f"Created {len(db)} test users")

with shelve.open(ADMIN_SHELVE_NAME) as db:
    for key, user in db.items():
        print(key, user.get_user_type())
