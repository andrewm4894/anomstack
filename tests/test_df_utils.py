import pandas as pd

from anomstack.df.utils import generate_insert_sql


class TestGenerateInsertSQL:
    def test_batches_all_rows(self):
        df = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})
        result = generate_insert_sql(df, "my_table", batch_size=2)
        expected = [
            "INSERT INTO my_table (id, name) VALUES (1, 'a'), (2, 'b');",
            "INSERT INTO my_table (id, name) VALUES (3, 'c');",
        ]
        assert result == expected

    def test_timestamp_quoting(self):
        df = pd.DataFrame(
            {
                "metric_timestamp": [
                    pd.Timestamp("2023-01-01"),
                    pd.Timestamp("2023-01-02"),
                ],
                "value": [10, 20],
            }
        )
        result = generate_insert_sql(df, "metrics", batch_size=1)
        expected = [
            (
                "INSERT INTO metrics (metric_timestamp, value) "
                "VALUES ('2023-01-01 00:00:00', 10);"
            ),
            (
                "INSERT INTO metrics (metric_timestamp, value) "
                "VALUES ('2023-01-02 00:00:00', 20);"
            ),
        ]
        assert result == expected
