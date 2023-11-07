.PHONY: dashboard
.PHONY: local

dashboard:
	streamlit run ./dashboard.py

local:
	dagster dev -f anomstack/main.py
