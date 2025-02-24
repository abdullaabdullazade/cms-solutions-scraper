import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os, time
from webdriver_manager.chrome import ChromeDriverManager

path_ = os.path.join(os.getcwd(), "submissions")

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")  # eger brauzer gui gormek istesen sil getsin!!!
options.add_experimental_option(
    "prefs",
    {
        "download.default_directory": path_,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": False,
    },
)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
df = pd.read_excel("file.xlsx")
students_data = df[["ad", "soyad", "ataadi", "sinif", "login", "şifrə"]]
string_data = list(students_data.to_string(index=False).split("\n"))
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


if not os.path.exists(path_):
    os.makedirs(path_)

def waiting_for_downloading_file(path_, time=4):
    end_time = time.time() + time
    while time.time() < end_time:
        files = [f for f in os.listdir(path_) if not f.endswith(".crdownload")]
        if files:
            last_file = max(
                [os.path.join(path_, f) for f in files], key=os.path.getctime
            )
            return last_file
        time.sleep(1)
    return None


for student in students_data:
    _class = student["sinif"]
    link_ = (
        "RIO2025_Semifinal_Seniors"
        if _class in [10, 11]
        else "RIO2025_Semifinal_Juniors"
    )

    driver.get(f"https://algo.az/{link_}")
    driver.find_element(By.ID, "username").send_keys(student["login"])
    driver.find_element(By.ID, "password").send_keys(student["şifrə"])
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    for task_num in range(1, 5):
        try:
            char_ = "S" if _class in [10, 11] else "J"
            driver.get(
                f"https://algo.az/{link_}/tasks/RIO2025_Semifinal_{char_}{task_num}/submissions"
            )
            tr_elements = driver.find_elements(By.XPATH, "//tbody/tr[@data-submission]")
            files = driver.find_elements(By.CLASS_NAME, "files")[2:]
            for j in range(len(tr_elements)):
                data_submission_value = tr_elements[j].get_attribute("data-submission")
                point = tr_elements[j].text.split()[6].replace(",", ".")
                if int(float(point)) == 0:
                    continue
                file_url = files[j].find_element(By.TAG_NAME, "a").get_attribute("href")
                driver.get(file_url)
                time.sleep(2)
                file_path = file_url.split("/")[-1]
                new_filename = f"{student['ad']}_{student['soyad']}_{student['ataadi']}_{_class}_{data_submission_value}_{point}BAL_{file_path}"
                downloaded_file_path = waiting_for_downloading_file(path_, timeout=3)
                if downloaded_file_path:
                    try:
                        os.rename(
                            downloaded_file_path, os.path.join(path_, new_filename)
                        )
                        print(f"File has saved: {new_filename}")
                    except Exception as e:
                        print("Fucking rename error:", e)
                else:
                    print("Error file was not downloaded")

        except Exception as e:
            print("Errorrrr", e)

    driver.delete_all_cookies()
    time.sleep(2)

driver.quit()
