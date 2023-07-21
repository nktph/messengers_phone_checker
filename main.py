import logging
import time
import random
import asyncio

from telethon import TelegramClient
from telethon import functions, types

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import NoSuchElementException, ElementNotInteractableException, UnexpectedAlertPresentException

# Для получения API_ID и API_HASH нужно перейти на https://my.telegram.org/apps, авторизоваться и создать приложение
api_id = "ВСТАВИТЬ_API_ID_КАВЫЧКИ_УБРАТЬ"
api_hash = 'ВСТАВИТЬ_API_HASH_КАВЫЧКИ_ОСТАВИТЬ'

# API-код для 2Captcha
captcha_api = "API_2Captcha"

# Лог, куда будут сохраняться результаты
# (В случае если программа завершит работу досрочно, полученные данные смотреть в Result.txt)
logging.basicConfig(level=logging.INFO, filename="Result.txt", filemode="w", format="%(message)s")

options = Options()
# Добавляем расширение в браузер
options.add_extension("Captcha-Solver.crx")

driver = webdriver.Edge(options=options)
wait = WebDriverWait(driver, 60)

# Проверка существования аккаунта Viber по номеру телефона
def check_viber(phone_number):
    print(f"Проверка Viber для номера {phone_number[:12]}")
    driver.get("https://account.viber.com/ru/create-account")

    input_field = wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="content"]/div/div/div/div/form/div/div[1]/div[2]/div/input[2]')))
    input_field.click()

    input_field.send_keys(keys.Keys.BACKSPACE)
    input_field.send_keys(keys.Keys.BACKSPACE)
    input_field.send_keys(keys.Keys.BACKSPACE)
    input_field.send_keys(keys.Keys.BACKSPACE)
    prefix_field = wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="content"]/div/div/div/div/form/div/div[1]/div[2]/div/input[1]')))

    prefix_field.send_keys(phone_number[0:3])
    input_field.send_keys(phone_number[3:12])
    input_field.send_keys(keys.Keys.ENTER)
    time.sleep(3)

    try:
        driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div/div/form/div/div[1]/div[2]/div[2]')  # Сообщение об ошибке (стр 1)
        logging.info(f"VIBER: {phone_number[:12]} не зарегистрирован")
        print(f"VIBER: {phone_number[:12]} не зарегистрирован")
        return "Не зарегистрирован"
    except NoSuchElementException:
        try:
            driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div/div/form/div/div[1]/div/input')  # Ввод кода (стр 2)
            logging.info(f"VIBER: {phone_number[:12]} зарегистрирован")
            print(f"VIBER: {phone_number[:12]} зарегистрирован")
            return "Зарегистрирован"
        except NoSuchElementException:
            logging.info(f"VIBER: Потребовалась капча для {phone_number[:12]}")
            print(f"VIBER: Потребовалась капча для {phone_number[:12]}. РЕШЕНИЕ КАПЧИ НЕ ОТЛАЖЕНО, пропускаем")
            return "Нет данных (капча)"

            # Примерный набросок решения. ВАЖНО!!! КОД НЕ БЫЛ ПРОТЕСТИРОВАН, КОНЕЧНОЕ РЕШЕНИЕ МОЖЕТ ОТЛИЧАТЬСЯ

            # Нажимаем на кнопку "Решить"
            # driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div/div/form/div/div[2]/div[2]').click()
            # Ждём
            # time.sleep(30)
            # Выводим сообщение от расширения
            # message = driver.find_element('//*[@id="content"]/div/div/div/div/form/div/div[2]/div[2]/div[2]').text
            # print(message)
            # if "ERROR_ZERO_BALANCE" in message:
                # print("Нулевой баланс, капча не может быть решена. Пропускаем проверку номера...")
            # else:
                # При успешном решении проверяем номер
                # try:
                #     valid = driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div/div/form/div/div[2]/div/button')
                #     print("зарегистрирован")
                #     logging.info(f"VIBER: {phone_number[:12]} зарегистрирован")
                # except NoSuchElementException:
                #
                #     logging.info(f"VIBER: {phone_number[:12]} не зарегистрирован")
                #     print("не зарегистрирован")


# Проверка существования аккаунта WhatsApp по номеру телефона
def check_whatsapp(phone_number):
    print(f"Проверка Whatsapp для номера {phone_number[:12]}")
    driver.get("https://web.whatsapp.com")
    btn = wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[3]/div[1]/div/div/div[3]/div/span')))
    try:
        btn.click()
    except ElementNotInteractableException:
        time.sleep(3)
        btn.click()

    input_field = wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[3]/div[1]/div/div[3]/div[2]/div/div/div/form/input')))
    input_field.click()
    input_field.send_keys(keys.Keys.BACKSPACE)
    input_field.send_keys(keys.Keys.BACKSPACE)
    input_field.send_keys(keys.Keys.BACKSPACE)
    input_field.send_keys(keys.Keys.BACKSPACE)
    input_field.send_keys(f"+{phone_number}")
    time.sleep(5)
    try:
        invalid = driver.find_element(By.XPATH, '//*[@id="app"]/div/span/div/div/div/div/div')
        logging.info(f"WHATSAPP: {phone_number[:12]} не зарегистрирован")
        print(f"WHATSAPP: {phone_number[:12]} не зарегистрирован")
        return "Не зарегистрирован"
    except NoSuchElementException:
        logging.info(f"WHATSAPP: {phone_number[:12]} зарегистрирован")
        print(f"WHATSAPP: {phone_number[:12]} зарегистрирован")
        return "Зарегистрирован"


# Проверка существования аккаунта Telegram по номеру телефона
async def check_telegram(client, phone_number):
    print(f"Проверка Telegram для номера {phone_number[:12]}")
    result = await client(functions.contacts.ImportContactsRequest(
        contacts=[types.InputPhoneContact(
            client_id=random.randrange(-2**63, 2**63),
            phone=f"+{phone_number[0:12]}",
            first_name='Some Name',
            last_name=''
        )]
    ))
    if len(result.users):
        logging.info(f"TELEGRAM: +{phone_number[0:12]} зарегистрирован")
        print(f"TELEGRAM: +{phone_number[0:12]} зарегистрирован")
        await client(functions.contacts.DeleteContactsRequest(result.users))
        return "Зарегистрирован"
    else:
        logging.info(f"TELEGRAM: +{phone_number[0:12]} не зарегистрирован")
        print(f"TELEGRAM: +{phone_number[0:12]} не зарегистрирован")
        return "Не зарегистрирован"


# Точка входа в программу
async def main():

    # Настраиваем расширение
    driver.get("chrome-extension://ifibfemgeogfhoebkmokieepdoobkbpo/options/options.html")
    # Заполняем поле API-ключа и включаем автоотправку форм
    captcha_api_field = wait.until(ec.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/table/tbody/tr[1]/td[2]/input')))
    captcha_api_field.click()
    captcha_api_field.send_keys(captcha_api)
    time.sleep(1)
    btn = wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="connect"]'))).click()
    try:
        turn_auto_send = wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="autoSubmitForms"]'))).click()
    except UnexpectedAlertPresentException as ua:
        print(f"2CAPTCHA: {ua.alert_text}")
        turn_auto_send = driver.find_element(By.XPATH, '//*[@id="autoSubmitForms"]')
        turn_auto_send.click()
        time.sleep(2)

    # Авторизуемся в телеграмм (проверка номеров осуществляется при помощи ImportContactsRequest)
    client = TelegramClient('session', api_id, api_hash)
    await client.start()

    # Считываем список номеров из txt-файла
    with open('phone_numbers.txt', 'r') as file:
        nums = file.readlines()

    viber_data = []
    whatsapp_data = []
    telegram_data = []
    for num in nums:
        viber_data.append(check_viber(phone_number=nums[0]))
        print()
        whatsapp_data.append(check_whatsapp(phone_number=num))
        print()
        telegram_data.append(await check_telegram(client=client, phone_number=num))
        logging.info("")
        print()

    print("Проверка номеров успешно завершена, записываем результат в таблицу...")

    # Записываем результат проверок в exel-таблицу
    import pandas as pd
    df = pd.DataFrame({'PhoneNumber': nums,
                       'Viber': viber_data,
                       'Whatsapp': whatsapp_data,
                       'Telegram': telegram_data})
    df.to_excel('./result.xlsx', index=False)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


# MADE BY NKTPH: https://zelenka.guru/members/6790416/
#                https://github.com/nktph
