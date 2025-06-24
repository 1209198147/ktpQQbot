from deepseek.functool.func_tool import LLMTools, llmtool
from ktpApi.ktpApi import KeTangPaiAPI
from core.db.mysql import KTPDatabase, get_KTPdb
from ncatbot.utils.logger import get_log
import json

_log = get_log()

ktpTool = LLMTools()

db = get_KTPdb(r'D:\LLM\database_config.yaml')
def get_KeTangPaiAPI(user_id):
    result = db.read_user(user_id)
    if result is None:
        return "无法找到对应用户ID的信息，可能是没有绑定课堂派账号。"
    if result['token'] is not None:
        return KeTangPaiAPI(result['token'])
    else:
        api = KeTangPaiAPI()
        resp = api.login(result['ktp_username'], result['wang200435'])
        resp = resp.json()
        if resp.status_code==200 and resp.get("status", None) == 0:
            return f"[无法登入课堂派账号]{resp.get('message', '')}。"
        return api

@llmtool(tools=ktpTool)
def bind_ktp(user_id, ktp_username, ktp_password):
    '''
    绑定课堂派账号，将课堂派账号绑定和用户绑定
    user_id: 用户id
    ktp_username: 课堂派用户名
    ktp_password: 课堂派密码
    '''
    result = db.read_user(user_id)
    if result:
        return "你已经绑定过了"
    api = get_KeTangPaiAPI(user_id)
    resp = api.login(ktp_username, ktp_password).json()
    db.create_user(user_id, ktp_username, ktp_password, api.token)
    if api.token:
        return "绑定成功"
    return f"[绑定失败]{resp.get('message', '')}"

@llmtool(tools=ktpTool)
def get_user_info(user_id:str):
    '''
    获取用户信息，需要传入用户id
    user_id: 用户id
    '''
    api = get_KeTangPaiAPI(user_id)
    if type(api) == str:
        return api
    return json.dumps(api.get_user_info().json())

@llmtool(tools=ktpTool)
def get_semester_list(user_id:str):
    '''
    获取学期列表，需要传入用户id
    user_id: 用户id
    '''
    api = get_KeTangPaiAPI(user_id)
    if type(api) == str:
        return api
    return json.dumps(api.get_semester_list().json())

@llmtool(tools=ktpTool)
def get_semester_courses(semester:str, term:str, user_id:str):
    '''
    获取学期课程，需要传入用户id、学年和学期
    semester:学年段，例如"2023-2024"
    term:学期，例如"1"
    user_id:用户id
    '''
    api = get_KeTangPaiAPI(user_id)
    if type(api) == str:
        return api
    return json.dumps(api.get_semester_courses(semester, term).json())

@llmtool(tools=ktpTool)
def get_course_content(courseid:str, contenttype:int, user_id:str, page:int, limit:int):
    '''
    获取课程内容，需要传入用户id、学年和学期
    courseid: 课程ID，4-作业，5-话题，6-测试，
    contenttype: 内容类型
    user_id: 用户ID
    page: 当前页数
    limit: 每页大小
    '''
    api = get_KeTangPaiAPI(user_id)
    if type(api) == str:
        return api
    return json.dumps(api.get_course_content(courseid, contenttype, page=page, limit=limit).json())

@llmtool(tools=ktpTool)
def get_unfinished_tasks(user_id:str):
    """
    获取所有未完成的任务
    user_id: 用户id
    """
    api = get_KeTangPaiAPI(user_id)
    if type(api) == str:
        return api
    return json.dumps(api.get_unfinished_tasks())

if __name__ == '__main__':
    # print("注册的工具:")
    # for tool in ktpTool.tools:
    #     print(f"{tool}")
    #
    # print("\n函数映射:")
    # for name, func in ktpTool.functions.items():
    #     print(f"{name}: {func.__name__}")
    print(get_unfinished_tasks('1319507316'))