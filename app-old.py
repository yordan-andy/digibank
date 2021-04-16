# import Library
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS

import time
import urllib.request
import urllib.parse
import urllib.error
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

import sys
import logging

# initiate object flask
app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

# initiate object flask_restful
api = Api(app)

# initiate object flask_cors
CORS(app)

identitas = {}


class BankApp(Resource):
    __url = 'https://internet-banking.dbs.com.sg/'

    def get(self):
        return identitas

    def post(self):
        username = request.form["username"]
        password = request.form["password"]
        identitas["username"] = username
        identitas["password"] = password
        self.__username = username
        self.__password = password
        response = self.login()
        return response
        # return {"message": "Login sukses"}

    def login(self):
        opts = webdriver.ChromeOptions()
        opts.headless = True
        self.__driver = webdriver.Chrome(
            ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install(), options=opts)
        self.__driver.wait = WebDriverWait(self.__driver, 3)

        try:
            self.__driver.get(self.__url)
            username = self.__driver.wait.until(
                EC.presence_of_element_located((By.ID, "UID")))
            password = self.__driver.wait.until(
                EC.presence_of_element_located((By.ID, "PIN")))
            login_bca = self.__driver.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[text()='Login']")))
            username.send_keys(self.__username)
            password.send_keys(self.__password)
            login_bca.send_keys(webdriver.common.keys.Keys.SPACE)

            try:
                self.__driver.switch_to.frame(
                    self.__driver.find_element_by_name("user_area"))
                self.__driver.switch_to.default_content()
                return self.cekSaldo()
            except:
                alert = self.__driver.switch_to.alert()
                # return alert.text
                return {"message": "Login gagal 1"}
                alert.accept()

        except:
            return {"message": "Login gagal 2"}

    def cekSaldo(self):
        try:
            self.__driver.switch_to.frame(
                self.__driver.find_element_by_name("user_area"))
            self.__driver.switch_to.frame(
                self.__driver.find_element_by_name("iframe1"))

            saldo = self.__driver.find_element_by_xpath(
                "//*[contains(text(), \"S$\")]").text
            self.__driver.switch_to.default_content()
            self.logout()
            return {"message": "Saldo DBS saat ini adalah %s" % saldo}
        except TimeoutException:
            return {"message": "Session timeout. please login again"}

    def logout(self):
        try:
            self.__driver.switch_to.frame(
                self.__driver.find_element_by_name("user_area"))
            logout = self.__driver.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href, \"javascript:goToState\")]")))
            logout.click()
            print("Anda berhasil logout")
        except TimeoutException:
            print("Session timeout. please login again")

    # setup resource
api.add_resource(BankApp, "/api", methods=["GET", "POST"])

if __name__ == "__main__":
    app.run(debug=True, port=5005)
