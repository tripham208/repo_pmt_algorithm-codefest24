from lib.model.enum.gameobjects import MarryItem, AnotherItem


def match_step_spoil(num_step):
    step_values = {1: 400, 2: 200, 3: 100}
    return step_values.get(num_step, 50)


def match_spoil(item):
    spoil_values = {
        MarryItem.RICE.value: 50,
        MarryItem.CAKE.value: 100,
        MarryItem.ELEPHANT.value: 300,
        MarryItem.ROOSTER.value: 150,
        MarryItem.HORSE.value: 200,
        AnotherItem.SPIRIT_STONE.value: 150,
    }
    return spoil_values.get(item, 0)


def match_need_item(item, need_item: list) -> int:
    if item in need_item:
        return 0
    else:
        need_item_values = {4: 50, 3: 100, 2: 200, 1: 400}
        return need_item_values.get(len(need_item), 0)
