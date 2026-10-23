import repo


async def test_empty(session, players):
    assert await repo.leaderboard(session) == []          # без партий в таблицу не попадаем


async def test_order(session, players):
    await repo.record_match(session, "c4", 1, 2, "win1")   # Аня 1016, Боря 984
    await repo.record_match(session, "c4", 3, 4, "win1")   # Вика 1016, Гоша 984
    await repo.record_match(session, "c4", 1, 3, "draw")   # Аня 1016, Вика 1016, у обеих по 2 партии
    await session.commit()
    assert await repo.leaderboard(session) == [
        ("Аня", 1016, 2), ("Вика", 1016, 2), ("Боря", 984, 1), ("Гоша", 984, 1),
    ]


async def test_games_breaks_tie(session, players):
    await repo.record_match(session, "c4", 1, 2, "draw")
    await repo.record_match(session, "c4", 1, 2, "draw")
    await repo.record_match(session, "c4", 4, 3, "draw")
    await session.commit()
    rows = await repo.leaderboard(session)
    assert [r[2] for r in rows] == [2, 2, 1, 1]
    assert [r[0] for r in rows] == ["Аня", "Боря", "Вика", "Гоша"]


async def test_limit(session, players):
    for a, b in [(1, 2), (3, 4), (1, 3)]:
        await repo.record_match(session, "c4", a, b, "win1")
    await session.commit()
    top = await repo.leaderboard(session, limit=2)
    assert [r[0] for r in top] == ["Аня", "Вика"]
