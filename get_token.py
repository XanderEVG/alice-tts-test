import requests
from urllib.parse import urlparse, parse_qs

# Это официальный client_id приложения "Яндекс Станция", который гарантированно работает
client_id = "23cabbbdc6cd418abb4b39c32c41195d"

auth_url = f"https://oauth.yandex.ru/authorize?response_type=token&client_id={client_id}"

print("=" * 70)
print("ПОЛУЧЕНИЕ ТОКЕНА (Официальный client_id Яндекс Станции)")
print("=" * 70)
print(f"\n1. Откройте эту ссылку в браузере:")
print(auth_url)
print("\n2. Войдите в свой аккаунт Яндекс.")
print("\n3. После входа вы попадете на страницу с URL вида:")
print("   https://yandex.ru/?access_token=XXXXX#...")
print("\n4. Скопируйте ВЕСЬ этот URL из адресной строки и вставьте ниже:")
print("=" * 70)

redirect_url = input("\nВставьте URL: ").strip()

try:
    if '#' in redirect_url:
        fragment = redirect_url.split('#')[1]
        params = parse_qs(fragment)
    else:
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)

    if 'access_token' in params:
        token = params['access_token'][0]
        print("\n✅ ТОКЕН УСПЕШНО ПОЛУЧЕН!")
        print(f"Скопируйте и сохраните его:\n{token}")
    else:
        print("❌ Токен не найден в URL. Убедитесь, что скопировали всю строку.")
except Exception as e:
    print(f"❌ Ошибка: {e}")