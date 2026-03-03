from typing import Optional

from mkpipe.spark.base import BaseExtractor
from mkpipe.models import ConnectionConfig, ExtractResult, TableConfig
from mkpipe.utils import get_logger

logger = get_logger(__name__)


class RedisExtractor(BaseExtractor, variant='redis'):
    def __init__(self, connection: ConnectionConfig):
        self.connection = connection
        self.host = connection.host or 'localhost'
        self.port = connection.port or 6379
        self.password = connection.password
        self.database = int(connection.database or 0)

    def extract(self, table: TableConfig, spark, last_point: Optional[str] = None) -> ExtractResult:
        logger.info({
            'table': table.target_name,
            'status': 'extracting',
        })

        import redis
        import pandas as pd
        import json

        r = redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.database,
            decode_responses=True,
        )

        pattern = table.name
        keys = list(r.scan_iter(match=pattern))

        if not keys:
            logger.info({'table': table.target_name, 'status': 'extracted', 'rows': 0})
            return ExtractResult(df=None, write_mode='overwrite')

        rows = []
        for key in keys:
            key_type = r.type(key)
            if key_type == 'string':
                val = r.get(key)
                try:
                    val = json.loads(val)
                    if isinstance(val, dict):
                        val['_key'] = key
                        rows.append(val)
                        continue
                except (json.JSONDecodeError, TypeError):
                    pass
                rows.append({'_key': key, '_value': val})
            elif key_type == 'hash':
                val = r.hgetall(key)
                val['_key'] = key
                rows.append(val)

        if not rows:
            return ExtractResult(df=None, write_mode='overwrite')

        pdf = pd.DataFrame(rows)
        df = spark.createDataFrame(pdf)

        logger.info({
            'table': table.target_name,
            'status': 'extracted',
            'rows': len(rows),
        })

        return ExtractResult(df=df, write_mode='overwrite')
