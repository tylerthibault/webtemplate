"""
Database seed data for development and testing.

Provides sample data for users and contact messages.
"""

from datetime import datetime, timedelta
from src import db
from src.models.user import User
from src.models.contact_message import ContactMessage
from src.logic.auth_service import AuthService


def seed_users():
    """
    Create sample users for development and testing.

    Returns:
        list: Created user instances
    """
    users_data = [
        {
            "email": "admin@example.com",
            "password": "Admin123",
            "full_name": "Admin User",
        },
        {
            "email": "john.doe@example.com",
            "password": "JohnDoe123",
            "full_name": "John Doe",
        },
        {
            "email": "jane.smith@example.com",
            "password": "JaneSmith123",
            "full_name": "Jane Smith",
        },
        {
            "email": "test.user@example.com",
            "password": "TestUser123",
            "full_name": "Test User",
        },
    ]

    created_users = []

    for user_data in users_data:
        # Check if user already exists
        if not User.email_exists(user_data["email"]):
            result = AuthService.register_user(
                email=user_data["email"],
                password=user_data["password"],
                full_name=user_data["full_name"],
            )
            if result["success"]:
                user = User.find_by_email(user_data["email"])
                created_users.append(user)
                print(f"Created user: {user_data['email']}")
            else:
                print(
                    f"Failed to create user {user_data['email']}: {result.get('errors')}"
                )
        else:
            print(f"User {user_data['email']} already exists")

    return created_users


def seed_contact_messages():
    """
    Create sample contact messages for development and testing.

    Returns:
        list: Created contact message instances
    """
    messages_data = [
        {
            "name": "Alice Johnson",
            "email": "alice.johnson@example.com",
            "subject": "Inquiry about web design services",
            "message": "Hello! I am interested in your web design services for my startup. Could you provide more information about your rates and timeline?",
        },
        {
            "name": "Bob Williams",
            "email": "bob.williams@example.com",
            "subject": "Question about portfolio piece",
            "message": 'I really liked your portfolio piece "Modern E-commerce Platform". What technologies did you use to build it?',
        },
        {
            "name": "Carol Martinez",
            "email": "carol.martinez@example.com",
            "subject": "Collaboration opportunity",
            "message": "We have an exciting project coming up and would love to collaborate with you. Are you available for freelance work in the next quarter?",
        },
        {
            "name": "David Chen",
            "email": "david.chen@example.com",
            "subject": "Technical question",
            "message": 'I saw your blog post about Flask authentication. Could you explain more about the "coat hanger" session management pattern you mentioned?',
        },
        {
            "name": "Emma Davis",
            "email": "emma.davis@example.com",
            "subject": "Speaking engagement",
            "message": "We are organizing a tech conference and would like to invite you as a speaker. Would you be interested in presenting about modern web development?",
        },
    ]

    created_messages = []

    for i, msg_data in enumerate(messages_data):
        # Create message with staggered timestamps (recent to old)
        submitted_time = datetime.utcnow() - timedelta(days=i, hours=i * 2)

        contact_message = ContactMessage(
            name=msg_data["name"],
            email=msg_data["email"],
            subject=msg_data["subject"],
            message=msg_data["message"],
            submitted_at=submitted_time,
            confirmation_email_sent=False,
            admin_notification_sent=False,
        )

        contact_message.save()
        created_messages.append(contact_message)
        print(f"Created contact message from: {msg_data['name']}")

    return created_messages


def seed_database():
    """
    Seed the database with all sample data.

    Usage:
        flask seed-db
    """
    print("\n=== Seeding Database ===\n")

    # Seed users
    print("Seeding users...")
    users = seed_users()
    print(f"Created {len(users)} new users\n")

    # Seed contact messages
    print("Seeding contact messages...")
    messages = seed_contact_messages()
    print(f"Created {len(messages)} new contact messages\n")

    print("=== Database seeding complete! ===\n")

    return {"users": users, "messages": messages}


def clear_database():
    """
    Clear all data from database (keep tables).

    WARNING: This will delete all data!
    """
    print("\n=== Clearing Database ===\n")

    # Delete all contact messages
    num_messages = ContactMessage.query.delete()
    print(f"Deleted {num_messages} contact messages")

    # Delete all users (and their coat hanger sessions via cascade)
    num_users = User.query.delete()
    print(f"Deleted {num_users} users")

    db.session.commit()
    print("\n=== Database cleared! ===\n")
