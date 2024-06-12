import json
import aiohttp

from sanic import Sanic, response
from sanic.request import Request

import firebase_admin
from firebase_admin import credentials, auth, firestore_async

import prompts

app = Sanic("ChatApp")
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore_async.client()


@app.middleware('request')
async def authenticate_request(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return response.json({'message': 'Authorization header missing or malformed'}, status=401)

    token = auth_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        request.ctx.user = decoded_token
    except Exception as e:
        return response.json({'message': 'Invalid or expired token', 'error': str(e)}, status=401)


async def get_user_info(doc_id):
    try:
        user_ref = db.collection('users').document(doc_id)
        doc = await user_ref.get()

        if doc.exists:
            return doc.to_dict()
    except Exception as e:
        pass

    return None


@app.route('/v1/chat', methods=['POST'])
async def chat(request: Request):
    user = request.ctx.user
    uid = user['uid']

    user_prompt = request.body.decode()

    data = await get_user_info(uid)
    if data is None:
        return response.json({"status": "bad"})

    expenses = data.get("spendings") if data.get("spendings") else "Not provided" 
    budget = data.get("budget") if data.get("budget") else "Not provided"
    country = data.get("country") if data.get("country") else "US"

    _response = None
    async with aiohttp.ClientSession() as session:
        data = {
            "model": "llama3",
            "stream": False,
            "prompt": prompts.default_prompt.format(
                expenses,
                budget,
                country,
                user_prompt
            )
        }
        async with session.post('http://localhost:11434/api/generate', data=json.dumps(data).encode()) as resp:
            _response = json.loads(await resp.text())

    return response.json({
        'message': _response.get('response')
    })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
