from dotenv import load_dotenv
from fasthtml.common import Div, P, fast_app, serve

from anomstack.config import specs

load_dotenv('./.env')

app,rt = fast_app()

@rt('/')
def get():
    metric_batches = list(specs.keys())
    return Div(P(metric_batches))


serve()
