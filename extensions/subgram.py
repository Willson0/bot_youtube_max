import aiohttp, asyncio

from config import SUBGRAM_AD_TOKEN

async def request_op(user_id: int, lang_code: str = None):
    headers = {
        'Content-Type': 'application/json',
        'Auth': SUBGRAM_AD_TOKEN,
        'Accept': 'application/json',
    }
    data = {'UserId': user_id, 'ChatId': user_id, "Age": "18"}

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1)) as session:
            try:
                async with session.post('https://api.subgram.ru/request-op-tokenless/', headers=headers, json=data) as response:
                    if not response.ok or response.status != 200:
                        return 'ok'
                    
                    response_json = await response.json()
                    if response_json.get('status') == 'warning':
                        return response_json.get("links", [])
                    
                    return response_json.get("status")
            
            except asyncio.TimeoutError:
                return 'ok'
    
    except:
        return 'ok'
