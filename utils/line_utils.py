# --------------------------------------------------------------------------- #
#                                   Import                                    #
# --------------------------------------------------------------------------- #
import requests

# --------------------------------------------------------------------------- #
#                               Define functions                              #
# --------------------------------------------------------------------------- #
def send_line_message(message):
    token = "your_line_token"
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + token
    }
    response = requests.post(url, headers=headers, data={"message": message})
    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print("Failed to send message. Status code:", response.status_code)


if __name__ == '__main__':
    pass