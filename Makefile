.PHONY: dashboard
.PHONY: local
.PHONY: docker

dashboard:
	streamlit run ./dashboard.py --server.port 8501

local:
	dagster dev -f anomstack/main.py

docker:
	docker compose up -d --build
