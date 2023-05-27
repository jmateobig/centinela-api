from api.api_v1.database.connection import query_execute_app
from sqlalchemy import text

def get_user(uuid):
    query =query = f'''
    SELECT a.id as user_id, c.name
	FROM public.main_user as a
	inner join public.main_user_groups as b on a.id=b.user_id
	inner join public.auth_group as c on b.group_id=c.id
	where a.uuid='{uuid}'
	order by c.id
	limit 1;
    '''
    result = query_execute_app(text(query))
    row = result.fetchone()
    return row if row is not None else None