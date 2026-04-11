import base
from web import models


def run():
    models.Product.objects.create(
        category=2,
        name='VIP',
        money=100,
        max_project=10,
        max_member=5,
        max_storage=30,
        max_send=10
    )

    models.Product.objects.create(
        category=2,
        name='SVIP',
        money=200,
        max_project=15,
        max_member=10,
        max_storage=50,
        max_send=15
    )

    models.Product.objects.create(
        category=2,
        name='ProVIP',
        money=300,
        max_project=20,
        max_member=25,
        max_storage=100,
        max_send=20
    )


if __name__ == '__main__':
    run()