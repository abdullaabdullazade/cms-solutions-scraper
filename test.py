import pandas as pd

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os, shutil, time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from urllib.parse import urljoin

# options.add_argument("--headless")
# options.add_argument("--disable-gpu")
download_path = r"C:\Users\Asus Vivobook\Documents\all-cms-solutions\submissions"


proxy = "http://ezhdkibx:2jkx383c9xc9@45.159.53.148:7520"

options = Options()

options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

#45.159.53.148:7520:ezhdkibx:2jkx383c9xc9

options.add_experimental_option(
    "prefs",
    {
        #"profile.default_content_settings.popups": 0,
         "download.default_directory": download_path,
        #"download.prompt_for_download": False,
        # "download.directory_upgrade": True,
        # "safebrowsing.enabled": True,
        #"download_restrictions": 0,
    },
)

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=options)
df = pd.read_excel("file.xlsx")

df_selected = df[["ad", "soyad", "ataadi", "sinif", "login", "şifrə"]]

string_data = list(df_selected.to_string(index=False).split("\n"))

students_data = []

for i in string_data[1:]:
    i = i.split()
    try:
        students_data.append(
            {
                "ad": i[0],
                "soyad": i[1],
                "ataadi": i[2],
                "sinif": int(float(i[4])),
                "login": i[5],
                "şifrə": i[6],
            }
        )
    except:
        pass

# for i in students_data[4:]:
#students_data = [students_data[8]]
start = 61
end = 120

for i in students_data[start:end+1]:
    _class = i["sinif"]
    link_ = 'RIO2025_Semifinal_Seniors' if _class == 10 or _class == 11 else 'RIO2025_Semifinal_Juniors'
    driver.get(f"https://algo.az/{link_}")
    try:
            driver.find_element(By.ID, "username").send_keys(i["login"])
            driver.find_element(By.ID, "password").send_keys(i["şifrə"])
            driver.find_element(
                By.XPATH, "//button[@type='submit']"
            ).click()
            for __ in range(1, 5):
                driver.get(
                    f"https://algo.az/{link_}/tasks/RIO2025_Semifinal_S{__}/submissions"
                )

                # a = driver.find_element(By.XPATH,"//tbody/tr[@data-submission]").text
                # print(a)

                tr_elements = driver.find_elements(
                    By.XPATH, "//tbody/tr[@data-submission]"
                )
                files = driver.find_elements(By.CLASS_NAME, "files")[2:]
                for j in range(len(tr_elements)):
                    data_submission_value = tr_elements[j].get_attribute("data-submission")
                    point = "".join(tr_elements[j].text.split()[6])

                    file_url = files[j].find_element(By.TAG_NAME, "a").get_attribute("href")

                    driver.get(file_url)

                    file_ext = file_url.split("/")[-1]
                    #print(i)
                    #print(point,file_url,file_ext)
                    #print(f"{i['ad']}_{i['soyad']}_{i['ataadi']}_{_class}_{data_submission_value+1}_{point}_{file_ext}")
                    #time.sleep(2)
                    print(file_ext,i)
                    new_filename = f"{i['ad']}_{i['soyad']}_{i['ataadi']}_{_class}_{data_submission_value}_{point}BAL_{file_ext}"
                    list_of_files = os.listdir(download_path)
                    latest_file = max(
                        [os.path.join(download_path, f) for f in list_of_files],
                        key=os.path.getctime
                    )
                    
                    print(latest_file,new_filename)
                    new_file_path = os.path.join(download_path, new_filename)
                    os.rename(latest_file, new_file_path)
                    print(f"✅ Fayl köçürüldü: {new_file_path}")
                    
                        

    except Exception as e:
            print(f"❌ Xəta baş verdi: {str(e)}")
    driver.delete_all_cookies()
    time.sleep(5)
    