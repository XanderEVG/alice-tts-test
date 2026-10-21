import requests
import json
from urllib.parse import urlparse, parse_qs


def get_yandex_token():
    """Получение токена через OAuth flow"""

    # Client ID для Яндекс.Станции
    client_id = "23cabbbdc6cd418abb4b39c32c41195d"

    # Шаг 1: Открываем страницу авторизации
    auth_url = f"https://oauth.yandex.ru/authorize?response_type=token&client_id={client_id}"

    print("=" * 70)
    print("ПОЛУЧЕНИЕ ТОКЕНА ЯНДЕКС")
    print("=" * 70)
    print("\n1. Откройте эту ссылку в браузере:")
    print(auth_url)
    print("\n2. Войдите в свой Яндекс аккаунт (к которому привязана колонка)")
    print("\n3. После успешной авторизации вы будете перенаправлены на страницу")
    print("   с URL вида: https://yandex.ru/?token=XXXXX#...")
    print("\n4. Скопируйте ВЕСЬ URL из адресной строки браузера")
    print("=" * 70)

    redirect_url = input("\nВставьте URL из адресной строки: ").strip()

    # Парсим URL для извлечения токена
    try:
        # Токен может быть в fragment (#) или query (?)
        if '#' in redirect_url:
            fragment = redirect_url.split('#')[1]
            params = parse_qs(fragment)
        else:
            parsed = urlparse(redirect_url)
            params = parse_qs(parsed.query)

        if 'access_token' in params:
            token = params['access_token'][0]
            print("\n" + "=" * 70)
            print("ТОКЕН УСПЕШНО ПОЛУЧЕН!")
            print("=" * 70)
            print(f"\nВаш токен:\n{token}")
            print("\n⚠️  ВАЖНО: Сохраните этот токен в безопасном месте!")
            print("⚠️  Токен действует бессрочно, но его можно отозвать в настройках Яндекс ID")
            return token
        else:
            print("\n❌ Ошибка: токен не найден в URL")
            print("Убедитесь, что вы скопировали полный URL после авторизации")
            return None

    except Exception as e:
        print(f"\n❌ Ошибка при парсинге URL: {e}")
        return None


if __name__ == "__main__":
    get_yandex_token()