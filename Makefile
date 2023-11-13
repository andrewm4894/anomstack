.PHONY: dashboard
.PHONY: local

dashboard:
	streamlit run ./dashboard.py --server.port 8501

local:
	dagster dev -f anomstack/main.py
