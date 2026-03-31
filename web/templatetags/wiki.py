from django import template
from web import models

register = template.Library()


@register.inclusion_tag('inclusion/all_catalog.html')
def all_catalog(request):
    """构造内存引用组装树"""

    catalog_tree = []
    big_dict = {}
    # 查出所有数据(可迭代字典序列) ——> [{'id':1, 'title':xxx, 'parent_id':3},{}]
    wikis = models.Wiki.objects.filter(project=request.tracer.project).values('id', 'title', 'parent_id')

    # 遍历wikis,将所有数据加入big_dict中
    for item in wikis:
        big_dict[item['id']] = {
            'id':item['id'],
            'title':item['title'],
            'parent_id':item['parent_id'],
            'children':[]
        }

    # 遍历big_dict,将所有子节点与父节点挂钩,
    for key, value in big_dict.items():
        # 如果这个wiki有parent
        if value['parent_id']:
            # 在这个big_dict中找到这个wiki的父亲
            papa = big_dict[value['parent_id']]
            # 直接把这个wiki加入父亲的children中
            papa['children'].append(value)
        else:
            catalog_tree.append(value)

    return {'request':request,'catalog_tree':catalog_tree}


"""
big_dict构造结果：
{
    1:{
        id:1
        title:xxx,
        parent_id:id,
        children:[
            {'id': 2, 'title': '后端规范', 'parent_id': 1, 'children': []},
            {'id': 3, 'title': '后端规范', 'parent_id': 1, 'children': []}
        ]
    }
}

列表、字典、元组等里面的元素都是：<font color="red">指向它们的内存地址，进行值的引用</font>，而非实体拷贝：
    当2的children中添加了东西，1的children中的2的children也有这个东西，因为1的children中的2是指向2的内存地址，而非重新拷贝了一份
"""
