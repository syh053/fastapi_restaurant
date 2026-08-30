"""種子資料腳本

一次灌入一組固定的繁體中文範例資料（分類／使用者／餐廳／菜單／評論），
方便開發、demo 與分頁／排序功能的驗證。

用法：
    uv run python db/seed.py            # 不清空，逐筆比對，只追加還沒有的資料（重複的略過）
    uv run python db/seed.py --reset    # 先清空 restaurant schema 各表，再整組重建

需先套用 migration：uv run alembic -n restaurant upgrade head
"""
import asyncio
import sys
import uuid
from pathlib import Path

# 讓 `python db/seed.py` 能 import db.model.*（把 repo root 加進 sys.path）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bcrypt
from sqlalchemy import select, text

from db.model import Comment, MenuItem, Restaurant, User
from db.model.category import Category
from db.model.database import AsyncSessionLocal


def _hash(pw: str) -> str:
    """以 bcrypt 雜湊密碼（與 src/service/user/add_user.py 的寫法一致）"""
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# --- 分類 -------------------------------------------------------------------

# 「預設分類」為必要項目：CRUDRestaurant._get_default_category_id 以此名稱查詢
CATEGORIES = ["預設分類", "台式小吃", "日式料理", "義式餐廳", "美式漢堡", "飲料甜點"]


# --- 使用者 ----------------------------------------------------------------

USERS = [
    {"name": "admin", "email": "admin@test.com", "password": "123", "is_admin": True},
    {"name": "Sindy", "email": "sindy@test.com", "password": "123", "is_admin": False},
    {"name": "Ken", "email": "ken@test.com", "password": "123", "is_admin": False},
    {"name": "Amy", "email": "amy@test.com", "password": "123", "is_admin": False},
    {"name": "John", "email": "john@test.com", "password": "123", "is_admin": False},
    {"name": "Jane", "email": "jane@test.com", "password": "123", "is_admin": False},
]


# --- 餐廳 -----------------------------------------------------------------

RESTAURANTS = [
    {
        "name": "玉堂春魯肉飯", "category": "台式小吃", "tel": "04-23013008", "openingHours": 10,
        "address": "臺中市西區中興里美村路一段220號", "description": "在地老字號魯肉飯，滷汁香而不膩。",
    },
    {
        "name": "李海魯肉飯", "category": "台式小吃", "tel": "04-22200986", "openingHours": 14,
        "address": "臺中市中區成功路105號", "description": "營業到凌晨的宵夜好去處。",
    },
    {
        "name": "財神爺魯肉飯", "category": "台式小吃", "tel": "04-22345678", "openingHours": 9,
        "address": "臺中市北區三民路三段129號", "description": "招牌爌肉飯與筍絲滷得入味。",
    },
    {
        "name": "一蘭拉麵 台中店", "category": "日式料理", "tel": "04-23201234", "openingHours": 12,
        "address": "臺中市西屯區台灣大道三段251號", "description": "豚骨湯頭濃郁，可自選辣度與麵條硬度。",
    },
    {
        "name": "藏壽司 秀泰站前店", "category": "日式料理", "tel": "04-22299888", "openingHours": 11,
        "address": "臺中市東區南京路147號", "description": "迴轉壽司，集點可抽扭蛋。",
    },
    {
        "name": "和心屋丼飯", "category": "日式料理", "tel": "04-23788899", "openingHours": 10,
        "address": "臺中市南屯區公益路二段51號", "description": "現點現做的海鮮丼與炸豬排丼。",
    },
    {
        "name": "薩莉亞 台中中港店", "category": "義式餐廳", "tel": "04-23139999", "openingHours": 13,
        "address": "臺中市西屯區台灣大道三段301號", "description": "平價義式，適合聚餐分食。",
    },
    {
        "name": "拿坡里窯烤披薩", "category": "義式餐廳", "tel": "04-23021777", "openingHours": 9,
        "address": "臺中市西區精誠路12號", "description": "柴燒窯烤餅皮，現桿現烤。",
    },
    {
        "name": "五郎漢堡 Goro Burger", "category": "美式漢堡", "tel": "04-23268686", "openingHours": 8,
        "address": "臺中市北區太原路一段99號", "description": "手打牛肉排，麵包每日現烤。",
    },
    {
        "name": "麻吉茶飲", "category": "飲料甜點", "tel": "04-23011234", "openingHours": 12,
        "address": "臺中市西區向上路一段2號", "description": "手搖飲與現烤鬆餅，下午茶人氣店。",
    },
]


# --- 菜單 -----------------------------------------------------------------

# section -> section_order（數字越小越前面）
SECTION_ORDER = {"套餐": 1, "主餐": 2, "副餐": 3, "湯品": 4, "飲料": 8, "甜點": 9}

# restaurant name -> list of (name, price, section, description)
MENU_BY_RESTAURANT = {
    "玉堂春魯肉飯": [
        ("魯肉飯便當", 110, "套餐", "魯肉飯＋主菜＋三樣配菜"),
        ("雞腿飯便當", 130, "套餐", None),
        ("魯肉飯（小）", 30, "主餐", None),
        ("魯肉飯（大）", 45, "主餐", None),
        ("焢肉飯", 75, "主餐", "帶皮五花，滷至軟嫩"),
        ("燙青菜", 35, "副餐", None),
        ("滷蛋", 15, "副餐", None),
        ("滷豆腐", 20, "副餐", None),
        ("味噌湯", 20, "湯品", None),
        ("貢丸湯", 30, "湯品", None),
        ("紅茶", 20, "飲料", None),
    ],
    "李海魯肉飯": [
        ("宵夜套餐", 120, "套餐", "魯肉飯＋切盤＋湯"),
        ("魯肉飯", 35, "主餐", None),
        ("爌肉飯", 70, "主餐", None),
        ("排骨飯", 80, "主餐", None),
        ("切盤（豬頭皮）", 60, "副餐", None),
        ("燙地瓜葉", 35, "副餐", None),
        ("苦瓜排骨湯", 45, "湯品", None),
        ("四神湯", 50, "湯品", None),
        ("冬瓜茶", 20, "飲料", None),
    ],
    "財神爺魯肉飯": [
        ("招牌爌肉飯套餐", 115, "套餐", None),
        ("爌肉飯", 65, "主餐", None),
        ("魯肉飯", 30, "主餐", None),
        ("雞肉飯", 50, "主餐", None),
        ("筍絲", 30, "副餐", None),
        ("滷白菜", 30, "副餐", None),
        ("竹筍湯", 40, "湯品", None),
        ("豆漿", 20, "飲料", None),
    ],
    "一蘭拉麵 台中店": [
        ("經典豚骨拉麵套餐", 380, "套餐", "拉麵＋半熟蛋＋叉燒加點"),
        ("豚骨拉麵", 280, "主餐", "可自選辣度與麵硬度"),
        ("叉燒拉麵", 360, "主餐", None),
        ("加麵（替玉）", 50, "副餐", None),
        ("溏心蛋", 40, "副餐", None),
        ("海苔", 30, "副餐", None),
        ("綠茶", 40, "飲料", None),
        ("柚子雪酪", 70, "甜點", None),
    ],
    "藏壽司 秀泰站前店": [
        ("超值雙人套餐", 520, "套餐", "12 貫壽司＋味噌湯＋茶碗蒸 x2"),
        ("鮭魚握壽司", 40, "主餐", None),
        ("鮪魚握壽司", 60, "主餐", None),
        ("玉子燒", 40, "主餐", None),
        ("炸蝦手卷", 50, "副餐", None),
        ("茶碗蒸", 45, "副餐", None),
        ("味噌湯", 30, "湯品", None),
        ("綠茶（自助）", 0, "飲料", "免費供應"),
        ("北海道霜淇淋", 60, "甜點", None),
    ],
    "和心屋丼飯": [
        ("海鮮丼套餐", 320, "套餐", "海鮮丼＋小菜＋湯"),
        ("炸豬排丼", 220, "主餐", None),
        ("親子丼", 180, "主餐", None),
        ("鰻魚丼", 360, "主餐", None),
        ("溫泉蛋", 30, "副餐", None),
        ("和風沙拉", 60, "副餐", None),
        ("豚汁", 50, "湯品", None),
        ("焙茶", 40, "飲料", None),
    ],
    "薩莉亞 台中中港店": [
        ("經典雙人套餐", 499, "套餐", "義大利麵 x2＋披薩＋沙拉＋飲料 x2"),
        ("番茄肉醬義大利麵", 129, "主餐", None),
        ("白酒蛤蜊義大利麵", 159, "主餐", None),
        ("瑪格麗特披薩", 149, "主餐", None),
        ("酥炸花枝圈", 89, "副餐", None),
        ("凱薩沙拉", 79, "副餐", None),
        ("蔬菜濃湯", 49, "湯品", None),
        ("無限暢飲吧", 59, "飲料", None),
        ("提拉米蘇", 69, "甜點", None),
    ],
    "拿坡里窯烤披薩": [
        ("雙人披薩套餐", 620, "套餐", "9 吋披薩 x2＋前菜＋飲料 x2"),
        ("瑪格麗特披薩", 260, "主餐", "水牛乳酪＋羅勒"),
        ("四種起司披薩", 320, "主餐", None),
        ("臘腸披薩", 300, "主餐", None),
        ("烤大蒜麵包", 90, "副餐", None),
        ("凱薩沙拉", 120, "副餐", None),
        ("氣泡水", 60, "飲料", None),
        ("烤布蕾", 100, "甜點", None),
    ],
    "五郎漢堡 Goro Burger": [
        ("經典套餐", 260, "套餐", "漢堡＋薯條＋飲料"),
        ("原味牛肉堡", 180, "主餐", "150g 手打牛肉排"),
        ("起司牛肉堡", 200, "主餐", None),
        ("蘑菇培根堡", 230, "主餐", None),
        ("脆薯", 70, "副餐", None),
        ("洋蔥圈", 80, "副餐", None),
        ("玉米濃湯", 50, "湯品", None),
        ("可樂", 40, "飲料", None),
        ("布朗尼", 80, "甜點", None),
    ],
    "麻吉茶飲": [
        ("下午茶套餐", 160, "套餐", "手搖飲＋鬆餅一份"),
        ("珍珠鮮奶茶", 65, "飲料", "可調糖冰"),
        ("四季春青茶", 35, "飲料", None),
        ("檸檬紅茶", 50, "飲料", None),
        ("冬瓜檸檬", 55, "飲料", None),
        ("原味鬆餅", 90, "甜點", None),
        ("巧克力鬆餅", 110, "甜點", None),
        ("布丁一份", 40, "甜點", None),
    ],
}


# --- 評論 -----------------------------------------------------------------

# (餐廳 index, 使用者 index 於 USERS 中的位置, 評論文字)
# 使用者 index 從 1 起（0 是 admin，評論只用一般使用者）
COMMENTS = [
    (0, 1, "魯肉飯滷汁很香，配菜也給得大方，CP 值高！"),
    (0, 2, "中午人有點多要排隊，但翻桌快。"),
    (0, 3, "焢肉入口即化，會再來。"),
    (1, 2, "宵夜時段還開著真的太感人，排骨飯份量足。"),
    (1, 4, "切盤新鮮，四神湯很暖。"),
    (2, 1, "爌肉飯偏甜，喜歡這個口味。"),
    (2, 5, "筍絲滷得很入味，白飯可以續。"),
    (3, 2, "湯頭濃郁，辣度可以自己選很貼心。"),
    (3, 3, "價格偏高，但份量和品質有到位。"),
    (3, 4, "溏心蛋加點必備，蛋黃流心。"),
    (4, 1, "小朋友很愛抽扭蛋，壽司新鮮度不錯。"),
    (4, 5, "尖峰時間候位久，建議先線上取號。"),
    (5, 2, "炸豬排丼酥脆，醬汁不會太鹹。"),
    (5, 3, "親子丼滑嫩，份量剛好。"),
    (6, 4, "適合朋友聚餐分食，飲料吧很划算。"),
    (6, 5, "白酒蛤蜊麵蛤蜊給得多。"),
    (7, 1, "餅皮是我喜歡的薄脆型，起司很牽絲。"),
    (7, 2, "窯烤香氣足，內用環境舒服。"),
    (8, 3, "牛肉排肉汁多，麵包也香。"),
    (8, 4, "洋蔥圈炸得剛好，不會太油。"),
    (9, 5, "珍珠煮得Q，甜度可調很棒。"),
    (9, 1, "鬆餅外酥內軟，配茶剛剛好。"),
    (9, 2, "冬瓜檸檬清爽，夏天必點。"),
]


async def seed(reset: bool) -> None:
    """
    灌入種子資料。

    reset=True  ：先 TRUNCATE restaurant schema 各表，再整組重建。
    reset=False ：不清空，逐筆比對既有資料，只補「還沒有的」，重複的略過。

    兩種模式共用同一段「比對 -> 只加新的」邏輯；reset 只是先把表清空，
    使比對結果全為「不存在」。
    """
    async with AsyncSessionLocal() as session:
        if reset:
            await session.execute(text(
                'TRUNCATE restaurant.menu_item, restaurant.comment, '
                'restaurant.restaurant, restaurant."user", restaurant.category '
                'RESTART IDENTITY CASCADE'
            ))
            print("已清空 restaurant schema 各表")

        # --- 分類（以 name 判斷是否重複）---
        existing_category = dict(
            (await session.execute(select(Category.name, Category.id))).all()
        )
        category_id: dict[str, uuid.UUID] = {}
        new_categories: list[Category] = []
        for name in CATEGORIES:
            if name in existing_category:
                category_id[name] = existing_category[name]
            else:
                obj = Category(id=uuid.uuid4(), name=name)
                new_categories.append(obj)
                category_id[name] = obj.id

        # --- 使用者（以 name 判斷是否重複）---
        existing_user = dict(
            (await session.execute(select(User.name, User.id))).all()
        )
        user_id: dict[str, uuid.UUID] = {}
        new_users: list[User] = []
        for u in USERS:
            if u["name"] in existing_user:
                user_id[u["name"]] = existing_user[u["name"]]
            else:
                obj = User(
                    id=uuid.uuid4(),
                    name=u["name"],
                    email=u["email"],
                    password=_hash(u["password"]),
                    is_admin=u["is_admin"],
                )
                new_users.append(obj)
                user_id[u["name"]] = obj.id

        # --- 餐廳（以 name 判斷是否重複）---
        existing_restaurant = dict(
            (await session.execute(select(Restaurant.name, Restaurant.id))).all()
        )
        restaurant_id: dict[str, uuid.UUID] = {}
        new_restaurants: list[Restaurant] = []
        for r in RESTAURANTS:
            if r["name"] in existing_restaurant:
                restaurant_id[r["name"]] = existing_restaurant[r["name"]]
            else:
                obj = Restaurant(
                    id=uuid.uuid4(),
                    name=r["name"],
                    tel=r["tel"],
                    openingHours=r["openingHours"],
                    address=r["address"],
                    description=r["description"],
                    category_id=category_id[r["category"]],
                )
                new_restaurants.append(obj)
                restaurant_id[r["name"]] = obj.id

        # --- 菜單（以 (restaurant_id, 餐點名稱) 判斷是否重複）---
        existing_menu = {
            (rid, name)
            for rid, name in (await session.execute(
                select(MenuItem.restaurant_id, MenuItem.name)
            )).all()
        }
        new_menu_items: list[MenuItem] = []
        for restaurant_name, items in MENU_BY_RESTAURANT.items():
            rid = restaurant_id[restaurant_name]
            for name, price, section, description in items:
                if (rid, name) in existing_menu:
                    continue
                new_menu_items.append(MenuItem(
                    id=uuid.uuid4(),
                    restaurant_id=rid,
                    name=name,
                    price=price,
                    section=section,
                    section_order=SECTION_ORDER[section],
                    description=description,
                ))

        # --- 評論（以 (restaurant_id, user_id, 文字) 判斷是否重複）---
        existing_comment = {
            (rid, uid, body)
            for rid, uid, body in (await session.execute(
                select(Comment.restaurant_id, Comment.user_id, Comment.text)
            )).all()
        }
        user_id_by_index = [user_id[u["name"]] for u in USERS]
        restaurant_id_by_index = [restaurant_id[r["name"]] for r in RESTAURANTS]
        new_comments: list[Comment] = []
        for r_idx, u_idx, body in COMMENTS:
            rid = restaurant_id_by_index[r_idx]
            uid = user_id_by_index[u_idx]
            if (rid, uid, body) in existing_comment:
                continue
            new_comments.append(Comment(
                id=uuid.uuid4(),
                text=body,
                restaurant_id=rid,
                user_id=uid,
            ))

        # 依外鍵相依順序寫入：分類 -> 使用者 -> 餐廳 -> 菜單／評論。
        # Comment/MenuItem 與 User/Restaurant 之間沒有 ORM relationship()，
        # 不能靠 unit-of-work 自動排序，故每一層先 flush 確保外鍵目標已存在。
        session.add_all(new_categories)
        await session.flush()
        session.add_all(new_users)
        session.add_all(new_restaurants)
        await session.flush()
        session.add_all(new_menu_items)
        session.add_all(new_comments)
        await session.commit()

        def _report(label: str, added: int, total: int) -> str:
            return f"{label} +{added}（略過既有 {total - added}）"

        print("seeding 完成：")
        print("  " + _report("分類", len(new_categories), len(CATEGORIES)))
        print("  " + _report("使用者", len(new_users), len(USERS)))
        print("  " + _report("餐廳", len(new_restaurants), len(RESTAURANTS)))
        print("  " + _report(
            "菜單", len(new_menu_items),
            sum(len(v) for v in MENU_BY_RESTAURANT.values()),
        ))
        print("  " + _report("評論", len(new_comments), len(COMMENTS)))


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    if reset:
        print("--reset：將清空 restaurant schema 內所有資料後重建")
    asyncio.run(seed(reset=reset))
