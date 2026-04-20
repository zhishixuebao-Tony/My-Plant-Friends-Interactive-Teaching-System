import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = 'mongodb://localhost:27017'
DB_NAME = 'composition_db'

SENSORY_ALIAS_MAP = {
    '看了看': '看一看',
    '看一看': '看一看',
    '闻了闻': '闻一闻',
    '闻一闻': '闻一闻',
    '摸了摸': '摸一摸',
    '摸一摸': '摸一摸',
    '听一听': '听一听',
    '尝了尝': '尝一尝',
    '尝一尝': '尝一尝',
    '其他': '其他',
}


def normalize_checks(checks):
    if not isinstance(checks, list):
        return []

    out = []
    seen = set()
    for item in checks:
        key = str(item).strip()
        if not key:
            continue
        value = SENSORY_ALIAS_MAP.get(key, key)
        if value not in seen:
            out.append(value)
            seen.add(value)
    return out


async def main():
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]

    cursor = db.students.find({}, {'_id': 1, 'sensory_evaluations': 1})
    total = 0
    changed = 0

    async for doc in cursor:
        total += 1
        old_checks = doc.get('sensory_evaluations', [])
        new_checks = normalize_checks(old_checks)
        if old_checks != new_checks:
            await db.students.update_one({'_id': doc['_id']}, {'$set': {'sensory_evaluations': new_checks}})
            changed += 1

    print(f'Students scanned: {total}')
    print(f'Students updated: {changed}')
    client.close()


if __name__ == '__main__':
    asyncio.run(main())
