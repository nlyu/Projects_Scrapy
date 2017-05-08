import pandas as pd
import numpy as np


company = []
df = pd.read_csv('result_final982.csv', names=['UID', 'Name', 'Title', 'Company'])
df = df.drop(df[df.Company == 'University of Illinois at Urbana-Champaign'].index)

title = df.Title
company = df.Company

uid = df.UID
num_company = company.value_counts()
num_title = title.value_counts()
num_uid = uid.value_counts()
print(num_uid.mean())
print(num_uid.median())
