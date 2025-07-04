import pandas as pd
from anomstack.df.utils import generate_insert_sql


class TestGenerateInsertSql:
    """Tests for the generate_insert_sql utility."""

    def test_batches_and_values(self):
        # Create DataFrame with more rows than default batch size (100)
        df = pd.DataFrame({
            "id": range(1, 251),
            "value": [f"value_{i}" for i in range(1, 251)],
        })

        insert_sqls = generate_insert_sql(df, "test_table")

        # Expect ceil(250/100) = 3 batches
        assert len(insert_sqls) == 3

        # Build expected SQL strings manually
        columns = ", ".join(df.columns)
        expected_sqls = []
        for i in range(0, len(df), 100):
            batch = df.iloc[i:i + 100]
            values_list = []
            for _, row in batch.iterrows():
                row_values = []
                for val in row:
                    if isinstance(val, str) or isinstance(val, pd.Timestamp):
                        row_values.append(f"'{val}'")
                    else:
                        row_values.append(str(val))
                values_list.append(f"({', '.join(row_values)})")
            values = ", ".join(values_list)
            expected_sqls.append(
                f"INSERT INTO test_table ({columns}) VALUES {values};"
            )

        assert insert_sqls == expected_sqls

