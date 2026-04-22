import json
from typing import Dict, Any, Optional

from db.mysql_client import MySQLClient


class PipelineRunRepository:
    """
    MySQL-backed repository for pipeline execution tracking
    """

    def __init__(self):
        self.client = MySQLClient()

    def create_run(self, input_config: Dict[str, Any]) -> int:
        cursor = self.client.get_cursor()

        query = """
        INSERT INTO pipeline_runs (status, input_config)
        VALUES (%s, %s)
        """

        cursor.execute(
            query,
            (
                "STARTED",
                json.dumps(input_config)  # ✅ FIXED
            )
        )

        self.client.commit()
        return cursor.lastrowid

    def update_status(
        self,
        run_id: int,
        status: str,
        output_summary: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        cursor = self.client.get_cursor()

        query = """
        UPDATE pipeline_runs
        SET status = %s,
            output_summary = %s,
            error = %s
        WHERE id = %s
        """

        cursor.execute(
            query,
            (
                status,
                json.dumps(output_summary) if output_summary else None,  # ✅ FIXED
                error,
                run_id
            )
        )

        self.client.commit()
        return cursor.rowcount > 0

    def get_run(self, run_id: int) -> Dict[str, Any]:
        cursor = self.client.get_cursor()

        query = "SELECT * FROM pipeline_runs WHERE id = %s"
        cursor.execute(query, (run_id,))

        result = cursor.fetchone()

        if not result:
            raise ValueError("Run not found")

        return result
    def list_runs(self, limit: int = 20):
        cursor = self.client.get_cursor()

        query = """
        SELECT id, status, output_summary, error, created_at
        FROM pipeline_runs
        ORDER BY id DESC
        LIMIT %s
        """

        cursor.execute(query, (limit,))
        results = cursor.fetchall()

        runs = []
        for row in results:
            runs.append({
                "id": row.get("id"),
                "status": row.get("status"),
                "output_summary": row.get("output_summary"),
                "error": row.get("error"),
                "created_at": row.get("created_at")
            })

        return runs
