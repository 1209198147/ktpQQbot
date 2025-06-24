import time
import requests

class KeTangPaiAPI:
    BASE_URL = "https://openapiv5.ketangpai.com/"

    # API端点定义
    USER_API = {
        'login': 'UserApi/login',
        'user_info': 'UserApi/getUserBasinInfo'
    }

    COURSE_API = {
        'semester_list': 'CourseApi/semesterList',
        'semester_courses': 'CourseApi/semesterCourseList',
        'course_content': 'FutureV2/CourseMeans/getCourseContent'
    }

    def __init__(self, token=None):
        """
        初始化API客户端
        :param token: 可选的身份验证令牌
        """
        self.token = token

    @staticmethod
    def _get_timestamp():
        """
        获取当前时间戳（毫秒）
        """
        return int(round(time.time() * 1000))

    def _get_headers(self, token=None):
        """
        生成请求头
        :param token: 如果提供则覆盖实例token
        """
        token = token or self.token
        return {
            'Token': token or '',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

    def login(self, username, password, remember=1):
        """
        用户登录
        :param username: 用户名/邮箱
        :param password: 密码
        :param remember: 是否记住登录状态
        :return: 响应对象
        """
        payload = {
            "email": username,
            "password": password,
            "remember": remember,
            "code": "",
            "mobile": "",
            "type": "login",
            "reqtimestamp": self._get_timestamp()
        }
        try:
            resp = requests.post(
                self.BASE_URL+self.USER_API['login'],
                headers=self._get_headers(''),  # 登录时不需要token
                json=payload
            )
            # 如果登录成功，自动更新实例token
            if resp.status_code == 200:
                if resp.json().get("status", None) == 0:
                    print("登入失败："+resp.json().get("message", ""))
                self.token = resp.json().get('data', {}).get('token')
            return resp
        except Exception as e:
            print(f"登录失败: {e}")
            return None

    def get_user_info(self, token=None):
        """
        获取用户基础信息
        :param token: 可选，覆盖默认token
        :return: 响应对象
        """
        payload = {'reqtimestamp': self._get_timestamp()}
        try:
            return requests.post(
                self.BASE_URL+self.USER_API['user_info'],
                headers=self._get_headers(token),
                json=payload
            )
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None

    def get_semester_list(self, token=None):
        """
        获取学期列表
        :param token: 可选，覆盖默认token
        :return: 响应对象
        """
        payload = {
            'isstudy': "1",
            'search': "",
            'reqtimestamp': self._get_timestamp()
        }
        try:
            return requests.post(
                self.BASE_URL+self.COURSE_API['semester_list'],
                headers=self._get_headers(token),
                json=payload
            )
        except Exception as e:
            print(f"获取学期列表失败: {e}")
            return None

    def get_semester_courses(self, semester, term, token=None):
        """
        获取学期课程列表
        :param semester: 学期
        :param term: 学期代码
        :param token: 可选，覆盖默认token
        :return: 响应对象
        """
        payload = {
            'isstudy': "1",
            'search': "",
            'semester': semester,
            'term': term,
            'reqtimestamp': self._get_timestamp()
        }
        try:
            return requests.post(
                self.BASE_URL+self.COURSE_API['semester_courses'],
                headers=self._get_headers(token),
                json=payload
            )
        except Exception as e:
            print(f"获取学期课程失败: {e}")
            return None

    def get_course_content(self, courseid, contenttype, token=None, **kwargs):
        """
        获取课程内容
        :param courseid: 课程ID
        :param contenttype: 内容类型 (4-作业, 6-测试)
        :param token: 可选，覆盖默认token
        :param kwargs: 其他可选参数
            dirid=0,
            courserole=0,
            page=1,
            limit=50,
            desc=3
        :return: 响应对象
        """
        payload = {
            "courseid": courseid,
            "contenttype": contenttype,
            "dirid": kwargs.get('dirid', 0),
            "lessonlink": [],
            "sort": [],
            "page": kwargs.get('page', 1),
            "limit": kwargs.get('limit', 50),
            "desc": kwargs.get('desc', 3),
            "courserole": kwargs.get('courserole', 0),
            "vtr_type": "",
            "reqtimestamp": self._get_timestamp()
        }
        try:
            return requests.post(
                self.BASE_URL+self.COURSE_API['course_content'],
                headers=self._get_headers(token),
                json=payload
            )
        except Exception as e:
            print(f"获取课程内容失败: {e}")
            return None

    def get_unfinished_tasks(self, token=None):
        """
        获取所有未完成的任务
        :param token: 可选，覆盖默认token
        :return: 任务列表，或None
        """
        tasks = []

        # 获取学期信息
        semester_resp = self.get_semester_list(token)
        if not semester_resp or semester_resp.status_code != 200:
            return None
        semester_data = semester_resp.json().get('data', {})
        if not semester_data.get('semester'):
            return None

        # 获取当前学期
        current_semester = semester_data['semester'][0]

        # 获取学期课程
        courses_resp = self.get_semester_courses(
            current_semester['semester'],
            current_semester['term'],
            token
        )
        if not courses_resp or courses_resp.status_code != 200:
            return None

        courses = courses_resp.json().get('data', [])

        # 遍历课程获取未完成任务
        for course in courses:
            tasks_resp = self.get_course_content(
                courseid=course['id'],
                contenttype=4,  # 4表示作业
                token=token
            )

            if not tasks_resp or tasks_resp.status_code != 200:
                continue

            task_data = tasks_resp.json().get('data', {})
            task_list = task_data.get('list', [])

            for task in task_list:
                if task.get('mstatus') == 0:  # 0表示未完成
                    task['coursename'] = course['coursename']
                    tasks.append(task)

        return tasks


# 使用示例
if __name__ == "__main__":
    # 创建API客户端
    ktp_api = KeTangPaiAPI()

    # 用户登录
    login_resp = ktp_api.login("13906052451", "ktp132546")
    if login_resp and login_resp.status_code == 200:
        print("登录成功!")

        # 获取用户信息
        user_info = ktp_api.get_user_info()
        if user_info:
            print(f"用户信息: {user_info.json()}")

        # 获取未完成任务
        unfinished_tasks = ktp_api.get_unfinished_tasks()
        print(f"未完成任务数: {len(unfinished_tasks)}")
        for task in unfinished_tasks:
            print(f"课程: {task['coursename']}, 任务: {task['title']}")
    else:
        print("登录失败!")