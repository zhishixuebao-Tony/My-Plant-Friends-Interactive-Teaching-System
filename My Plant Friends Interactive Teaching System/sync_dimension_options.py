import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = 'mongodb://localhost:27017'
DB_NAME = 'composition_db'

DIMENSION_ALIAS_MAP = {
    '我暂时没有新的发现。': '我暂时没有新的发现',
    '我暂时没有新的发现': '我暂时没有新的发现',
    '我已经有了新的发现：（1）有以前没观察到的': '我已经有了新的发现：（1）有以前没观察到的',
    '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价一：能真实记录植物特点': '我已经有了新的发现：（1）有以前没观察到的',
    '评价一': '我已经有了新的发现：（1）有以前没观察到的',
    '评价二：能描写自己的感受': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价二：能描写出自己的感受': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价二': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价三：书写认真、字迹工整': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
    '评价三': '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）',
}

NO_NEW = '我暂时没有新的发现'
OPT1 = '我已经有了新的发现：（1）有以前没观察到的'
OPT2 = '我已经有了新的发现：（2）观察后，有了点儿感受（身体感觉 心里想法）'


def normalize_dimension_checks(checks):
    if not isinstance(checks, list):
        return []

    out = []
    seen = set()
    for item in checks:
        key = str(item).strip()
        if not key:
            continue
        val = DIMENSION_ALIAS_MAP.get(key, key)
        if val not in seen:
            out.append(val)
            seen.add(val)

    # enforce mutual exclusion rule
    if NO_NEW in seen:
        return [NO_NEW]

    normalized = []
    if OPT1 in seen:
        normalized.append(OPT1)
    if OPT2 in seen:
        normalized.append(OPT2)
    return normalized


async def main():
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]

    cursor = db.students.find({}, {'_id': 1, 'dimension_evaluations': 1})
    total = 0
    changed = 0

    async for doc in cursor:
        total += 1
        old_checks = doc.get('dimension_evaluations', [])
        new_checks = normalize_dimension_checks(old_checks)
        if old_checks != new_checks:
            await db.students.update_one({'_id': doc['_id']}, {'$set': {'dimension_evaluations': new_checks}})
            changed += 1

    print(f'Students scanned: {total}')
    print(f'Students updated: {changed}')
    client.close()


if __name__ == '__main__':
    asyncio.run(main())
