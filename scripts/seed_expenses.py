import random
import sys
from datetime import date, timedelta

sys.path.insert(0, ".")

from database.db import get_db


def main():
    if len(sys.argv) != 4:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    user_id = int(sys.argv[1])
    count = int(sys.argv[2])
    months = int(sys.argv[3])

    conn = get_db()
    try:
        # Step 2 — Verify user exists
        user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if user is None:
            print(f"No user found with id {user_id}.")
            sys.exit(1)

        # Categories with (min, max) amount ranges in ₹ and distribution weights
        categories = {
            "Food": (50, 800, 35),
            "Transport": (20, 500, 15),
            "Bills": (200, 3000, 20),
            "Health": (100, 2000, 5),
            "Entertainment": (100, 1500, 5),
            "Shopping": (200, 5000, 10),
            "Other": (50, 1000, 5),
        }

        descriptions = {
            "Food": ["Lunch at local dhaba", "Groceries from kirana store", " chai at tapri",
                     "Dinner at restaurant", "Street food snacks"],
            "Transport": ["Auto rickshaw fare", "Metro card recharge", "Uber ride",
                          "Petrol for bike", "Bus fare"],
            "Bills": ["Electricity bill", "Mobile recharge", "Internet bill",
                      "Water bill", "DTH recharge"],
            "Health": ["Doctor consultation", "Pharmacy medicines", "Path lab test",
                       "Gym membership"],
            "Entertainment": ["Movie ticket", "BookMyShow booking", "Streaming subscription",
                              "Bowling with friends"],
            "Shopping": ["New kurti", "Sneakers", "Groceries from BigBasket",
                         "Electronics accessory", "Festival shopping"],
            "Other": ["Gift for friend", "Salon visit", "Misc. expense",
                      "Temple donation", "Printing charges"],
        }

        # Step 3 — Generate expenses spread across past <months> months
        today = date.today()
        start_date = today - timedelta(days=30 * months)

        names = list(categories.keys())
        weights = [categories[c][2] for c in names]

        rows = []
        for _ in range(count):
            cat = random.choices(names, weights=weights, k=1)[0]
            lo, hi, _ = categories[cat]
            amount = round(random.uniform(lo, hi), 2)
            delta_days = (today - start_date).days
            exp_date = start_date + timedelta(days=random.randint(0, delta_days))
            desc = random.choice(descriptions[cat])
            rows.append((user_id, amount, cat, exp_date.isoformat(), desc))

        # Single transaction — roll back everything if any insert fails
        conn.execute("BEGIN")
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()

        # Step 4 — Confirm
        min_date = min(r[3] for r in rows)
        max_date = max(r[3] for r in rows)

        print(f"✅ Inserted {len(rows)} expenses for user_id {user_id}")
        print(f"📅 Date range: {min_date} to {max_date}")
        print("\nSample of 5 inserted records:")
        sample = conn.execute(
            "SELECT id, date, category, amount, description FROM expenses "
            "WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (user_id,),
        ).fetchall()
        for s in sample:
            print(f"  • id={s['id']} | {s['date']} | {s['category']:14s} | "
                  f"₹{s['amount']:>8.2f} | {s['description']}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Transaction rolled back: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
