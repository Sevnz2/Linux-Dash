from instagrapi import Client
import os
from instagrapi import Client
import time

cl = Client()

cl.login("noahpitest", "cleetus223")

main_acc= "gwn.nnoah"
main_userid = cl.user_id_from_username(main_acc)

while True:
    print("Checken op nieuwe berichten..")
    threads = cl.direct_threads(amount=5)
    for thread in threads:
        print(f"Thread id: {thread.id}, Users: {[u.username for u in thread.users]}")
        for msg in thread.messages:
            sender = cl.user_info(msg.user_id).username
            print(f"bericht: {msg.txt}, Sender: {sender}")
    time.sleep(60)
