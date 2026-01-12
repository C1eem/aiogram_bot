import aiohttp
import os
from dotenv import load_dotenv



class OpenRouterAPI:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("AI_TOKEN")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    async def response(self, question, model="xiaomi/mimo-v2-flash:free"):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "My aiohttp app",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You're a helpful assistant, so answer in detail but without unnecessary information."},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=headers, json=payload) as response:
                response_text = await response.text()
                print(f"🔍 Ответ API: {response_text}")
                try:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                except KeyError:
                    print(f"❌ Нет поля 'choices'. Весь ответ: {response_text}")
                    return "Ошибка API: неверный формат ответа"
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
                    return "Ошибка при обработке ответа"

