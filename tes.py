querys = ['pemilu2024', 'pemilu', 'Masa Tenang', 'Bawaslu', 'AyoSiapSiapNyoblos', 'Nyoblos']

for i in querys:
    try:
        print(f"===== search tweets: {i} ===")
        # client.search_tweets(query=search_query)
    except Exception as e:
        pass
        # traceback.print_exc()