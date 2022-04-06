#!/usr/bin/env python
# coding: utf-8

# In[41]:


import pandas as pd
import numpy as np
import sys
import neo4j
from neo4j import GraphDatabase
import streamlit as st
import streamlit_agraph
from streamlit_agraph import agraph, Node, Edge, Config
from streamlit_agraph import TripleStore, GraphAlgos
import networkx as nx
from networkx.algorithms import community
pd.set_option('display.max_rows',6000)
pd.set_option('display.max_columns',500)
pd.set_option('display.max_colwidth',100)


# In[32]:


data_folder = '../data/'
input_file = data_folder + 'who_are_projects_following.csv'
df_following_all = pd.read_csv(input_file)


# In[33]:


# df_following_all.head()


# In[34]:


nodes = []
edges = []
for _,row in df_following_all.iterrows():
    nodes.append(Node(id=row['following_username'],label=row['following_username']))
    nodes.append(Node(id=row['username'],label=row['username']))
    edges.append(Edge(source=row['following_username'],label='follows',target=row['username']))


# In[35]:


config = Config(width=1500,height=750,directed=True,nodeHighlightBehavior=True,highlightColor="#F7A7A6",collapsible=True,
                node={'labelProperty':'label'},link={'labelProperty':'label','renderLabel':True})


# In[36]:


# return_value = agraph(nodes=nodes,edges=edges,config=config)


# In[37]:


g = nx.Graph()


# In[38]:


for _,row in df_following_all.iterrows():
    g.add_node(row['following_username'])
    g.add_node(row['username'])
    g.add_edge(row['following_username'],row['username'],label='Follows')


# In[39]:


# g.nodes()


# In[40]:


# g.edges()


# In[15]:


# communities_generator = community.girvan_newman(g)
# top_level_communities = next(communities_generator)
# next_level_communities = next(communities_generator)
# sorted(map(sorted,next_level_communities))


# In[42]:


df_centrality = pd.DataFrame.from_dict(nx.degree_centrality(g),orient='index',columns=['Centrality'])
df_centrality.sort_values(by='Centrality',axis=0,ascending=False,inplace=True)
df_centrality.reset_index(drop=False,inplace=True)
df_centrality.columns=['Nodes','Centrality']
# df_centrality
centrality_list = list((df_centrality['Centrality'].unique()))
centrality_list.sort()
min_threshold = centrality_list[4]

# In[43]:


df_projects_list = ['VulcanForged','DeRaceNFT','altura_nft','SIPHERxyz','animocabrands',           'zssbecker','elliotrades','AzukiOfficial','GoGalaGames','ultra_io','DefiKingdoms',]
df_single_entity_list = list(df_centrality.loc[df_centrality['Centrality']<min_threshold,'Nodes'])


# In[44]:


len(df_single_entity_list)


# In[45]:


df_following_final = df_following_all.loc[((~df_following_all['username'].isin(df_projects_list))
                    & (~df_following_all['username'].isin(df_single_entity_list)))]
df_following_final.reset_index(drop=True,inplace=True)
# df_following_final.shape


# In[46]:


nodes = []
edges = []
for _,row in df_following_final.iterrows():
    nodes.append(Node(id=row['following_username'],label=row['following_username']))
    nodes.append(Node(id=row['username'],label=row['username']))
    edges.append(Edge(source=row['following_username'],label='follows',target=row['username']))


# In[47]:


return_value = agraph(nodes=nodes,edges=edges,config=config)


# In[ ]:




