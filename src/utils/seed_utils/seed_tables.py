


def run(table_to_seed='all'):
    """Seed database with initial data."""
    from src.utils.seed_utils.users import seed_users
    from src.utils.seed_utils.role import seed_roles

    if table_to_seed == 'roles' or table_to_seed == 'all':
        seed_roles()
    if table_to_seed == 'users' or table_to_seed == 'all':
        seed_users()
    
    print("Seeding completed.")

