# _*_encoding:utf-8_*_
from __future__ import division
import subprocess
from functools import reduce
import io
import sqlite3
import os
import json
from datetime import datetime,timedelta
global_job_path = os.path.dirname(os.path.abspath(__file__))

class Ability:
    def __init__(self):
        self.ips = ['10.17.41.141','10.17.41.142','10.17.41.143','10.17.41.145']
        self.apis = [
            '/richlifeApp/devapp/getdisk',
            '/richlifeApp/devapp/getDiskInfo',
            '/richlifeApp/devapp/andAlbum/openApi/queryCloudMember',
            '/richlifeApp/devapp/downloadRequest',
            '/richlifeApp/devapp/pcUploadFileRequest'
        ]
        
        currentDay = datetime.now()
        days = timedelta(days=-1)
        self.dayBefore = (currentDay + days).strftime("%Y-%m-%d")

    def runCommand(self, cmd):
        """
        :param cmd: 所执行的命令
        :return: 命令执行的结果
        """
        ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ret.stdout.read().strip()

    def saveDB(self,mergearr):
        db = DB()
        db.insert('openapi', (json.dumps(mergearr,ensure_ascii=False), self.dayBefore))
        db.close()

    def generateTrs(self):
        mergearr = []
        for ip in self.ips:
            filepath = "/data/logs/web/"+ip+"/access.log.%s"%self.dayBefore
            cmd = "./tps_request_time.sh %s" % filepath
            print(cmd)
            data = self.runCommand(cmd)
            mergearr.append((ip,data.split("\n")))
        print(mergearr)
        # 备份数据到数据库
        self.saveDB(mergearr)
        return mergearr

    def select(self,searchDate):
        """
        查询指定日期的数据
        """
        db = DB()
        rows = db.select('openapi', searchDate)
        for row in rows:
            data, date = row
            data = json.loads(data)
            print(data)
        db.close()

    def statistics(self):
        mergearr = self.generateTrs()
        number = 1
        strTrs = ""
        for index,api in enumerate(self.apis):
            strTrs += """
                        <tr><td rowspan="%s" style="border:1px solid black;">
                                        %s
                        </td></tr>
                    """ % (6, str(number))
            totalTps = reduce(lambda x,y:x+y,map(lambda x:int(x[1][index + 1]),mergearr))
            # totalTime = reduce(lambda x,y:x+y,map(lambda x:float(x[1][index + 7]),mergearr))/len(self.ips)
            strTrs += """
                        <tr><td rowspan="%s" style="border:1px solid black;">
                                        %s
                        </td></tr>
                    """ % (5, api+"<br/>"+"(总tps->%s;)"%(totalTps)) #totalTime
            for item in mergearr:
                ip,data = item
                strTrs += """
                            <tr>
                                <td style="border:1px solid black;">%s</td>
                                <td style="border:1px solid black;">%s</td>
                                <td style="border:1px solid black;">%s</td>
                            </tr>
                        """%(ip,data[index + 1],data[index + 7])
            number += 1
        if strTrs:
            # 统计总的tps
            TotalTps = reduce(lambda x,y:x+y,map(lambda x:int(x[1][0]),mergearr))
            # 总的耗时
            TotalRequestTime = reduce(lambda x,y:x+y,map(lambda x:float(x[1][6]),mergearr))/len(self.ips)
            return TotalTps,TotalRequestTime,strTrs
        return False

    def get_message(self):
        """
        读取html文件，填充格式化数据
        :return: filedata
        """
        result = self.statistics()
        if result:
            TotalTps, TotalRequestTime, strTrs = result
            with io.open('data.html', 'r', encoding='utf-8') as fl:
                filedata = fl.read()
                filedata = filedata % (self.dayBefore,TotalTps, TotalRequestTime, strTrs)
            return filedata
        return False

    def run(self):
        message = self.get_message()
        if message:
            with io.open('result.html','w',encoding='utf-8') as file:
                file.write(message)

class DB(object):
    def __init__(self, db_file=None):
        if db_file is None:
            db_file_default = os.path.join(global_job_path, 'apiData.db')
        else:
            db_file_default = db_file
        self.conn = sqlite3.connect(db_file_default)
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()
        self.create_table('openapi')

    def create_table(self, table):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS %s
                   (CONTENT TEXT  NOT NULL,
                   DATETIME TEXT NOT NULL);''' % table)

    def insert(self, table, data):
        rows = self.select('openapi',data[1])
        if rows:
            print("已经有数据...")
            return
        else:
            self.cursor.execute("INSERT INTO %s (CONTENT,DATETIME) VALUES(?,?)" % table, data)
            self.conn.commit()
            print("插入成功...")

    def select(self, table,date):
        sql="select * from {table} where DATETIME like '%{date}%'".format(table=table,date=date)
        print(sql)
        rows = self.cursor.execute(sql).fetchall()
        return rows

    def close(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    terminal = Ability()
    # 运行入口
    terminal.run()
    # 查询指定的日期是否有对应数据
    # terminal.select(terminal.dayBefore)