import sqlite3 as lite
import threading
from queue import Queue
import logging


# "(1423136, 1, 2, 'hu', 'date', 'text', 2)"
def tuple2str(t):
    return "({}, {}, {}. '{}', '{}', '{}', {})".format(t[0], t[1], t[2], t[3], t[4], t[5], t[6])


class DB:
    def __init__(self, filename):
        global c
        self.tablename = filename.split('.')[0]
        try:
            self.table = lite.connect(filename)
            c = self.table.cursor()
            create = "CREATE TABLE {} (message_id TEXT NOT NULL, id TEXT NOT NULL, id_chat TEXT NOT NULL, " \
                     "name TEXT NOT NULL, date TEXT NOT NULL, text TEXT NOT NULL, tonal INT NOT NULL)" \
                .format(self.tablename)
            c.execute(create)
            self.table.commit()
        except:
            pass
        finally:
            logging.info("db start")
            c.close()

    # record - строка вида (message_id, id, id_chat, name, date, text, tonal)
    def insert(self, record):
        c = self.table.cursor()
        command = "insert into {} values {}".format(self.tablename, record)
        c.execute(command)

    # record - строка вида (id, id_chat, name, date, text, tonal)
    def update(self, record):
        c = self.table.cursor()
        command = "update {} date='{}' text='{}' tonal={} where message_id={}".format(self.tablename, record[4],
                                                                                      record[5],
                                                                                      record[6], record[0])
        c.execute(command)

    def delete(self, message_id):
        c = self.table.cursor()
        command = "delete from {} where message_id={}".format(self.tablename, message_id)
        c.execute(command)

    def commit(self):
        self.table.commit()

    def close(self):
        self.table.close()

    def total_tonal(self):
        c = self.table.cursor()
        command = "SELECT tonal FROM {}".format(self.tablename)
        return c.execute(command)


class DBThread(threading.Thread):
    def __init__(self, work_queue, filename, bot):
        threading.Thread.__init__(self)
        self.bot = bot
        self.work_queue = work_queue
        logging.basicConfig(filename="sample.log", level=logging.INFO)
        self.filename = filename

    def run(self):
        self.db = DB(self.filename)
        while True:
            if not self.work_queue.empty():
                (command, request) = self.work_queue.get()
                logging.info("db start with {} {}".format(command, request))
                self.execute(command, request)

    def execute(self, command, body):
        if command == "insert":
            self.db.insert(body)
        if command == "delete":
            self.db.delete(body)
        if command == "total_tonal":
            records = []
            tonal = 0
            for str in self.db.total_tonal():
                records.append(str)
            for r in records:
                for e in r:
                    tonal += e
            self.bot.send_message(body, tonal / len(records))

            self.db.commit()
