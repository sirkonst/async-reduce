import asyncio
import time

from async_reduce import async_reduce


async def fetch(url):
    print('- fetch page: ', url)
    await asyncio.sleep(1)
    return time.time()


async def amain():
    coros = [
        async_reduce(fetch('/page')) for _ in range(10)
    ]

    print('-- First simultaneous run')
    done, pending = await asyncio.wait(coros)
    assert not pending

    print('Results:')
    for f in done:
        print(
            await f
        )

    print('-- Second simultaneous run')
    coros = [
        async_reduce(fetch('/page')) for _ in range(10)
    ]

    done, pending = await asyncio.wait(coros)
    assert not pending

    print('Results:')
    for f in done:
        print(
            await f
        )

    print('-- Third simultaneous run with differences')
    coros = [
        async_reduce(fetch('/page/{}'.format(i))) for i in range(10)
    ]

    done, pending = await asyncio.wait(coros)
    assert not pending

    print('Results:')
    for f in done:
        print(
            await f
        )


def main():
    asyncio.run(amain())


if __name__ == '__main__':
    main()
