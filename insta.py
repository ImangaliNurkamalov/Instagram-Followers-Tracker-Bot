from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import psycopg2
from time import sleep

connection = psycopg2.connect(database = "followers", user = "postgres", password = "1502")

def main(username):
    driver = webdriver.Chrome()
    driver.get("https://www.instagram.com/")
    sleep(2)
    driver.find_element("xpath", "//input[@name=\"username\"]")\
        .send_keys("insta_username")
    driver.find_element("xpath", "//input[@name=\"password\"]")\
        .send_keys("insta_password")
    driver.find_element("xpath", '//button[@type="submit"]')\
        .click()
    sleep(5)
    driver.get("https://www.instagram.com/instausername/")
    sleep(3)

    followers_btn = driver.find_element("xpath", '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[2]/a')
    followers_count = followers_btn.text
    followers_count = int(followers_count.split(' ')[0])
    print(f"Number of followers: {followers_count}")

    temp = int(followers_count / 12)
    sleep(4)
    followers_btn.click()
    sleep(5)

    followers_list = driver.find_element("xpath", "/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]")

    try:
        for i in range(1, temp + 1):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_list)
            sleep(2)

        with connection:
            with connection.cursor() as cursor:
                table_name = "new_followers"
                column_name = "accounts"

                check_table_query = f"SELECT to_regclass('public.{table_name}');"
                cursor.execute(check_table_query)
                result = cursor.fetchone()

                if result[0] is not None:
                    drop_table_query = f'DROP TABLE {table_name};'
                    cursor.execute(drop_table_query)
                    connection.commit()

                create_table_query = f'''
                    CREATE TABLE {table_name} (
                        {column_name} text
                    );
                '''

                cursor.execute(create_table_query)

                for i in range(1, int(followers_count + 1)):
                    tq = driver.find_element("xpath", f"/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div[{i}]/div/div/div/div[2]")
                    str1 = tq.text.split('\n')[0]
                    insert_query = f"""INSERT INTO new_followers VALUES ('{str1}');"""
                    cursor.execute(insert_query, (str(str1)))
                cursor.close()

    except Exception as er:
        print(er)
        driver.close()

def compare():
    with connection:
        table1_name = 'test'
        table2_name = 'new_followers'
        column_name = 'accounts'

        select_query1 = f"""SELECT {column_name} FROM {table1_name};"""
        select_query2 = f"""SELECT {column_name} FROM {table2_name};"""

        cur1 = connection.cursor()
        cur2 = connection.cursor()
        cur1.execute(select_query1)
        cur2.execute(select_query2)

        table1_data = set(row[0] for row in cur1.fetchall())
        table2_data = set(row[0] for row in cur2.fetchall())

        cur1.close()
        cur2.close()

        unique_to_table1 = table1_data.difference(table2_data)
        
        if unique_to_table1:
            print(f'Following accounts unfollowed you: {unique_to_table1}')
        else:
            print("Works")


if __name__ == "__main__":
    main("instausername")
    compare()