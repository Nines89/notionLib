################################### use Api's for cursor example ######################################
################################### CREATE A PAGE
from nEndpoints.databases import get_db_datasources
from nEndpoints.datasources import get_ds_templates, get_ds, filter_a_ds

from nEndpoints.pages import create_page

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
################################### CHECK DATASOURCE
print(filter_a_ds(api.headers, ds_id_, filt={}))

