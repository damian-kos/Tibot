import requests
from bs4 import BeautifulSoup
import re
import json


class Character():

    def __init__(self, name):
        self.character = self.character(name)
        self.char_name = self.character.get("Name:")
        self.char_world = self.character.get("World:")
        self.char_voc = self.character.get("Vocation:")

    @staticmethod
    def response_from_site(suffix):
        response = requests.get(f"https://www.tibia.com/community/?{suffix}")
        response_text = response.text
        soup = BeautifulSoup(response_text, "html.parser")
        return soup

    # Character info
    def char_suffix(self, character_name):
        suffix = f"name={character_name}"
        ready_soup = self.response_from_site(suffix)
        return ready_soup

    # World info
    def world_suffix(self, world_name):
        suffix = f"subtopic=worlds&world={world_name}"
        ready_soup = self.response_from_site(suffix)
        return ready_soup

    # World's highscore info
    def high_score_suffix(self, links):
        suffix = links
        ready_soup = self.response_from_site(suffix)
        return ready_soup

    def character(self, name):
        soup = self.char_suffix(name)
        info = soup.find_all(class_="TableContent")
        character_info = self.label_format(info)
        return character_info

    def character_deaths(self):
        soup = self.char_suffix(self.char_name)
        info_ = soup.find_all(string=re.compile(r"^Died"))
        return info_

    def character_info_merge(self):
        message = ""
        char = self.character
        for data in char:
            message += f"{data} {char[data]}\n"
        deaths = self.character_deaths()
        for deaths in deaths:
            message += f"{deaths}\n"
        return message

    @staticmethod
    def label_format(soup):
        character_details = {}
        for label in soup:
            for label_details in label.find_all(class_="LabelV175"):
                character_details[label_details.text] = label_details.findNext().text

                if "(" in label_details.findNext().text:
                    character_details[label_details.text] = label_details.findNext().text.split(" (")[0]

                if "None " in label_details.findNext().text:
                    del character_details[label_details.text]

                if "Comment" in label_details.text or label_details.text == "":
                    del character_details[label_details.text]

                if label_details.text == "Achievement Points:":
                    a = label_details.findNext()
                    character_details[label_details.text] = a.findNext().text

        return character_details

    def who_is_online(self):
        chars = []
        soup = self.world_suffix(self.char_world)
        online = soup.find_all(class_=["Odd", "Even"])
        for i in online:
            a = i.findNext().text
            chars.append(a.replace("\xa0", " "))
        return chars

    # Definitely needs to be cleaned up. Fetches character's world highscores lists.
    def highscores_pull(self):
        world = self.char_world
        category_records = {}
        labels = ["Rank", "Name", "Vocation", "World", "Level", "Skill"]
        for category in range(1, 16):
            category_page = f"subtopic=highscores&world={world}&beprotection=-1&category={category}"
            soup = self.high_score_suffix(category_page)
            page_num = soup.select("b")
            category_char_list = []
            for page in range(1, int(page_num[-2].get_text()[-2::])):
                high_score_site = f"subtopic=highscores&world={world}&beprotection=-1&category={category}" \
                                  f"&profession=0&currentpage={page}"
                soup = self.high_score_suffix(high_score_site)
                high_score = soup.find_all(class_="LabelH")
                for i in high_score:
                    for j in i.find_next_siblings():
                        char_record = {labels[y]: [x.get_text() for x in j.contents][y] for y in range(len(labels))}
                        category_char_list.append(char_record)
                        category_records[category] = category_char_list
        for vocs in range(2, 4):
            category_voc_page = f"subtopic=highscores&world={world}&beprotection=-1&category={11}&profession={vocs}"
            soup = self.high_score_suffix(category_voc_page)
            page_voc_num = soup.select("b")
            category_char_list = []
            for voc_page in range(1, int(page_voc_num[-2].get_text()[-2::]) + 1):
                high_score_site = f"subtopic=highscores&world={world}&beprotection=-1&category={11}" \
                                  f"&profession={vocs}&currentpage={voc_page}"
                soup = self.high_score_suffix(high_score_site)
                high_score = soup.find_all(class_="LabelH")
                for i in high_score:
                    for j in i.find_next_siblings():
                        char_record = {labels[y]: [x.get_text() for x in j.contents][y] for y in range(len(labels))}
                        category_char_list.append(char_record)
                        category_records[f"11.{vocs}"] = category_char_list
        with open("highscores.json", "w") as file:
            json.dump(category_records, file)

    def is_in_highscores(self):
        with open("highscores.json", "r") as file:
            highscores = json.load(file)
            for i in highscores:
                for category in (highscores[i]):
                    if self.char_name == category["Name"]:
                        yield i, category

    def format_highscores(self):
        categories = {
            1: "Achievemets",  # points
            2: "Axe Fighting",  # level
            3: "Charm Points",  # points
            4: "Club Fighting",  # level
            5: "Distance Fighting",  # level
            6: "Experience",  # level
            7: "Fishing",  # level
            8: "Fist Fighting",  # level
            9: "Goshnar's Taint",  # points
            10: "Loyalty Points",  # points
            11: "Magic Level",  # level
            12: "Shielding",  # level
            13: "Sword Fighting",  # level
            14: "Drome Score",  # score
            15: "Boss points",  # points
            11.2: "Magic Level (knights)",  # level
            11.3: "Magic Level (paladins)"  # level
        }
        high_score_str = ""
        for i in self.is_in_highscores():
            a = (float(i[0]))
            if a == 14:
                high_score_str += f"__{categories[a]}__ | Rank **{i[1]['Rank']}** | **{i[1]['Skill']}** score\n"
            elif a == 1 or a == 3 or a == 9 or a == 10 or a == 15:
                high_score_str += f"__{categories[a]}__ | Rank **{i[1]['Rank']}** | **{i[1]['Skill']}** points\n"
            elif a == 6:
                high_score_str += f"__{categories[a]}__ | Rank **{i[1]['Rank']}** | level **{i[1]['Level']}**\n"
            else:
                high_score_str += f"__{categories[a]}__ | Rank **{i[1]['Rank']}** | level **{i[1]['Skill']}**\n"
        return high_score_str

    def is_online(self):
        if self.char_name in self.who_is_online():
            return True
        else:
            return False



