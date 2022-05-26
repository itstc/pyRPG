
def attackEffect(player, value):
    player.stats.ad += value 

def speedEffect(player, value):
    player.stats.maxcd = max(10, player.stats.maxcd - value)

def maxHPEffect(player, value):
    player.stats.maxHP += value

def hpEffect(player, value):
    player.stats.hp = min(player.stats.maxHP, player.stats.hp + value)

def defenceEffect(player, value):
    player.stats.defence += value

ITEM_EFFECT_MAP = {
    "attack": attackEffect,
    "speed": speedEffect,
    "maxHP": maxHPEffect,
    "hp": hpEffect,
    "defence": defenceEffect
}
