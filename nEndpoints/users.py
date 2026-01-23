from client.https import NGET
from utils.utils import check_url_or_id

try:
    from mixed import find_parent_type
except ModuleNotFoundError:
    from nEndpoints.mixed import find_parent_type

BASE = "https://api.notion.com/v1/users"


def get_all_users(headers):
    return NGET(header=headers, url=f"{BASE}")['results']


def get_user(headers, user_id):
    user_id = check_url_or_id(user_id)
    return NGET(header=headers, url=f"{BASE}/{user_id}")


def get_bot_token(headers):
    return NGET(header=headers, url=f"{BASE}/me")


if __name__ == "__main__":
    from client.auth import NotionApiClient
    api = NotionApiClient(key="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")

    ################### GET ALL USERS EXAMPLE #######################################################
    # users = get_all_users(api.headers)
    # for user in users:
    #     print(user)
    ############################################################################################
    # person_id = '8711f079-8ae4-4748-89a7-d2daf31ff8fe'
    bot_id = '9816fe23-bc82-4025-aa43-76789960e89a'

    # print(get_user(api.headers, person_id), '\n\n')
    print(get_user(api.headers, bot_id), '\n\n')
    ################# TOKEN EXAMPLE #################################################
    # print(get_bot_token(api.headers))
