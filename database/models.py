"""
GrowLog - Models (Banco de Dados)
Usa Peewee ORM com SQLite local.
"""

import datetime
from peewee import (
    SqliteDatabase, Model, CharField, DateField,
    FloatField, IntegerField, TextField, BooleanField,
    ForeignKeyField
)

db = SqliteDatabase(None)  # Inicializado depois com o caminho correto


class BaseModel(Model):
    class Meta:
        database = db


class Plant(BaseModel):
    """Representa uma planta no cultivo."""
    name             = CharField()
    strain           = CharField(null=True)
    environment_type = CharField(default='indoor')   # indoor / outdoor
    grow_medium      = CharField(default='solo')     # solo / hidro / coco
    stage            = CharField(default='germinacao')
    planted_on       = DateField(default=datetime.date.today)
    notes            = TextField(null=True)

    # Últimos valores registrados (cache para o dashboard)
    last_watered     = DateField(null=True)
    last_fertilized  = DateField(null=True)
    current_ph       = FloatField(null=True)
    current_ec       = FloatField(null=True)

    class Meta:
        table_name = 'plants'

    def days_since_planted(self):
        return (datetime.date.today() - self.planted_on).days

    def days_since_watered(self):
        if not self.last_watered:
            return None
        return (datetime.date.today() - self.last_watered).days

    def stage_label(self):
        labels = {
            'germinacao': 'Germinação',
            'seedling':   'Seedling',
            'vegetativa': 'Vegetativa',
            'floracao':   'Floração',
            'colheita':   'Colheita',
        }
        return labels.get(self.stage, self.stage.capitalize())


class Log(BaseModel):
    """
    Registro de qualquer evento: rega, nutrição, anotação, troca de fase.
    """
    LOG_TYPES = ['rega', 'nutricao', 'nota', 'fase', 'outro']

    plant        = ForeignKeyField(Plant, backref='logs', on_delete='CASCADE')
    log_type     = CharField()          # rega / nutricao / nota / fase / outro
    date         = DateField(default=datetime.date.today)
    summary      = CharField(null=True) # linha resumida exibida no histórico

    # Rega
    water_amount = FloatField(null=True)   # litros
    ph           = FloatField(null=True)
    ec           = FloatField(null=True)   # mS/cm
    runoff_ph    = FloatField(null=True)

    # Nutrição
    product      = CharField(null=True)
    dose         = FloatField(null=True)   # ml/L
    ph_after     = FloatField(null=True)

    # Nota livre
    content      = TextField(null=True)

    class Meta:
        table_name = 'logs'
        order_by   = ['-date']


class Task(BaseModel):
    """
    Tarefas agendadas — aparecem no calendário.
    """
    plant     = ForeignKeyField(Plant, backref='tasks', on_delete='CASCADE')
    title     = CharField()
    due_date  = DateField()
    completed = BooleanField(default=False)
    notes     = TextField(null=True)

    class Meta:
        table_name = 'tasks'


# ─── Inicialização ────────────────────────────────────────────────────────────

def init_db(path: str = 'growlog.db'):
    db.init(path)
    db.connect(reuse_if_open=True)
    db.create_tables([Plant, Log, Task], safe=True)
