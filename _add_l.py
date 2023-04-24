operator.lt
[limit_id for dictionary in [V[limit_id] for limit_id in limit_ids] for limit_id in dictionary]

BASE_DIR = Path(__file__).resolve().parent.parent


def ping_is_alive(model, name):
    # model(name=name, last_ping=now()).save()  ne marche pas return 0 pas input dans la db
    model.insert(name=name, last_ping=now()).execute()  # ok