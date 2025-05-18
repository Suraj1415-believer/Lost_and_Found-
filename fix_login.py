from werkzeug.security import generate_password_hash
import pymysql

def fix_user_login(username, password):
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='687819990505',
        database='lost_and_found'
    )
    
    try:
        with conn.cursor() as cursor:
            # Generate proper password hash
            hashed_password = generate_password_hash(password)
            
            # Update only the password_hash field
            sql = "UPDATE user SET password_hash = %s WHERE username = %s"
            cursor.execute(sql, (hashed_password, username))
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"Success! User '{username}' can now log in with the password you provided.")
            else:
                print(f"User '{username}' not found in database.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

# Example usage
username = input("Enter username that can't login: ")
password = input("Enter the password you want to use: ")
fix_user_login(username, password) 