# buffering-async-logger

Helpers for sending logs to a destination in batches using a buffer in an async Python app.

Built for use with [Sumo Logic](https://www.sumologic.com/), which allows for sending logs in batches via an HTTP endpoint. Can potentially work with any other similar service.


## Getting started

1. Install a recent Python 3.x version (if you don't already have one).
2. Create a project that uses asyncio (if you don't already have one) - for example a [FastAPI](https://fastapi.tiangolo.com/) based project. It's also recommended, but not required, that the project uses [Loguru](https://github.com/Delgan/loguru).
3. Install `buffering-async-logger` as a dependency using [Poetry](https://python-poetry.org/), pip, or similar:
   ```sh
   poetry add buffering-async-logger
   ```
4. Use the utils:
   ```python
   import json
   from logging import LogRecord
   from typing import NamedTuple

   from fastapi import FastAPI
   from loguru import logger
   from buffering_async_logger import BufferingAsyncHandler
   from buffering_async_logger import start_flush_buffer_timer


   class LogAggregatorContext(NamedTuple):
       foo: str
       moo: str


   class LogAggregatorKey(NamedTuple):
       woo: str
       hoo: str


   def get_log_aggregator_context() -> LogAggregatorContext:
       return LogAggregatorContext(
           foo="foo123",
           moo="moo123",
       )


   def get_log_aggregator_key_for_record(
          record: LogRecord, context: LogAggregatorContext | None
   ) -> LogAggregatorKey:
       if context is None:
           raise ValueError(
               "context is required by get_log_aggregator_key_for_record"
           )

       return LogAggregatorKey(
           woo=context.foo,
           hoo=f"{context.moo}/{record.levelname}",
       )


   def get_request_headers(
       headers: dict[str, Any], key: LogAggregatorKey
   ) -> dict[str, Any]:
       new_headers = headers.copy()

       new_headers["X-Logshmog-Woo"] = key.woo
       new_headers["X-Logshmog-Hoo"] = key.hoo

       return new_headers


   def get_serialized_record(record: Any) -> dict[str, Any]:
       _record = {
           "timestamp": f"{record['time']}",
           "level": f"{record['level']}",
           "logger": record["name"],
           "message": record["message"],
       }

       if record["extra"].get("foo"):
           _record["foo"] = record["extra"]["foo"]
       if record["extra"].get("moo"):
           _record["moo"] = record["extra"]["moo"]

       return _record


   def log_formatter(record: Any) -> str:
       record["extra"]["serialized"] = json.dumps(
           get_serialized_record(record)
       )
       return "{extra[serialized]}\n"


   async def start_logshmog_flush_buffer_timer():
       await start_flush_buffer_timer(10)


   def configure_buffering_async_logger(context: LogAggregatorContext):
       handler = BufferingAsyncHandler(
           capacity=1000,
           url="https://foo.logshmog.com/v1/logs/a1b2c3",
           get_log_aggregator_key_func=get_aggregator_key_for_record,
           get_request_headers_func=get_request_headers,
           chunk_size=100,
           context=context,
       )

       logger.add(handler, format=log_formatter)


   def configure_logger():
       context = get_log_aggregator_context()
       logger.configure(extra=context._asdict())

       # Config for other log handlers may go here ...

       configure_buffering_async_logger(context)


   def get_app() -> FastAPI:
       """Create a FastAPI app instance."""
       return FastAPI(on_startup=[start_logshmog_flush_buffer_timer])


   configure_logger()
   app = get_app()
   ```


## Developing

To clone the repo:

```sh
git clone git@github.com:Jaza/buffering-async-logger.git
```

To automatically fix code style issues:

```sh
./scripts/format.sh
```

To verify code style and static typing:

```sh
./scripts/verify.sh
```

To run tests:

```sh
./scripts/test.sh
```


## Building

To build the library:

```sh
poetry build
```


Built by [Seertech](https://www.seertechsolutions.com/).
