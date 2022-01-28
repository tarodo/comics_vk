# xkcd's comics VK bot
Service to post random comics to your group at [vk.com](https://vk.com/feed).

## Install
Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```
## Env Settings
Create `.env` from `.env.Example`
1. VK_APP_ID - str, application id of your bot [VK apps](https://vk.com/apps?act=manage)
2. VK_APP_TOKEN - str, token of your app [Implicit Flow](https://vk.com/dev/implicit_flow_user). Add `photos, groups, wall, offline` scopes. 
Example `https://oauth.vk.com/authorize?client_id=1&display=page&scope=photos,groups,wall,offline&response_type=token&v=5.131&state=123456`
3. VK_GROUP_ID - str, id of your group [ID finder](https://regvk.com/id/)
## Start
```
python main.py
```