from werkzeug.security import generate_password_hash
import pymysql

def hash_password(password):
    return generate_password_hash(password)

def update_user_password(username, new_password):
    # Database connection
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='687819990505',
        database='lost_and_found'
    )
    
    try:
        with conn.cursor() as cursor:
            # Hash the new password
            hashed_password = hash_password(new_password)
            
            # Update the password in the database
            sql = "UPDATE user SET password_hash = %s WHERE username = %s"
            cursor.execute(sql, (hashed_password, username))
            
            # Commit the changes
            conn.commit()
            print(f"Password updated successfully for user: {username}")
            
    except Exception as e:
        print(f"Error updating password: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    username = input("Enter username: ")
    new_password = input("Enter new password: ")
    update_user_password(username, new_password) 