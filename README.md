# mkpipe-extractor-redis

Redis extractor plugin for [MkPipe](https://github.com/mkpipe-etl/mkpipe). Reads Redis keys using `redis-py` `SCAN` and converts to Spark DataFrames. Supports `string` (JSON) and `hash` key types.

## Documentation

For more detailed documentation, please visit the [GitHub repository](https://github.com/mkpipe-etl/mkpipe).

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

---

## Connection Configuration

```yaml
connections:
  redis_source:
    variant: redis
    host: localhost
    port: 6379
    password: mypassword
    database: "0"
```

---

## Table Configuration

The `name` field is a Redis key pattern (glob-style). Both `string` keys containing JSON objects and `hash` keys are supported:

```yaml
pipelines:
  - name: redis_to_pg
    source: redis_source
    destination: pg_target
    tables:
      - name: "user:*"
        target_name: stg_users
        replication_method: full
```

---

## Supported Key Types

| Redis Type | Behavior |
|---|---|
| `string` | Value is parsed as JSON. If it is a dict, fields become columns. Otherwise stored as `_value`. |
| `hash` | All hash fields become columns. |

Other key types (list, set, zset, stream) are ignored.

---

## Performance Notes

- Redis is single-threaded on the server side — parallel reads do not help and can hurt by saturating the connection.
- For very large keyspaces, Redis `SCAN` is non-blocking and iterates in batches (internally 10 keys per iteration). It is safe for production but slower than bulk reads.
- Keep patterns as specific as possible to reduce scanned keys.
- All data is collected on the Spark driver before creating the DataFrame — not suitable for keyspaces larger than available driver memory.

---

## All Table Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | string | required | Redis key glob pattern (e.g. `user:*`) |
| `target_name` | string | required | Destination table name |
| `replication_method` | `full` only | `full` | Incremental not supported |
| `tags` | list | `[]` | Tags for selective pipeline execution |
| `pass_on_error` | bool | `false` | Skip table on error instead of failing |
