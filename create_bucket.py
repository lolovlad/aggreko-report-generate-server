from server.repositories.FileBucketRepository import FileBucketRepository
from asyncio import run


async def create_bucket():
    repo = FileBucketRepository("user")
    repo_1 = FileBucketRepository("blueprint")
    repo_2 = FileBucketRepository("report")

    await repo_1.create_bucket()
    await repo_2.create_bucket()
    await repo.create_bucket()


async def main():
    await create_bucket()


run(main())