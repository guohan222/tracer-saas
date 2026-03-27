import base

from web import models

def run():
    exist = models.Product.objects.filter(category=1, name='个人免费版').exists()
    if not exist:
        models.Product.objects.create(
            category=1,
            name='个人免费版',
            money=0,
            max_project=3,
            max_member=2,
            max_storage=20,
            max_send=5
        )

if __name__ == '__main__':
    run()