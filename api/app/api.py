from flask import request, jsonify
from app import app
from base64 import b64encode
from collections import OrderedDict
from hashlib import sha256
from hmac import HMAC
from urllib.parse import urlparse, parse_qsl, urlencode
from pymongo import MongoClient
import time
import hashlib
import datetime
import requests
import jwt
import re

from keys import DB
app.config['SECRET_KEY'] = 'instaparse'

db = MongoClient(
    username=DB['login'],
    password=DB['password'],
    authSource='admin',
    authMechanism='SCRAM-SHA-1'
)['vkapp']

def is_valid_vk(*, query: dict) -> bool:
    client_secret = "lQm4PXqSMgcuxyLknNQb"
    vk_subset = OrderedDict(sorted(x for x in query.items() if x[0][:3] == "vk_"))
    hash_code = b64encode(HMAC(client_secret.encode(), urlencode(vk_subset, doseq=True).encode(), sha256).digest())
    decoded_hash_code = hash_code.decode('utf-8')[:-1].replace('+', '-').replace('/', '_')
    return query["sign"] == decoded_hash_code

def secure_vk_id(*, id: int) -> str:
    secure_id = hashlib.md5(bytes(str(id) + 'instaparse', 'utf-8')).hexdigest()
    return secure_id

def is_valid_user(*, url: str, vk_id: int, id: str) -> bool:
    return re.search(r'vk_user_id=\d+', url)[0][11:] == str(vk_id) and secure_vk_id(id=vk_id) == id

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        header = request.headers.get('Authorization')
        if header:
            token = header.split(' ')[1]

            if not token:
                return jsonify({'message' : 'Token is missing!'}), 403

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                kwargs['jwt'] = data
            except:
                return jsonify({'message' : 'Token is invalid!'}), 403
        else:
            return jsonify({'message' : 'Token is missing!'}), 403

        return f(*args, **kwargs)
    return decorated

@app.route('/auth', methods=['POST'])
def auth():
    # try:
        x = request.json

        query_params = dict(parse_qsl(urlparse(x['url']).query, keep_blank_values=True))
        status = is_valid_vk(query=query_params)

        if status:
            id = re.search(r'vk_user_id=\d+', x['url'])[0][11:]
            token = jwt.encode({
                        'user_vk_id' : id,
                        'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=1),
                        }, app.config['SECRET_KEY'])

            user = db.users.find_one({'vk_id': id}, {'_id': False})
            if not user:
                user = {
                    'id': secure_vk_id(id=id),
                    'vk_id': id,
                    'parse': [],
                    'reg_time': int(time.time())
                }
                db.users.insert_one(user)
                del user['_id']

            user['token'] = token.decode('UTF-8')
            return jsonify(user)
        else:
            return jsonify({'server': 'error'}), 400
    # except:
        # return jsonify({'server': 'error'}), 400


@app.route('/account', methods=['POST'])
def get_account():
    return jsonify({ 'server': 'true' })
