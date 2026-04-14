from src.agent.database import create_db_and_tables


def main():
    create_db_and_tables()
    print("Hello from customer-support-agent!")


if __name__ == "__main__":
    main()
