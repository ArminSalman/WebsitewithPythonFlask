import requests
from bs4 import BeautifulSoup

def schoolList(cityCode):
    schools = []
    noneUrl = "http://www.meb.gov.tr/baglantilar/okullar/index.php?ILKODU="
    url = noneUrl + str(cityCode)

    website = requests.get(url)
    source = BeautifulSoup(website.content,"lxml")
    tr = source.find_all("tr")
    for i in tr:
        a = i.select("td > a")
        for k in a:
            j = k.text
            if len(j) == 0:
                pass
            else:
                o = j.split("-")
                if o[-1] != "\n\n":
                    schools.append(o[2])

    return schools

def findSchoolWebAdress(cityCode,schoolName):
    noneUrl = "http://www.meb.gov.tr/baglantilar/okullar/index.php?ILKODU="
    url = noneUrl + str(cityCode)

    website = requests.get(url)
    source = BeautifulSoup(website.content,"lxml")
    tr = source.find_all("tr")
    for i in tr:
        a = i.select("td > a")
        for k in a:
            j = k.text
            if len(j) == 0:
                pass
            else:
                if schoolName in j:
                    k = str(k)
                    u = k.split('"')
                    schoolWebAdress = u[1]
    return schoolWebAdress

def teacherVerifyControl(name,familyname,schoolWebAdress,branch):
    match = False
    familyname = familyname.upper()
    n = name[0].upper()
    name = n + name[1:-1] + name[-1]
    branch = branch.upper()
    url = schoolWebAdress + "/teskilat_semasi.html"

    website = requests.get(url)
    source = BeautifulSoup(website.content,"lxml")
    li = source.find_all("li")
    for i in li:
        a = i.select("a")
        for k in a:
            j = k.text
            if len(j) > 0 and j != "RSS" and j != "Site Haritası":
                j = j.replace("İ","I")
                j = j.split(" ")
                if len(j) == 2:
                    if "." in j[0]:
                        o = j[0].split(".")
                        if len(o[0]) > 2:
                            if o[0] in j[0] and familyname == j[-1]:
                                k = str(k)
                                u = k.split('"')
                                b = u[3]
                                b = b.upper()
                                if branch in b:
                                    match = True
                                    break
                        if len(o[1]) > 2:
                            if o[1] in j[0] and familyname == j[-1]:
                                k = str(k)
                                u = k.split('"')
                                b = u[3]
                                b = b.upper()
                                if branch in b:
                                    match = True
                                    break
                    else:
                        if name in j[0] and familyname == j[-1]:
                            k = str(k)
                            u = k.split('"')
                            b = u[3]
                            b = b.upper()
                            if branch in b:
                                match = True
                                break
                if len(j) > 2:
                    if len(j[0]) > 2:
                        if j[0] in name and familyname == j[-1]:
                            k = str(k)
                            u = k.split('"')
                            b = u[3]
                            b = b.upper()
                            if branch in b:
                                match = True
                                break
                    if len(j[1]) > 2:
                        if name in j[0] and familyname == j[-1]:
                            k = str(k)
                            u = k.split('"')
                            b = u[3]
                            b = b.upper()
                            if branch in b:
                                match = True
                                break


    return match
