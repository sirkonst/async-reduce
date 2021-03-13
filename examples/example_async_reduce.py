import asyncio
import time

from async_reduce import async_reduce


async def fetch(url):
    print('- fetch page: ', url)
    await asyncio.sleep(1)
    return time.time()


async def amain():
    print('-- First simultaneous run')
    coros = [
        async_reduce(fetch('/page')) for _ in range(10)
    ]
    results = await asyncio.gather(*coros)

    print('Results:')
    print('\n'.join(map(str, results)))

    print('-- Second simultaneous run')
    coros = [
        async_reduce(fetch('/page')) for _ in range(10)
    ]
    results = await asyncio.gather(*coros)

    print('Results:')
    print('\n'.join(map(str, results)))

    print('-- Third simultaneous run with differences')
    coros = [
        async_reduce(fetch('/page/{}'.format(i))) for i in range(10)
    ]
    results = await asyncio.gather(*coros)

    print('Results:')
    print('\n'.join(map(str, results)))


def main():
    asyncio.run(amain())


if __name__ == '__main__':
    main()
