import importlib.util
import sys, os

IS_FIRSTTIME = sys.path[0] != "."

def assert_dep(name):
    assert importlib.util.find_spec(name), f"需要安装 {name}"


def login():
    import inquirer
    import demos.手机登录 as 手机登录, 二维码登录

    class 匿名登陆:
        @staticmethod
        def login(session):
            from pyncm.apis.login import LoginViaAnonymousAccount

            return LoginViaAnonymousAccount(session=session)

    methods = {"手机登录": 手机登录, "二维码登录": 二维码登录, "匿名登陆": 匿名登陆}
    assert methods[
        inquirer.prompt([inquirer.List("method", message="登陆方法", choices=methods)])[
            "method"
        ]
    ].login(session), "登录失败"

    print(
        "已登录",
        session.nickname,
        "用户 ID：",
        session.uid,
    )
    return True


assert_dep("pyncm")
assert_dep("inquirer")

from pyncm import Session
session = Session()

# Find pyncm from working directories first,
if IS_FIRSTTIME:
    import inquirer

    if inquirer.confirm("使用调试模式"):
        os.environ["PYNCM_DEBUG"] = "DEBUG"
    sys.path.insert(0, ".")
    from pyncm import __version__, __file__

    print(f"PyNCM {__version__}", __file__)
