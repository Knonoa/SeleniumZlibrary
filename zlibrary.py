import os
import time
import argparse
from selenium import webdriver


class Zlibrary:
    def __init__(self, user, password, save_dir, driver_path):
        self.user = user
        self.password = password
        self.save_dir = save_dir
        self.driver_path = driver_path
        self.driver = webdriver.Chrome(executable_path=self.driver_path)
        self.save_check = 5

    def login(self):
        print("登录中...")

        self.driver.get("http://zh.singlelogin.me/")
        self.driver.find_element_by_xpath(
            '/html/body/table/tbody/tr[2]/td/div/div/div/div/div[1]/form/div[1]/input').clear()
        self.driver.find_element_by_xpath(
            '/html/body/table/tbody/tr[2]/td/div/div/div/div/div[1]/form/div[1]/input').send_keys(self.user)
        self.driver.find_element_by_xpath(
            '/html/body/table/tbody/tr[2]/td/div/div/div/div/div[1]/form/div[2]/input').clear()
        self.driver.find_element_by_xpath(
            '/html/body/table/tbody/tr[2]/td/div/div/div/div/div[1]/form/div[2]/input').send_keys(self.password)
        self.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/div/div/div/div/div[1]/form/button').click()

        self.driver.implicitly_wait(30)
        self.driver.switch_to.window(self.driver.window_handles[0])

    def search(self, label):
        print("搜索{}...".format(label))

        self.driver.implicitly_wait(100)
        self.driver.switch_to.window(self.driver.window_handles[0])

        self.driver.find_element_by_xpath(
            '/html/body/table/tbody/tr[2]/td/div/div/div/div[1]/form/div[1]/div/div[1]/input').clear()
        self.driver.find_element_by_xpath(
            '/html/body/table/tbody/tr[2]/td/div/div/div/div[1]/form/div[1]/div/div[1]/input').send_keys(label)
        self.driver.find_element_by_xpath(
            '/html/body/table/tbody/tr[2]/td/div/div/div/div[1]/form/div[1]/div/div[2]/div/button').click()

        self.driver.implicitly_wait(30)
        self.driver.switch_to.window(self.driver.window_handles[0])

    def get_pages(self):
        self.driver.implicitly_wait(100)
        self.driver.switch_to.window(self.driver.window_handles[0])
        pages = self.driver.find_elements_by_xpath(
            '/html/body/table/tbody/tr[2]/td/div/div/div/div[3]/table/tbody/tr[1]/td[3]/table/tbody/tr[1]/td/span/a')
        urls = [i.get_attribute('href') for i in pages]
        urls.insert(0, None)

        print("获取分页:{}".format(len(urls)))

        return urls

    def get_books(self):
        self.driver.implicitly_wait(100)
        self.driver.switch_to.window(self.driver.window_handles[-1])

        books = self.driver.find_elements_by_xpath(
            '/html/body/table/tbody/tr[2]/td/div/div/div/div[2]/div/div/table/tbody/tr/td[2]/table/tbody/tr[1]/td/h3/a')
        urls = [i.get_attribute('href') for i in books]

        print("获取该页书籍:{}".format(len(urls)))

        return urls

    def download(self):
        print("下载中...")

        self.driver.implicitly_wait(100)
        self.driver.switch_to.window(self.driver.window_handles[-1])

        self.driver.find_element_by_xpath(
            '/html/body/table/tbody/tr[2]/td/div/div/div/div[2]/div[2]/div[1]/div[1]/div/a').click()

        self.driver.implicitly_wait(100)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def detect_download(self, save_path):
        print("等待下载...")

        file_dict = {}

        while True:
            file_list = os.listdir(save_path)

            del_list = []
            for key in file_dict.keys():
                if key not in file_list:
                    del_list.append(key)

            for del_key in del_list:
                print("完成:{}".format(".".join(del_key.split('.')[:-1])))
                file_dict.pop(del_key)

            for file in file_list:
                if file.split('.')[-1] == 'crdownload':
                    if file not in file_dict.keys():
                        file_dict[file] = os.stat(os.path.join(save_path, file)).st_size
                    else:
                        if file_dict[file] == os.stat(os.path.join(save_path, file)).st_size:
                            print("{}下载中断".format(file))
                            os.remove(os.path.join(save_path, file))
                            file_dict.pop(file)
                        else:
                            file_dict[file] = os.stat(os.path.join(save_path, file)).st_size

            print("路径中共有{}文件，其中{}正在下载".format(len(file_list), len(file_dict)))
            print(file_dict.keys())
            if len(file_dict) == 0:
                print("结束等待")
                return True
            else:
                time.sleep(30)

    def run(self, labels):
        for label in labels:
            # set driver
            save_path = os.path.join(self.save_dir, label)
            os.system("mkdir -p {}".format(save_path))
            # 判断保存路径中是否存在没有下载完的文件
            for file in os.listdir(save_path):
                type = file.split('.')[-1]
                if type == 'crdownload':
                    os.remove(os.path.join(save_path, file))

            prefs = {
                'profile.default_content_settings.popups': 0,
                'download.default_directory': save_path
            }
            chromeOptions = webdriver.ChromeOptions()
            chromeOptions.add_experimental_option('prefs', prefs)
            self.driver = webdriver.Chrome(executable_path=self.driver_path, chrome_options=chromeOptions)

            # 登录网站
            self.login()
            # 根据标签搜索
            self.search(label)
            # 获取搜索结果的所有页面
            page_urls = self.get_pages()
            for page in page_urls:
                if page is not None:
                    # 在新的标签页中打开2及以后的页面
                    self.driver.execute_script(f'window.open("{page}")')

                book_urls = self.get_books()

                for i, book in enumerate(book_urls):
                    self.driver.execute_script(f'window.open("{book}")')
                    self.download()

                    if (i + 1) % self.save_check == 0:
                        self.detect_download(save_path)

                if page is not None:
                    self.driver.implicitly_wait(100)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self.driver.implicitly_wait(100)

    def __del__(self):
        self.driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', type=str)
    parser.add_argument('--pwd', type=str)
    parser.add_argument('--driver', type=str)
    parser.add_argument('--save', type=str)
    parser.add_argument('--labels', nargs='+')

    opt = parser.parse_args()

    zb = Zlibrary(opt.user, opt.pwd, opt.save, opt.driver)
    zb.run(opt.labels)
