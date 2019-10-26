import psycopg2
import redis
import json
from bottle import Bottle, request
import os


class Config:
    def __init__(self):
        self.db_host = os.getenv('DB_HOST', 'db')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_name = os.getenv('DB_NAME', 'emaildb')
        self.redis_host = os.getenv('REDIS_HOST', 'queue')


class Sender(Bottle):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.route('/', method='POST', callback=self.send)
        self.fila = redis.StrictRedis(host=self.config.redis_host, port=6379, db=0)
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(f'dbname={self.config.db_name} \
                                       user={self.config.db_user} \
                                       host={self.config.db_host}')

    def disconn(self, cursor=None):
        if cursor:
            cursor.close()

        self.conn.close()

    def save(self, subject, message):
        self.connect()
        cursor = self.conn.cursor()

        try:
            cursor.execute(f"INSERT INTO emails(assunto, mensagem) values('{subject}', '{message}');")
            self.conn.commit()

            msg = {'assunto': subject, 'mensagem': message}
            self.fila.rpush('sender', json.dumps(msg))

            print('Mensagem registrada')
        except Exception as e:
            self.conn.rollback()
            print(e)
        finally:
            self.disconn(cursor=cursor)

    def send(self):
        subject = request.forms.get('assunto')
        message = request.forms.get('mensagem')

        self.save(subject, message)

        return f'Mensagem enfileirada! Assunto: {subject} | Mensagem: {message}'

if __name__ == '__main__':
    sender = Sender()
    sender.run(host='0.0.0.0', port=8080, debug=True)
