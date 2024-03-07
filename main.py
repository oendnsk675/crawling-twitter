from client import Client
import traceback

profile_path = "D:\\Lab Belajar\\Kuliah\\Skripsi\\Project\\SA\\crawling-twitter\\chrome\\userData\\Profile 1"
driver_path = "D:\\Lab Belajar\\Kuliah\\Skripsi\\Project\\SA\\crawling-twitter\\chrome\\chromedriver-win32\\chromedriver.exe"
client = Client(profile_path=profile_path, driver_path=driver_path)

querys = ['pemilu2024', 'AyoSiapSiapNyoblos']
querys = ['pemilu2024']
# querys = ['AyoSiapSiapNyoblos']

for search_query in querys:
    # search_query = input("Search your tweet: ")
    # search_query = "pemilu2024"
    if search_query.lower() == 'q' or search_query.lower() == 'quit':
        break

    try:
        print(f"===== search tweets: {search_query} ===")
        client.search_tweets(query=search_query, recent=True)
    except Exception as e:
        traceback.print_exc()
        input("Continue")

    input("Continue")
    