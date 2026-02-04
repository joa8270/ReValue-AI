from app.core.database import get_random_citizens, get_all_citizens

print('Checking get_random_citizens...')
random_citizens = get_random_citizens(sample_size=3)
if not random_citizens:
    print("No citizens found.")
for c in random_citizens:
    name = c['name']
    has_quotes = name.startswith('"') or name.startswith("'")
    print(f"Name: {name}, Has Quotes: {has_quotes}")

print('\nChecking get_all_citizens...')
all_citizens = get_all_citizens(limit=3)
if not all_citizens:
    print("No citizens found.")
for c in all_citizens:
    name = c['name']
    has_quotes = name.startswith('"') or name.startswith("'")
    print(f"Name: {name}, Has Quotes: {has_quotes}")
