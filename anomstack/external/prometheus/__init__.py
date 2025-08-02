"""
Prometheus integration for Anomstack.

This module provides comprehensive Prometheus support including:
- Reading metrics via PromQL queries  
- Writing metrics via remote write API
- SQL-equivalent query processing for all job types

Job-specific query functions:
"""

from .prometheus import (
    read_sql_prometheus,
    save_df_prometheus,
    get_prometheus_config,
    get_prometheus_auth,
    execute_promql_queries
)

from .train import execute_prometheus_train_query
from .score import execute_prometheus_score_query  
from .alert import execute_prometheus_alert_query
from .change import execute_prometheus_change_query
from .llmalert import execute_prometheus_llmalert_query

__all__ = [
    # Core Prometheus functions
    "read_sql_prometheus",
    "save_df_prometheus", 
    "get_prometheus_config",
    "get_prometheus_auth",
    "execute_promql_queries",
    
    # Job-specific query functions
    "execute_prometheus_train_query",
    "execute_prometheus_score_query",
    "execute_prometheus_alert_query", 
    "execute_prometheus_change_query",
    "execute_prometheus_llmalert_query",
] 