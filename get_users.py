#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

import json
import sys
import db
DB = db.MyDB()
SES = DB.make_session()

g_dc = 0
g_fc = 0

def sg(d, k):
    if d.has_key(k):
        return d[k]
    else:
        return None

# get detail
def d(user_id):
    global g_dc
    g_dc += 1
    url = "http://it.snssdk.com/user/profile/homepage/v4/"

    querystring = {"user_id":user_id,"iid":"31047425023","device_id":"51425358841","ac":"wifi","channel":"tengxun","aid":"13","app_name":"news_article","version_code":"631","version_name":"6.3.1","device_platform":"android","ab_version":"297979,313416,319436,317498,295827,325046,323882,239097,324283,170988,325961,320218,325198,281392,297058,276203,286212,313219,328615,329603,329358,322321,327537,326536,321981,328095,328670,324007,324795,317077,324571,280773,330104,319960,326730,317208,322280,214069,31643,318434,207253,266310,321519,258356,247847,281298,328218,320995,325618,328376,330275,323429,287591,288418,260650,326188,324614,271178,326588,326524,326532","ab_client":"a1,c4,e1,f2,g2,f7","ab_feature":"94563,102749","abflag":"3","ssmix":"a","device_type":"MuMu","device_brand":"Android","language":"zh","os_api":"19","os_version":"4.4.4","uuid":"008796762094657","openudid":"b7215ea70ca32066","manifest_version_code":"631","resolution":"1280*720","dpi":"240","update_version_code":"6310","_rticket":"1524463139363","plugin":"256"}

    headers = {
        'cache-control': "no-cache"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    # print(response.text)
    jj = json.loads(response.text)
    data = jj['data']
    r_following_cnt = 0
    for user in SES.query(db.User).filter_by(ID=user_id).limit(1):
        if data.has_key('name') and data.has_key('screen_name'):
            user.AREA = sg(data, 'area')
            user.FOLLOWERS_COUNT = sg(data, 'followers_count')
            user.MEDIA_TYPE = sg(data, 'media_type')
            user.MEDIA_ID = sg(data,'media_id')
            user.DESCRIPTION = data['description']
            user.VERIFIED_CONTENT = sg(data, 'verified_content')
            user.SCREEN_NAME = sg(data, 'screen_name')
            user.VISIT_COUNT_RECENT = data['visit_count_recent']
            user.USER_AUTH_INFO = data['user_auth_info']
            user.NAME = data['name']
            user.BIG_AVATAR_URL = data['big_avatar_url']
            user.GENDER = data['gender']
            user.UGC_PUBLISH_MEDIA_ID = str(data['ugc_publish_media_id'])
            user.FOLLOWINGS_COUNT = data['followings_count']
            
            r_following_cnt = data['followings_count']
            print 'Got Detail', user.ID, user.NAME
        user.ST = 1
    SES.commit()
    return r_following_cnt

# get link of following
def t(user_id, page, cursor):
    global g_fc
    url = "http://it.snssdk.com/concern/v2/follow/list/v2/"

    querystring = {"count":"20","offset":page*20,"cursor":cursor, "user_id":user_id,"plugin_info":"0","iid":"31047425023","device_id":"51425358841","ac":"wifi","channel":"tengxun","aid":"13","app_name":"news_article","version_code":"631","version_name":"6.3.1","device_platform":"android","ab_version":"297979,313416,319436,317498,295827,325046,323882,239097,324283,170988,325961,320218,325198,281392,297058,276203,286212,313219,328615,329603,329358,322321,327537,326536,321981,328095,328670,324007,324795,317077,324571,280773,330104,319960,326730,317208,322280,214069,31643,318434,207253,266310,321519,258356,247847,281298,328218,320995,325618,328376,330275,323429,287591,288418,260650,326188,324614,271178,326588,326524,326532","ab_client":"a1,c4,e1,f2,g2,f7","ab_feature":"94563,102749","abflag":"3","ssmix":"a","device_type":"MuMu","device_brand":"Android","language":"zh","os_api":"19","os_version":"4.4.4","uuid":"008796762094657","openudid":"b7215ea70ca32066","manifest_version_code":"631","resolution":"1280*720","dpi":"240","update_version_code":"6310","_rticket":"1524461579082","plugin":"256"}

    headers = {
        'cache-control': "no-cache"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    has_more = False

    # print(response.text)
    jj = json.loads(response.text)
    for fo in jj['data']:
        if fo['is_verified'] == 1 and g_id_cache.has_key(fo['user_id']) == False:
            user = db.User()
            user.ID = fo['user_id']
            user.NAME = fo['name']
            user.ST = 0
            SES.add(user)
            try:
                SES.commit()
                g_fc += 1
                print g_dc, g_fc, 'Found', user.ID, fo['name']
                g_id_cache[user.ID] = 1
            except Exception:
                SES.rollback()
                # print 'dulp', user.ID, fo['name']

    if jj.has_key('has_more'):
        has_more = jj['has_more']
    
    next_cursor = jj['cursor']
    return has_more, next_cursor



def routine(start):
    last_cursor = 0
    c = 0
    for user in SES.query(db.User).filter(db.User.ID>start).filter_by(ST=0).limit(10):
        fc = d(user.ID)
        c += 1
        for i in xrange(int(fc/20)):
            has_more, last_cursor = t(user.ID, i, last_cursor)
    if c == 0:
        print 'no more'
        exit()


g_id_cache = {}

def load_cache():
    for id in SES.query(db.User.ID).all():
        g_id_cache[id] = 1


def main():
    load_cache()
    print len(g_id_cache)

    start = int(sys.argv[1]) * 100000000 #954 2009 9115
    while 1:
        routine(start)

