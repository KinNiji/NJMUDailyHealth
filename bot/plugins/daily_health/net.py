import os
import platform
import time
import json
import asyncio
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class DailyHealthException(Exception):
    pass


class Core:
    def __init__(self, user_id, password, form_content):
        sysstr = platform.system()
        driver_path = os.getcwd() + '/plugins/daily_health/lib/'
        if sysstr == 'Windows':
            driver_path = driver_path + 'chromedriver.exe'
        elif sysstr == 'Linux':
            driver_path = driver_path + 'chromedriver'
        else:
            driver_path = driver_path + 'chromedriver_mac64'
        service = Service(driver_path)
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(5)
        self.url = {
            'e-hall': 'http://ehall.njmu.edu.cn/new/index.html'
        }
        self.user_id = user_id
        self.password = password
        self.form_content = form_content

    async def quit(self):
        self.driver.quit()

    async def close(self):
        self.driver.close()

    async def switch_window(self, title):
        time.sleep(1)
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            if title in self.driver.title:
                return
        raise DailyHealthException(f'window not found: {title}')

    async def web_actions(self):
        self.driver.maximize_window()

        # 登录
        self.driver.get(self.url['e-hall'])
        self.driver.find_element(By.CSS_SELECTOR, '#ampHasNoLogin > span.amp-no-login-en').click()
        self.driver.find_element(By.CSS_SELECTOR, '#username').send_keys(self.user_id)
        self.driver.find_element(By.CSS_SELECTOR, '#password').send_keys(self.password)
        self.driver.find_element(By.CSS_SELECTOR, '#casLoginForm > p:nth-child(5) > button').click()

        # e-hall
        await self.switch_window('南京医科大学网上办事服务大厅')
        favourite = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, '#ampPersonalAsideLeftMini > div > div:nth-child(1)')))
        favourite.click()

        app_entry = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, 'div.amp-app-single:nth-child(1)')))
        app_entry.click()

        app_entry_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, '#ampDetailEnter')))
        app_entry_button.click()

        # 打卡
        await self.switch_window('健康信息每日打卡')
        add = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, 'body > main > article > section > div.bh-mb-16 > div.bh-btn.bh-btn-primary')))
        add.click()

        try:
            prompt = self.driver.find_element(
                By.CSS_SELECTOR, 'div.bh-modal > div.bh-pop.bh-card.bh-card-lv4.bh-dialog-con > div.bh-dialog-center'
                                 ' > div.bh-dialog-content > div')
            logger.warning(prompt.text)
            return prompt.text
        except TimeoutException:
            commitment_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, '#buttons > button.bh-btn.bh-btn-primary.bh-pull-right')))
            commitment_button.click()

            form_list = self.driver.find_elements(
                By.CSS_SELECTOR, '#emapForm > div > div:nth-child(3) > div.bh-form-block.bh-mb-36'
                                 ' > div.form-validate-block')
            for label, info in self.form_content.items():
                await self.form_select_process(form_list, label, info)

            save = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, '#save')))
            save.click()

            confirm = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, 'div.bh-modal > div.bh-pop.bh-card.bh-card-lv4.bh-dialog-con > div.bh-dialog-center'
                                 ' > div.bh-dialog-btnContainerBox'
                                 ' > a.bh-dialog-btn.bh-bg-primary.bh-color-primary-5')))
            confirm.click()
            logger.warning('打卡成功！')
            return '打卡成功！'

    async def form_select_process(self, form_list, label, info):
        default = bool(info['default'])
        option = info['option']
        form_item = None
        if not default:
            for the_form_item in form_list:
                the_label = the_form_item.find_element(By.CSS_SELECTOR, 'div.bh-form-group.bh-required > label')
                if the_label.text == label:
                    form_item = the_form_item
            if form_item is None:
                raise DailyHealthException(f'label not found: {label}')
            else:
                select = form_item.find_element(
                    By.CSS_SELECTOR, 'div.bh-form-group.bh-required > div.bh-ph-8.bh-form-readonly-input'
                                     ' > div.jqx-widget.jqx-dropdownlist-state-normal.jqx-rc-all.jqx-fill-state-normal')
                dropdown_id = select.get_attribute('aria-owns')

                show_dropdown = WebDriverWait(select, 5).until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, 'div > div > div.jqx-dropdownlist-content.jqx-disableselect')))
                show_dropdown.click()

                select_dropdown = self.driver.find_element(By.CSS_SELECTOR, f'#{dropdown_id}')
                select_filter = WebDriverWait(select_dropdown, 5).until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, 'input.jqx-widget.jqx-listbox-filter-input.jqx-input.jqx-rc-all')))

                if type(option) is str:
                    select_filter.send_keys(option)
                    time.sleep(1)
                    select_option = WebDriverWait(select_dropdown, 5).until(EC.element_to_be_clickable((
                        By.CSS_SELECTOR, 'span.jqx-listitem-state-normal.jqx-item.jqx-rc-all')))
                    logger.warning(f'success: {label} -> {select_option.text}')
                    if select_option.text == option:
                        select_option.click()
                    else:
                        raise DailyHealthException(f'option not found: {label} -> {option}')
                elif type(option) is list:
                    for opt in option:
                        select_filter.clear()
                        select_filter.send_keys(opt)
                        time.sleep(1)
                        select_option = WebDriverWait(select_dropdown, 5).until(EC.element_to_be_clickable((
                            By.CSS_SELECTOR, 'span.jqx-listitem-state-normal.jqx-item.jqx-rc-all')))
                        logger.warning(f'success: {label} -> {select_option.text}')
                        if select_option.text == opt:
                            select_option.click()
                        else:
                            raise DailyHealthException(f'option not found: {label} -> {option} -> {opt}')
                else:
                    raise DailyHealthException(f'option type invalid: {label} -> {option} -> {type(option)}')


class DailyHealth:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.user_id = config['userId']
        self.qq_id = config['qqId']
        self.core = Core(self.user_id, config['password'], config['form_content'])


if __name__ == '__main__':
    daily_health = DailyHealth('config/config.json')
    asyncio.run(daily_health.core.web_actions())
