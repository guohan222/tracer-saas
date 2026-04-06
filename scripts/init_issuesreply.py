import base

from web import models


models.IssuesReply.objects.create(
    reply_type=1,
    issues_id=1,
    creator_id=12,
    content='4asdfsad4',
    parent_id='2'
)
