import asyncio
import random
import time

from async_reduce import AsyncReducer, async_reduceable
from async_reduce.hooks import (
    DebugHooks, StatisticsOverallHooks, StatisticsDetailHooks
)

stats_overall = StatisticsOverallHooks()
stats_detail = StatisticsDetailHooks()
async_reduce = AsyncReducer(hooks=DebugHooks() & stats_overall & stats_detail)


@async_reduceable(async_reduce)
async def foo(sec):
    await asyncio.sleep(sec / 100)
    return time.time()


async def amain():
    coros = [
        foo(random.randint(1, 3)) for _ in range(5)
    ]
    await asyncio.gather(*coros)

    print('--- Overall stats ---')
    print(stats_overall)
    print('--- Detail stats ---')
    print(stats_detail)


def main():
    asyncio.run(amain())


if __name__ == '__main__':
    main()
