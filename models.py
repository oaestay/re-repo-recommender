import psycopg2

from config import config


class Repository:
    def __init__(self, object):
        self.id = object["id"]
        self.name = object["name"]
        self.owner = object["owner"]["id"]
        self.owner_name = object["owner"]["login"]
        self.created_at = object["created_at"]
        self.pushed_at = object["pushed_at"]
        self.subscribers_count = object["subscribers_count"]
        self.stargazers_count = object["stargazers_count"]
        self.forks_count = object["forks_count"]

    def save_to_db(self):
        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)

            cur = conn.cursor()

            query = """
                INSERT INTO repositories(id, name, owner, owner_name, subscribers_count, stargazers_count, forks_count, created_at, pushed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, TIMESTAMP %s, TIMESTAMP %s)
                ON CONFLICT (id) DO NOTHING;
            """
            cur.execute(query, (self.id, self.name, self.owner, self.owner_name, self.subscribers_count, self.stargazers_count, self.forks_count, self.created_at, self.pushed_at))

            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error on repository:")
            print("id: ", self.id)
            print("name: ", self.name)
            print("owner: ", self.owner)
            print("owner_name: ", self.owner_name)
            raise error
        finally:
            if conn is not None:
                conn.close()


class User:
    def __init__(self, object):
        self.id = object["id"]
        self.name = object["login"]

    def save_to_db(self):
        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)

            cur = conn.cursor()

            query = """
                INSERT INTO users(id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING;
            """
            cur.execute(query, (self.id, self.name))

            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()


class Star:
    def __init__(self, user, repository, created_at):
        self.user = user
        self.repository = repository
        self.created_at = created_at

    def save_to_db(self):
        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)

            cur = conn.cursor()

            query = """SELECT COUNT(*) FROM stars WHERE repository_id = %s AND user_id = %s;"""

            cur.execute(query, (self.repository, self.user))
            result = cur.fetchone()
            if result[0] == 0:
                cur = conn.cursor()

                query = """
                    INSERT INTO stars(user_id, repository_id, created_at)
                    VALUES (%s, %s, TIMESTAMP %s)
                """
                cur.execute(query, (self.user, self.repository, self.created_at))

                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            raise error
        finally:
            if conn is not None:
                conn.close()


class Watch:
    def __init__(self, user, repository):
        self.user = user
        self.repository = repository

    def save_to_db(self):
        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)

            cur = conn.cursor()

            query = """SELECT COUNT(*) FROM subscribers WHERE repository_id = %s AND user_id = %s;"""

            cur.execute(query, (self.repository, self.user))
            result = cur.fetchone()
            if result[0] == 0:
                cur = conn.cursor()

                query = """
                    INSERT INTO subscribers(user_id, repository_id)
                    VALUES (%s, %s)
                """
                cur.execute(query, (self.user, self.repository))

                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            raise error
        finally:
            if conn is not None:
                conn.close()


class Fork():
    def __init__(self, repository, object):
        self.repository_id = repository
        self.id = object["id"]
        self.name = object["name"]
        self.owner = object["owner"]["id"]
        self.owner_name = object["owner"]["login"]
        self.created_at = object["created_at"]

    def save_to_db(self):
        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)

            cur = conn.cursor()

            query = """
                INSERT INTO forks(id, repository_id, name, owner, owner_name, created_at)
                VALUES (%s, %s, %s, %s, %s, TIMESTAMP %s)
                ON CONFLICT (id) DO NOTHING;
            """
            cur.execute(query, (self.id, self.repository_id, self.name, self.owner, self.owner_name, self.created_at))

            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            raise error
        finally:
            if conn is not None:
                conn.close()
