import asyncio
import time

from async_reduce import async_reduceable


@async_reduceable()
async def fetch(url):
    print('- fetch page: ', url)
    await asyncio.sleep(1)
    return time.time()


async def amain():
    coros = [
        fetch('/page') for _ in range(10)
    ]

    print('-- Simultaneous run')
    done, pending = await asyncio.wait(coros)

    print('Results:')
    for f in done:
        print(
            await f
        )


def main():
    asyncio.run(amain())


if __name__ == '__main__':
    main()
