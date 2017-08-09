from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from utils.constants import Game


class Item(Model):
    __table_name__ = 'item'

    id = columns.UUID(primary_key=True)
    market_name = columns.Text(index=True)
    avg_7_days = columns.Float()
    avg_7_days_raw = columns.Float()
    avg_30_days = columns.Float()
    avg_30_days_raw = columns.Float()
    current_price = columns.Float()
    num_sales_24hrs = columns.Integer()
    num_sales_7days = columns.Integer()
    num_sales_30days = columns.Integer()
    avg_daily_volume = columns.Float()
    image_url = columns.Text()
    description = columns.Text()
    rarity = columns.Text()
    game = columns.Integer(discriminator_column=True)


class ItemCsgo(Item):
    __discriminator_value__ = Game.CSGO

    exterior = columns.Text()


class ItemDota2(Item):
    __discriminator_value__ = Game.DOTA2

    used_by = columns.Text()