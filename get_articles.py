#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import ascp
import db
import time
import HTMLParser
import sqlalchemy

DB = db.MyDB()
SES = DB.make_session()

def get_segment_users():
    with open('user_ids.txt', 'w') as fp:
        d = []
        for user in SES.query(db.User).filter_by(MEDIA_TYPE=7):
            d.append(dict(id=user.ID, media_id= user.MEDIA_ID))

        json.dump(d, fp)

def get_article_list(user_id, hot_time):
    url = "http://it.snssdk.com/pgc/ma/"

    ap = ascp.get_as_cp()
    querystring = {"page_type": "1", "max_behot_time": hot_time, "uid": user_id,
                   "media_id": user_id, "output": "json", "is_json": "1", "count": "20", "page":1,
                   "from": "user_profile_app", "version": "2", "as": ap['as'], "cp": ap['cp']}

    headers = {
        'user-agent': "Mozilla/5.0 (Linux; Android 4.4.4; MuMu Build/V417IR) \
        AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Mobile Safari/537.36 JsSdk/2 NewsArticle/6.3.1 NetType/wifi",
        'cache-control': "no-cache"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    # print (response.text)
    jj = json.loads(response.text)
    has_more = jj['has_more']
    next_hot_time = 0 
    if has_more:
       next_hot_time = jj['next']['max_behot_time']

    list = jj['data']
    print len(list), has_more, next_hot_time
    b_should_hold = False
    if len(list) == 0:
        print response.text
        b_should_hold = True
    
    # ss = []
    # for t in list:
        # print t['title']
        # pri
        # ss.append( [t['item_id'], t['publish_time'], t['has_video'], t['article_url'], t['title'], t['source'],  t['tag'], ' | '.join(t['categories'])])


    return list, has_more, next_hot_time, b_should_hold

def get_user_ids():
    with open('user_ids.txt', 'r') as fp:
        return json.load(fp)

def get_detail(group_id):
    url = "https://www.toutiao.com/a{}/".format(group_id)

    headers = {
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7,la;q=0.6",
        # 'cookie': "tt_webid=6547538660773250573; UM_distinctid=162e3be903dff6-0449f153325ada-33627106-1fa400-162e3be903fbe2; tt_webid=6547538660773250573; _ga=GA1.2.1193771552.1524469973; uuid=\"w:6b278e6d93e24b489d64fc1429314f78\"; login_flag=6e02465e870d2a82323af50ced7a3485; sid_tt=5a14e60aa368844ab5a74397a83fd330; sid_guard=\"5a14e60aa368844ab5a74397a83fd330|1524547131|15552000|Sun\054 21-Oct-2018 05:18:51 GMT\"; __tea_sdk__ssid=b011223f-64ee-4cc5-bbc2-e127f6df85a2; tt_webid=6547538660773250573; WEATHER_CITY=%E5%8C%97%E4%BA%AC; __tea_sdk__user_unique_id=97539191906; __tasessionId=97ajmgt551527917229150; sso_login_status=0; _gid=GA1.2.350819017.1527920525; CNZZDATA1259612802=1144703413-1524465903-https%253A%252F%252Fwww.google.com%252F%7C1527920669",
        'cache-control': "no-cache",
        'postman-token': "879dd0f8-5db8-147c-3a3b-279ea713eb2d"
        }

    response = requests.request("GET", url, headers=headers)
    # print(response.text)
    text = response.text
    content = text[text.find("content: '")+len("content: '"):text.find("groupId: '")]
    # html_parser = HTMLParser.HTMLParser()
    content = HTMLParser.HTMLParser().unescape(content)
    print content
    exit()

def next_time_seg():
    with open('last_time.txt', 'r+') as fp:
        last_time = int(fp.readline())
        if last_time == 0:
            last_time = int(time.time() - 60*60 -5)
        now_time = int(time.time()-5)
        fp.seek(0)
        fp.write(str(now_time))
        fp.truncate()
        return (last_time, now_time)

def inter():
    users = get_user_ids()
    while True:
        ts = next_time_seg()
        print ts
        for u in users:
            ss = get_article_list(u['media_id'])
            for s in ss:
                if s['publish_time'] > ts[0] and s['publish_time'] <= ts[1] and not s['has_video']:
                    #yooo we got an new article!!!!
                    # TODO fix 下面的代码
                    url = s[3]
                    print s[0], url, s[4], s[5]
                    get_detail(s[0])
                else:
                    pass
        time.sleep(5*60)

def get_mlc_data():
    b_flag = True
    b_hold_time = 0
    while b_flag:
        b_flag = False
        for user in SES.query(db.User).filter_by(ST=1).limit(10):
            b_flag = True
            b_has_more = True
            next_hot_time = ""
            while b_has_more:
                ss, b_has_more, next_hot_time, b_should_hold = get_article_list(user.MEDIA_ID, next_hot_time)
                for s in ss:
                    if not s['has_video']:
                        #a article
                        A = db.Content()
                        A.ID = s['item_id']
                        A.CATEGORIES =  ','.join(s['categories'])
                        A.CITY = s['city']
                        A.CREATOR_UID = s['creator_uid']
                        A.IMAGE_LIST = json.dumps(s['image_list'])       
                        A.KEYWORDS = s['keywords']
                        A.LABEL = ','.join(s['label'])
                        A.MEDIA_ID = s['media_id']
                        A.PUBLISH_TIME = s['publish_time']
                        A.SOURCE = s['source']
                        A.ST = 0
                        A.TAG = s['tag']
                        A.TITLE = s['title']
                        A.URL = s['url']
                        print A.SOURCE, A.TITLE
                        SES.add(A)
                        try:
                            SES.commit()
                        except sqlalchemy.exc.IntegrityError as e:
                            SES.rollback()
                            print 'dulp', A.TITLE, A.ID
                    else:
                        #a video
                        print 'skip video'
                if b_should_hold:
                    b_hold_time += 1
                    if b_hold_time > 5:
                        #after 5 holding request, do one hold job
                        print 'holding 30 secs'
                        time.sleep(30)
                        b_hold_time = 0
                else:
                    b_hold_time = 0
                # time.sleep(1)
            user.ST = 2
            SES.commit()

get_mlc_data()
