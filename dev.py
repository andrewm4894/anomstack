#%%

import pandas as pd
from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql

print(specs)

#%%

spec = specs['bigquery_example_simple']

#%%

db = spec['db']

#%%

df = read_sql(render("plot_sql", spec), db)
df.head()

#%%