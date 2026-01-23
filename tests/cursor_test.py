################################### use Api's for cursor example ######################################
################################### CREATE A PAGE
from nEndpoints.databases import get_db_datasources
from nEndpoints.datasources import get_ds_templates, get_ds, filter_a_ds

from nEndpoints.pages import create_page, get_page

from client.auth import NotionApiClient

api = NotionApiClient(key="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")

db_id_ = "https://www.notion.so/2c0b7a8f72948024a529f2a82e767024?v=2c0b7a8f72948174811f000c8c4bab20&source=copy_link"
ds_id_ = get_db_datasources(api.headers, db_id_)[1]['id']
tm_id = get_ds_templates(api.headers, ds_id_)['templates'][0]['id']
# props = {"FIRST FIELD": {
#     "title": [
#         {
#             "text": {
#                 "content": "name 4"
#             }
#         }
#     ]}
# }
# create_page(api.headers, ds_id_, properties=props, template_id=tm_id)
################################### CREATE MORE THEN 100 PAGES
# for i in range(58, 110):
#     props = {"FIRST FIELD": {
#         "title": [
#             {
#                 "text": {
#                     "content": f"name {i}"
#                 }
#             }
#         ]}
#     }
#     create_page(api.headers, ds_id_, properties=props, template_id=tm_id)
#     print(f'create page number {i}')
################################### RETRIEVE ALL PAGES FROM DATASOURCE

# all_items = []
# next_cursor = None
#
# while True:
#     try:
#         resp = filter_a_ds(api.headers, ds_id_, filt={'start_cursor': next_cursor} if next_cursor else {})
#     except Exception as e:
#         print(f"Errore API: {e}, ritento...")
#         continue
#
#     all_items.extend(resp["results"])
#     if not resp["has_more"]:
#         break
#     next_cursor = resp["next_cursor"]
#
# print(f"Totale elementi recuperati: {len(all_items)}")
#
#
#
# def paginate(fn):
#     def wrapper(*args, **kwargs):
#         all_results = []
#         start_cursor = None
#
#         while True:
#             if start_cursor:
#                 kwargs["start_cursor"] = start_cursor
#
#             resp = fn(*args, **kwargs)
#             all_results.extend(resp.get("results", []))
#
#             if not resp.get("has_more"):
#                 break
#
#             start_cursor = resp.get("next_cursor")
#
#         return all_results
#     return wrapper
#
# all_items = filter_a_ds(api.headers, ds_id_, filt={})
#
# for item in all_items:
#     print(item['properties']['FIRST FIELD']['title'][0]['text']['content'])
