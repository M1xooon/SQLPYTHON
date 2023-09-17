import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS client(
        id SERIAL PRIMARY KEY,
        name VARCHAR(40) NOT NULL,
        second_name VARCHAR(40) NOT NULL,
        email VARCHAR(255) NOT NULL);
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone(
        id SERIAL PRIMARY KEY,
        client_id INTEGER NOT NULL REFERENCES client(id),
        number VARCHAR(20));
        """)
        conn.commit()

def delete_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE client, phone CASCADE;
        """)
def add_phone(conn, client_id, number):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO phone(client_id, number) VALUES (%s, %s)""",(client_id,number))

def add_client(conn, name, second_name, email, number=None):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO client(name, second_name, email) VALUES (%s, %s, %s) RETURNING id;
        """,(name, second_name, email))
        client_id=cur.fetchone()[0]
        if number!=None:
            add_phone(conn, client_id, number)
        conn.commit()

def change_client(conn, client_id, name=None, second_name=None, email=None):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT * FROM client 
        WHERE id=%s
        """, (client_id,))
        information=cur.fetchone()
        if name==None:
            name=information[1]
        if second_name==None:
            second_name=information[2]
        if email==None:
            email=information[3]
        cur.execute("""
        UPDATE client
        SET name=%s, second_name=%s, email=%s
        WHERE id=%s
        """,(name, second_name, email, client_id))
        conn.commit()


def delete_phone(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phone
        WHERE client_id=%s
        """, (client_id,))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phone
        WHERE client_id=%s
        """, (client_id,))
        conn.commit()
        cur.execute("""
        DELETE FROM client
        WHERE id=%s
        """, (client_id,))
        conn.commit()

def find_client(conn, name=None, second_name=None, email=None, number=None):
    with conn.cursor() as cur:
        if name==None:
            name='%'
        else:
            name='%' + name + '%'
        if second_name==None:
            second_name='%'
        else:
            second_name='%' + second_name + '%'
        if email==None:
            email='%'
        else:
            email='%' + email + '%'
        if number==None:
            cur.execute("""
            SELECT c.id, c.name, c.second_name, c.email, p.number FROM client c
            LEFT JOIN phone p ON c.id = p.client_id
            WHERE c.name LIKE %s AND c.second_name LIKE %s AND c.email LIKE %s
            """,(name,second_name,email))
        else:
            cur.execute("""
            SELECT c.id, c.name, c.second_name, c.email, p.number FROM client c
            LEFT JOIN phone p ON c.id = p.client_id
            WHERE c.name LIKE %s AND c.second_name LIKE %s AND c.email LIKE %s AND p.number LIKE %s
            """, (name, second_name, email, number))
        return cur.fetchall()


if __name__ == '__main__':
    with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as conn:
        delete_db(conn)
        create_db(conn)
        add_client(conn, "Максим", "Минин", "msdsds@gmail.com", "799324324324")
        add_client(conn, "Константин", "Дементьев", "kfosdf0t@mail.ru", "4354664456")
        add_client(conn, "Никита", "Васильев","dfsfdsfd@outlook.com")
        add_phone(conn, 2, "79877876543")
        change_client(conn, 2, "Иван", None, "123@outlook.com")
        delete_phone(conn, 2)
        delete_client(conn, 3)
        print(find_client(conn, "Максим"))
    conn.close()