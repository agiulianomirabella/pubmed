from selenium import webdriver
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

wait_time = 10

#login xpaths:
user_xpath = '//*[@id="uname"]'
password_xpath = '//*[@id="upasswd"]'
login_button_xpath = '//*[@id="signinBtn"]/span/span'

#more xpaths:
search_text_xpath = '//*[@id="term"]'
search_button_xpath = '//*[@id="search"]'


class PubMedBot():
    def __init__(self):
        self.driver = webdriver.Chrome('C:/pubmed_bot/chromedriver')
        self.driver.minimize_window()
        self.wait = WebDriverWait(self.driver, wait_time)

    # generic functions:
    def selectElementByXPath(self, path):
        out = None
        try:
            out = self.driver.find_element_by_xpath(path)
        except:
            frames = self.driver.find_elements_by_tag_name('iframe')
            i = 0
            while out == None:
                self.driver.switch_to.frame(frames[i])
                try:
                    out = self.driver.find_element_by_xpath(path)
                except:
                    self.driver.switch_to.default_content()
                    i = i+1
        return out

    def typeText(self, elementXPath, text):
        self.selectElementByXPath(elementXPath).send_keys(text)

    def clickButton(self, elementXPath):
        self.selectElementByXPath(elementXPath).click()

    def getText(self, elementXPath):
        return self.selectElementByXPath(elementXPath).text

    def extractAbstract(self):
        out = ""
        try:
            e1 = self.selectElementByXPath(
                '//*[@id="maincontent"]/div/div[5]/div/div[4]/div')
            texts = [p.text for p in e1.find_elements_by_tag_name('p')]
            for t in texts:
                out = out + t
        except:
            pass
        return out

    def enter(self):
        self.driver.get('https://www.ncbi.nlm.nih.gov/pubmed')
        sleep(1)

    def typeSearch(self, search_target):
        self.typeText(search_text_xpath, search_target)
        self.clickButton(search_button_xpath)
        sleep(1)

    def filter(self, clinicalTrial=True, review=True, abstractTargetWords=[]):
        outLinks = []
        outTitles = []
        self.clickButton('//*[@id="_simsearch"]/li/ul/li[2]/a')
        if clinicalTrial:
            self.clickButton('//*[@id="_pubt"]/li/ul/li[1]/a')
        if review:
            self.clickButton('//*[@id="_pubt"]/li/ul/li[2]/a')
        papers_anchors_aux = [e.find_element_by_tag_name(
            'a') for e in self.driver.find_elements_by_class_name('rprt')]
        seen = set()
        seen_add = seen.add
        papers_anchors = [x for x in papers_anchors_aux if not (x in seen or seen_add(x))]
        papers_links = [e.get_property('href') for e in papers_anchors]
        for l in papers_links:
            self.driver.get(l)
            abstract = self.extractAbstract()
            if abstractTargetWords:
                for word in abstractTargetWords:
                    if word in abstract:
                        outLinks.append(l)
                        outTitles.append(self.getText(
                            '//*[@id="maincontent"]/div/div[5]/div/h1'))
            else:
                outLinks.append(l)
                outTitles.append(self.getText(
                    '//*[@id="maincontent"]/div/div[5]/div/h1'))

        sleep(1)
        return outTitles, outLinks

    def generateTarget(self):
        target = ''
        target_words = []
        print()
        print('First of all, please type the words you want to search: ')
        w = input('Type a search target word: ')
        while w != 'END':
            target_words.append(w)
            w = input('Type another search target word ("END" to finish): ')

        for i, w in enumerate(target_words):
            if ' ' in w:
                w = '"' + w + '"'
            if i == 0:
                target = target + w
            else:
                target = target + ' OR ' + w
        target = '(' + target + ')' + ' AND ("physical therapy" OR physiotherapy)'
        print()
        print('The search target is: ' + target)
        return target

    def generateKeywords(self):
        keywords = []
        print()
        print('Now, please type the keywords you want the abstract to contain:')
        w = input('Type a keyword: ')
        while w != 'END':
            keywords.append(w)
            w = input('Type another keyword ("END" to finish): ')
        printAux = keywords[0]
        for k in keywords[1:]:
            printAux = printAux + ', ' + str(k)
        print()
        print('The keaywords are: ' + printAux)
        return keywords

    def askClinicalAndReview(self):
        print()
        clinical = input('Do you want papers to be clinical trials? (y/n): ')
        print()
        review = input('Do you want papers to be reviews? (y/n): ')

        if clinical == "n":
            clinical = False
        else:
            clinical = True

        if review == "n":
            review = False
        else:
            review = True

        return clinical, review

    def newSearch(self):
        searchTarget = self.generateTarget()
        keywords = self.generateKeywords()
        clinical, review = self.askClinicalAndReview()
        self.enter()
        self.typeSearch(searchTarget)
        titles, links = self.filter(clinicalTrial= clinical, review= review, abstractTargetWords= keywords)
        print()
        if titles:
            print('RESULTS:')
            print()
            for i, t in enumerate(titles):
                print('Number: ' + str(i+1))
                print('Title: ' + str(t))
                print('Link: ' + str(links[i]))
                print()

            self.driver.minimize_window()
            self.driver.maximize_window()
            for i, l in enumerate(links):
                self.driver.execute_script("window.open('','_blank');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(l)
                if i == 4 or i==len(links)-1:
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self.driver.close()
                    break
        else:
            print('NO RESULTS FOUND')
            print()

'''
    def login(self):
        self.driver.get(
            'https://www.ncbi.nlm.nih.gov/account/?back_url=https%3A%2F%2Fwww.ncbi.nlm.nih.gov%2Fpubmed')
        self.typeText(user_xpath, input('Please type your username: '))
        self.typeText(password_xpath, input('Please type your password: '))
        self.clickButton(login_button_xpath)
        sleep(1)
'''

bot = PubMedBot()
bot.newSearch()



