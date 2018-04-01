import sqlite3 as lite
import threading
from queue import Queue
import logging

COLUMNS = "(message_id TEXT NOT NULL, id TEXT NOT NULL, id_chat TEXT NOT NULL, " \
          "username TEXT NOT NULL, date TEXT NOT NULL, text TEXT NOT NULL, " \
          "tonal FLOAT NOT NULL)"


# "(1423136, 1, 2, 'hu', 'date', 'text', 2)"
def tuple2str(t):
    return "({}, {}, {}. '{}', '{}', '{}', {})".format(t[0], t[1], t[2], t[3], t[4], t[5], t[6])


class DB:
    def __init__(self, filename):
        self.tablename = filename.split('.')[0]
        try:
            self.table = lite.connect(filename)
            self.create_table(self.tablename, COLUMNS)
            self.table.commit()
            self.table.close()
        except:
            pass

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

    def create_table(self, tablename, columns):
        c = self.table.cursor()
        create = "CREATE TABLE {} {}".format(tablename, columns)
        c.execute(create)

    def drop_table(self):
        c = self.table.cursor()
        command = "DROP TABLE {}".format(self.tablename)
        c.execute(command)

    def total_tonal(self):
        c = self.table.cursor()
        command = "SELECT sum(tonal), count(tonal) FROM {}".format(self.tablename)
        return c.execute(command)

    def user_tonal(self, usernname):
        c = self.table.cursor()
        command = "SELECT sum(tonal), count(tonal) FROM {} WHERE username='{}'".format(self.tablename, usernname)
        return c.execute(command)

    def users_tonality(self):
        c = self.table.cursor()
        command = "SELECT username, sum(tonal), count(tonal) FROM {} GROUP BY username".format(self.tablename)
        return c.execute(command)


class DBThread(threading.Thread):
    def __init__(self, work_queue, filename, bot):
        threading.Thread.__init__(self)
        self.bot = bot
        self.work_queue = work_queue
        self.filename = filename

    def run(self):
        self.db = DB(self.filename)
        while True:
            if not self.work_queue.empty():
                (command, request) = self.work_queue.get()
                self.execute(command, request)

    def get_stat(self, message):
        db = DB(self.filename)
        user = ([u for u in db.user_tonal(message.text)])[0]
        if user[0] is None:
            self.bot.send_message(message.chat.id, "Такого пользователя нет в данном чате")
            return
        if not user[1] == 0:
            tonal = user[0] / user[1]
        else:
            tonal = 0.5
        self.bot.send_message(message.chat.id, "@{} - {}".format(message.text, tonal))
        db.close()

    def execute(self, command, body):
        if command == "insert":
            self.db.insert(body)
        if command == "delete":
            self.db.delete(body)
        if command == "total_tonal":
            stat = ([i for i in self.db.total_tonal()])[0]
            if not stat[1] == 0:
                tonal = stat[0] / stat[1]
            else:
                tonal = 0.5
            self.bot.send_message(body, "Total tonality = {}".format(tonal))
        if command == 'user_tonality':
            self.bot.send_message(body.chat.id, "Put username:")
            self.bot.register_next_step_handler(body, self.get_stat)
        if command == 'users_tonality':
            str = "Статистика по пользователям:\n"
            users = [u for u in self.db.users_tonality()]
            users_tonal = []
            for user in users:
                if not user[2] == 0:
                    tonal = user[1] / user[2]
                else:
                    tonal = 0.5
                users_tonal.append((user[0], tonal,))
            for (i, user) in zip(range(1, len(users) + 1), sorted(users_tonal, key=lambda x: x[1], reverse=True)):
                str = "{}{} - @{}  {}\n".format(str, i, user[0], user[1])
            self.bot.send_message(body.chat.id, str)
        if command == "stop":
            pass
        if command == 'fatality':
            self.db.drop_table()
            self.db.create_table(self.db.tablename, COLUMNS)

        self.db.commit()
