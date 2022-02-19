#!/usr/bin/env python
# coding: utf-8

# In[43]:


import requests
import os
import json
import pandas as pd
import numpy as np
import getpass


# In[112]:


pd.set_option("display.max_rows",2000)


# In[44]:


bearer_token = getpass.getpass(prompt = 'BEARER_TOKEN?')


# In[2]:


# Please don't save your twitter bearer token here
# os.environ['BEARER_TOKEN'] = 'xxxxxxx'
# bearer_token = os.environ.get('BEARER_TOKEN')


# In[46]:


# print(bearer_token)


# In[86]:


def create_url_get_id(usrnm):
    # Specify the usernames that you want to lookup below
    # You can enter up to 100 comma-separated values.
    usernames = usrnm
    user_fields = "user.fields=id,name,username,created_at"
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, user_fields)
    return url


# In[87]:


def bearer_oauth_get_id(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


# In[88]:


def connect_to_endpoint_get_id(url):
    response = requests.request("GET", url, auth=bearer_oauth_get_id,)
#     print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


# In[89]:


def get_id(usrnm):
    url = create_url_get_id(usrnm)
    json_response = connect_to_endpoint_get_id(url)
#     print(json.dumps(json_response, indent=4, sort_keys=True))
    return json_response


# In[146]:


"""
(@AzukiZen, @worldwide_WEB3), 
less successful projects (@RavePigsNFT), popular people in the space (AB, Ellio, Squid, Vidar), 
and a few normies in the space with low follower count (@Arvo mine lol)
"""
cols = ['id','name','username','created_at']
df_get_id = pd.DataFrame()
usernames=['VulcanForged','DeRaceNFT','altura_nft','playbigtime','SIPHERxyz','animocabrands',           'zssbecker','elliotrades','AzukiZen','Worldwide_WEB3','RavePigsNFT','ANordicRaven','arvo']
# Make a short list since we are restricted to 15 follower lookup requests per 15 minute period
usernames=['VulcanForged','DeRaceNFT','playbigtime','SIPHERxyz','animocabrands']
for username in usernames:
#     print(username)
    out_id_data = (get_id('usernames='+username))
    df_get_id = df_get_id.append(pd.json_normalize(out_id_data['data']),ignore_index=True)
df_get_id = df_get_id.loc[:,cols]
df_get_id


# In[92]:


def create_url_get_followers(user_id):
    # Replace with user ID below
#     user_id = 2244994945
#     return "https://api.twitter.com/2/users/{}/followers".format(user_id)
    return f"https://api.twitter.com/2/users/{user_id}/followers"


# In[142]:


# https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a
def get_params_get_followers(next_page,max_results=1000):
    query_params = {
        'user.fields':'id,name,username,created_at',
        'max_results':max_results,
        'pagination_token':next_page
    }
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
#     user_fields = "user.fields:id,name"
    return query_params


# In[143]:


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FollowersLookupPython"
    return r


# In[144]:


def connect_to_endpoint_get_followers(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
#     print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


# In[145]:


def get_followers(id,next_page):
    url = create_url_get_followers(id)
    params = get_params_get_followers(next_page)
    json_response = connect_to_endpoint_get_followers(url, params)
#     print(json.dumps(json_response, indent=4, sort_keys=True))
    return json_response


# In[151]:


# get_followers(1243470638477697024,None)


# In[147]:


cols = ['id','name','username','created_at','follow_id','follow_name','follow_username']
df_followers_all = pd.DataFrame()
df_followers_meta_all = pd.DataFrame()
# cycle through the id list and pull followers
# result limit on api call is 1000 records
# need to ad
for _, row in df_get_id.iterrows():

    df_followers = pd.DataFrame()
    df_followers_meta = pd.DataFrame()
    follow_id = row['id']
    follow_name = row['name']
    follow_username = row['username']
    i = 1
    next_page = None
# Short list has length of 5. Attempt to get 3 pages of data per id (15 total calls out of 15 limit)
    while i <= 3:
        out_id_data = (get_followers(follow_id,next_page))
        df_followers = df_followers.append(pd.json_normalize(out_id_data['data']),ignore_index=True)
        df_followers['follow_id'] = follow_id
        df_followers['follow_name'] = follow_name
        df_followers['follow_username'] = follow_username
        df_followers = df_followers.loc[:,cols]
        df_meta = pd.json_normalize(out_id_data['meta'])
        df_followers_meta = df_followers_meta.append(df_meta,ignore_index=True)
        next_page = df_meta['next_token'].values[0]
        if next_page == None:
            print('no next_page: ',follow_id,follow_name,follow_username,i)
            break
        i+=1

    df_followers_all = df_followers_all.append(df_followers,ignore_index=True)
    df_followers_meta_all = df_followers_meta_all.append(df_followers_meta,ignore_index=True)
    
df_followers_all.reset_index(drop=True,inplace=True)
df_followers_meta_all.reset_index(drop=True,inplace=True)


# In[148]:


df_followers_all.shape


# In[150]:


df_followers_all


# In[ ]:




