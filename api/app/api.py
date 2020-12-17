from flask import request, jsonify
from app import app
from base64 import b64encode
from collections import OrderedDict
from hashlib import sha256
from hmac import HMAC
from urllib.parse import urlparse, parse_qsl, urlencode
from pymongo import MongoClient
from functools import wraps
import pycurl
from io import StringIO
import io
import time
import hashlib
import datetime
import requests
import jwt
import json
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
    try:
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
    except:
        return jsonify({'server': 'error'}), 400

@app.route('/parse/add', methods=['POST'])
@token_required
def parse_add(jwt):
    try:
        x = request.json

        user = db.users.find_one({'vk_id': jwt['user_vk_id']}, {'_id': False})
        if user:
            parse_item = {
                'account': x['text'],
                'data': []
            }

            user['parse'].append(parse_item);
            db.users.update_one({'vk_id': jwt['user_vk_id']}, { '$set': { 'parse': user['parse'] }})
            return jsonify(user['parse'])
        else:
            return jsonify({'server': 'error'}), 400
    except:
        return jsonify({'server': 'error'}), 400

@app.route('/parse/delete', methods=['POST'])
@token_required
def parse_delete(jwt):
    try:
        x = request.json

        user = db.users.find_one({'vk_id': jwt['user_vk_id']}, {'_id': False})
        if user:

            for i, parse_item in enumerate(user['parse']):
                if parse_item['account'] == x['text']:
                    del user['parse'][i]

            db.users.update_one({'vk_id': jwt['user_vk_id']}, { '$set': { 'parse': user['parse'] }})
            return jsonify(user['parse'])
        else:
            return jsonify({'server': 'error'}), 400
    except:
        return jsonify({'server': 'error'}), 400

@app.route('/search', methods=['POST'])
@token_required
def search(jwt):
    try:
        x = request.json

        user = db.users.find_one({'vk_id': jwt['user_vk_id']}, {'_id': False, 'parse': True})
        if user:

            items = []
            if '@' in x['text']:
                for parse_account in user['parse']:
                    if x['text'][1:] in parse_account['account']:
                        for parse_item in parse_account['data']:
                            items.append(parse_item);
            else:
                for parse_account in user['parse']:
                    for parse_item in parse_account['data']:
                        if x['text'] in parse_item['captions']:
                            items.append(parse_item);

            return jsonify(items)
        else:
            return jsonify({'server': 'error'}), 400
    except:
        return jsonify({'server': 'error'}), 400

@app.route('/scrapy', methods=['POST'])
def get_items():
    users = db.users.find({}, {'_id': False, 'parse': True, 'id': True})

    items_data = []
    users_parse = []
    for user in users:
        users_parse.append(user);
        for index, parse_item in enumerate(user['parse']):
            obj = {
                'user_id': user['id'],
                'account_index': index,
                'account': parse_item['account']
            }
            items_data.append(obj);

    for item_data in items_data:
        curl_temp = pycurl.Curl()
        io_temp = io.BytesIO()
        curl_temp.setopt(curl_temp.URL, 'http://localhost:9080/crawl.json')
        curl_temp.setopt(curl_temp.WRITEFUNCTION, io_temp.write)
        curl_temp.setopt(curl_temp.POST, True)
        account = item_data['account']
        post = '{{ "spider_name":"instagram", "max_requests":"20", "start_requests": true, "account":"{}"}}'.format(account)
        print(post)
        curl_temp.setopt(curl_temp.POSTFIELDS, post)
        curl_temp.perform()
        curl_temp.close()
        body = io_temp.getvalue().decode('UTF-8')
        items = json.loads(body)['items']
        print('!', len(items), items)

        update_user_parse = []
        for user_parse in users_parse:
            if user_parse['id'] == item_data['user_id']:
                index = item_data['account_index']
                user_parse['parse'][index]['data'] = items
                update_user_parse = user_parse['parse']

        db.users.update_one({'id': item_data['user_id']}, { '$set': { 'parse': update_user_parse }})

    return jsonify({'status': 'true'})
