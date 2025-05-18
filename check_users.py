import pymysql

def show_users():
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='687819990505',
        database='lost_and_found'
    )
    
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, username, email, is_admin, is_active FROM user"
            cursor.execute(sql)
            users = cursor.fetchall()
            
            print("\nAll Users in Database:")
            print("=" * 50)
            print("ID | Username | Email | Is Admin | Is Active")
            print("-" * 50)
            for user in users:
                print(f"{user[0]} | {user[1]} | {user[2]} | {user[3]} | {user[4]}")
            print("=" * 50)
            
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    show_users() 