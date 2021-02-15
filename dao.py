import sqlite3
import traceback
import sys
from models import Person, Queue
from random import randint
import random

class DBdao(object):
    """ Інтерфейс для доступу до бази даних """
    db_name = 'database.db'
    @staticmethod
    def get_connection():
        return sqlite3.connect(DBdao.db_name)

    @staticmethod
    def _add_person(person):
        try:
            conn = DBdao.get_connection()
            c = conn.cursor()
            attr = (person.id, person.first_name, person.last_name)
            c.execute("INSERT INTO person VALUES (?, ?, ?)", attr)
            conn.commit()
        except Exception as ignored:
            print('Person not added')
        finally:
            conn.close()


    @staticmethod
    def _add_queue(queue):
        try:
            conn = DBdao.get_connection()
            c = conn.cursor()
            attr = (queue.name, queue.img, queue.ranging)
            c.execute("INSERT INTO queue (name, img, range) VALUES (?, ?, ?)", attr)
            conn.commit()
            c.execute("SELECT MAX(qid) FROM queue")
            qid = c.fetchone()[0]
            queue.id = qid
            conn.close()
            return True
        except Exception as ignored:
            print('Queue not added')
            conn.close()
            return False


    @staticmethod
    def update_queue(queue):
        try:
            conn = DBdao.get_connection()
            c = conn.cursor()
            c.execute("UPDATE queue SET img=? WHERE qid=?;", (queue.img, queue.id))
            conn.commit()
            conn.close()
            return True
        except Exception as ignored:
            traceback.print_exc(file=sys.stdout)
            print('Queue not updated')
            conn.close()
            return False


    @staticmethod
    def get_queue(query, name=False):
        try:
            conn = DBdao.get_connection()
            c = conn.cursor()
            if name:
                c.execute("""SELECT qid, img, range FROM queue WHERE name=?""", (query,))
                tmp = c.fetchone()
                return Queue(id=tmp[0], img=tmp[1], ranging=tmp[2], name=query)
            else:
                c.execute("""SELECT name, img, range FROM queue WHERE qid=?""", (query,))
                tmp = c.fetchone()
                return Queue(tmp[0], query, tmp[1], ranging=tmp[2])
        except Exception as ignored:
            traceback.print_exc(file=sys.stdout)
        finally:
            conn.close()


    @staticmethod
    def get_queues():
        try:
            conn = DBdao.get_connection()
            c = conn.cursor()
            c.execute("SELECT name, qid FROM queue GROUP BY name;")
            return c.fetchall()
        except Exception as ignored:
            pass
        finally:
            conn.close()


    @staticmethod
    def add_order(person, queue):
        random.seed()
        try:
            DBdao._add_person(person)
            conn = DBdao.get_connection()
            c = conn.cursor()
            no = randint(0, queue.ranging)
            print(queue.ranging)
            attr = (queue.id, person.id, no)
            c.execute("INSERT INTO q_order (qid, pid, no) VALUES (?, ?, ?)", attr)
            conn.commit()
        except Exception as ignored:
            traceback.print_exc(file=sys.stdout)
            print('Order not added')
        finally:
            conn.close()
        

    @staticmethod
    def get_order(queue):
        try:
            conn = DBdao.get_connection()
            c = conn.cursor()
            rows_count = c.execute("""SELECT no, p.pid, first_name, last_name
                FROM q_order o INNER JOIN person p ON o.pid = p.pid
                WHERE o.qid=?
                ORDER BY 3""", (queue.id,))
            return c.fetchall()
        except Exception as ignored:
            pass
        finally:
            conn.close()


    @staticmethod
    def get_queue_count():
        try:
            conn = DBdao.get_connection()
            c = conn.cursor()
            c.execute("""SELECT COUNT(*) FROM queue;""")
            return c.fetchone()[0]
        except Exception as ignored:
            pass
        finally:
            conn.close()
        
