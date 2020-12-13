from flask import request, jsonify
from app import app

@app.route('/account', methods=['POST'])
def get_account():
    return jsonify({ 'server': 'true' })
