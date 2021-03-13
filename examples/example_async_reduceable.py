import asyncio
import time

from async_reduce import async_reduceable


@async_reduceable()
async def fetch(url):
    print('- fetch page: ', url)
    await asyncio.sleep(1)
    return time.time()


async def amain():
    print('-- Simultaneous run')
    coros = [
        fetch('/page') for _ in range(10)
    ]
    results = await asyncio.gather(*coros)

    print('Results:')
    print('\n'.join(map(str, results)))


def main():
    asyncio.run(amain())


if __name__ == '__main__':
    main()
