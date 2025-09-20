import asyncpg


class DatabaseConnection:
    def __init__(self):
        pass
    
    async def connect():
        pool = await asyncpg.create_pool(
            user="simon",
            password="example",
            database="PeopleDb",
            host="127.0.0.1",
            port=5432,
        )
