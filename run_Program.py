# import schedule
# import time
# import subprocess

# def run_script():
#     subprocess.run(["python", "E:\Web_TEST_connect_rinking_py\TrainingNodeJS\Data_NG.py"])

# schedule.every().day.at("16:04").do(run_script)

# while True:
#     schedule.run_pending()
#     time.sleep(1)


# import schedule
# import time
# import subprocess

# def run_script():
#     subprocess.run(["python", "E:\Web_TEST_connect_rinking_py\TrainingNodeJS\Data_NG.py"])

# # Schedule the script to run every 5 minutes
# schedule.every(3).minutes.do(run_script)

# while True:
#     schedule.run_pending()
#     time.sleep(1)

import schedule
import time
import subprocess
from plyer import notification

def send_notification():
    notification.notify(
        title='Script Completed',
        message='The script has completed successfully!',
        app_icon=None,  # e.g. 'C:\\icon_32x32.ico'
        timeout=10,  # seconds
    )

def run_script():
    subprocess.run(["python", "E:\Web_TEST_connect_rinking_py\TrainingNodeJS\Data_NG.py"])
    send_notification()

# Schedule the script to run every 3 minutes
schedule.every(3).minutes.do(run_script)

while True:
    schedule.run_pending()
    time.sleep(1)
