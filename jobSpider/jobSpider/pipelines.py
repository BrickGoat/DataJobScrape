# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd
import re

# Remove numbers
def parseCat(x):
    if checkNone(x):
        return None
    x = re.sub("\d", "", x)
    x = x.strip()
    return x


# search for state names or abreviations. Return / separated list of states
def parseLocation(x):
    df = pd.read_json("./states.json")
    states = ""
    if re.search("remote", x, re.IGNORECASE):
        states = "Remote/"
    for i in range(len(df[["state", "code"]])):
        state = df[["state", "code"]].iloc[i].state
        code = df[["state", "code"]].iloc[i].code
        if re.search(state, x, re.IGNORECASE) or re.search(f" +{code} +", x):
            states = states + f"{state}/"
    return states[:-1]


# search for language names, general tech terms. return / separated list of terms
# TODO - find json of languages
def parseRequirements(x):
    langs = [
        "python",
        "PySpark",
        "Selenium",
        "web",
        "DevOps",
        "database",
        "linux",
        "cloud",
        "Java",
        "JavaScript",
        "Machine Learning",
        "Rstudio",
        "Scala",
        "SQL",
        "Git",
        "AWS",
        "Tableau",
        "Postgresql",
        "MLOps",
    ]
    terms = ""
    for term in langs:
        if re.search(term, x, re.IGNORECASE):
            terms = terms + f"{term}/"
    return terms[:-1]

# TODO - If parsing description, also check for $
# TODO - Add zeros if digits are followed by K not only if it has three digits
def parseSalary(x):
    if checkNone(x):
        return None
    x = x.replace(",", "")
    matches = re.findall("\d+\.?\d+", x)
    min = float("inf")
    for match in matches:
        if len(match) == 3: # 110K
            match = match + "000"
        if match.isnumeric():
            salary = int(match)
            if salary > 3000 and salary < min: # avoid unrelated digits in description
                min = salary
    if min != float("inf"):
        return min
    return float('nan')


def parseSchedule(x):
    x = x.lower()
    full_pattern = "full-? *time"
    part_pattern = "part-? *time"
    fulltime = re.search(full_pattern, x)
    parttime = re.search(part_pattern, x)
    if fulltime and parttime:
        return None
    elif fulltime:
        return "full-time"
    elif parttime:
        return "part-time"
    return None


def parseType(x):
    x = x.lower()
    perm = "permanent"
    temp = "temporary|temp"
    contract = "contract"
    perm = re.search(perm, x)
    temp = re.search(temp, x)
    contract = re.search(contract, x)
    if perm:
        return "Permanant"
    elif temp:
        return "Temporary"
    elif contract:
        return "Contract"
    return None

def checkNone(val):
    return val is None

class JobspiderPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        keys = adapter.field_names()
        field_to_parse = {key:None for key in keys}
        for key in keys:
            if not checkNone(adapter[key]):
                field_to_parse[key] = adapter[key]
                continue
            field_to_parse[key] = adapter["Description"]
        adapter["Category"] = parseCat(adapter["Category"])
        adapter["Type"] = parseType(field_to_parse["Type"])
        adapter["Schedule"] = parseSchedule(field_to_parse["Schedule"])
        adapter["Location"] = parseLocation(field_to_parse["Location"])
        adapter["Salary"] = parseSalary(field_to_parse["Salary"])
        adapter["Requirements"] = parseRequirements(field_to_parse["Requirements"])
        return item
