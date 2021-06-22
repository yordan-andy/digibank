# import Library
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

import sys
import logging
import datetime

# initiate object flask
app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

# initiate object flask_restful
api = Api(app)

# initiate object flask_cors
CORS(app)

identitas = {}


class klikDBS(Resource):
    __url = 'https://internet-banking.dbs.com.sg/'

    def get(self):
        return 'REST API DBS'

    def post(self):
        username = request.form["username"]
        password = request.form["password"]
        identitas["username"] = username
        identitas["password"] = password
        self.__username = username
        self.__password = password
        response = self.login()
        return response

    def login(self):
        opts = webdriver.ChromeOptions()
        # opts.headless = False
        opts.add_argument('--headless')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--no-sandbox')
        self.__driver = webdriver.Chrome(
            executable_path=r'/app/.chromedriver/bin/chromedriver', options=opts)
        self.__driver.wait = WebDriverWait(self.__driver, 5)
        self.__driver.get(self.__url)

        username = self.__driver.wait.until(
            EC.presence_of_element_located((By.ID, "UID")))
        password = self.__driver.wait.until(
            EC.presence_of_element_located((By.ID, "PIN")))
        login = self.__driver.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Login']")))

        username.send_keys(self.__username)
        password.send_keys(self.__password)
        login.send_keys(webdriver.common.keys.Keys.SPACE)

        self.__driver.wait.until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "user_area")))
        self.__driver.wait.until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "iframe1")))

        self.__driver.wait = WebDriverWait(self.__driver, 30)
        saldo = self.__driver.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"notification\"]/ul/li[2]/div[2]/table/tbody/tr/td[2]/span"))).text

        self.__driver.switch_to.default_content()
        self.logout()
        return (jsonify({
            'code': 200,
            'success': 'true',
            'message': 'data found',
            'data': {
                'balance': '%s' % saldo,
                'timestamp': '%s' % datetime.datetime.now()
            }
        }))

    def logout(self):
        try:
            self.__driver.switch_to.frame(
                self.__driver.find_element_by_name("user_area"))
            logout = self.__driver.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href, \"LogOutUser\")]")))
            logout.send_keys(webdriver.common.keys.Keys.SPACE)
            print("Anda berhasil logout")
        except TimeoutException:
            print("Session timeout. please login again")


# setup resource
api.add_resource(klikDBS, "/api", methods=["GET", "POST"])

if __name__ == "__main__":
    app.run(debug=True, port=5005)
