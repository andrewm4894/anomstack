from dotenv import load_dotenv
from fasthtml.common import Div, P, fast_app, serve

from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql

load_dotenv('./.env')

app,rt = fast_app()

@rt('/')
def get():
    print(999)
    metric_batches = list(specs.keys())

    for metric_batch in specs:

        spec = specs[metric_batch]

        # get data
        sql = render("dashboard_sql", spec, params={"alert_max_n": 90})
        db = spec["db"]
        df = read_sql(sql, db=db)
        print(df.head())

    return Div(P(metric_batches))


serve(host="0.0.0.0", port=5002)
