from flask import Flask, render_template
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


app = Flask(__name__)

@app.route('/')
def index():
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="password",
                                    host="db",
                                    port="5432")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = connection.cursor()
        q = 'SELECT * FROM test_data ORDER BY ID ASC'
        cursor.execute(q)   
        list_data = cursor.fetchall()

        cursor.close()
        connection.close()

    except (Exception, Error) as error:
        print("Ошибка", error)
        list_data = []
    
    return render_template('index.html', list_data=list_data)

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", debug = True)