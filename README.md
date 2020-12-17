# instaParse - automatic aggregator of data from Instagram

Parsing the video files + the texts from this post and searching for them in the app

[More detailed (presentation)](https://github.com/mike-petrov/scrapy_instagram/blob/main/presentation.pdf)

# Technology stack

- Scrapy
- Scrapyrt
- Flask
- React js
- MongoDB

# Also used
- VK Mini App platrofm
- ScraperApi
- Cron task

# Get started
### Frontend
```
cd web
npm install
npm start
```
_it will be better to use vk mini app hosting:_
```
npm run deploy
```
### Backend
##### Flask
```
cd api
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
python run.py
```
##### Scrapy & Scrapyrt
```
pip3 install Scrapy
pip3 install Scrapyrt
scrapyrt
```
##### MongoDB
[good manual](https://github.com/kosyachniy/dev/tree/master/db/mongodb)
##### Cron task
```
crontab -e
sudo systemctl enable cron

grep CRON /var/log/syslog // check logs
```
### Сreators
made by Mike Petrov ([@mike_petrov](https://github.com/mike-petrov)) & Leonid Romanychev ([@romanychev-l](https://github.com/romanychev-l))

433 group of AM-CP Faculty SPBU
