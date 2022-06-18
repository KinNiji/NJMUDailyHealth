import json
import os

import dash
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import encrypt

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
]

app = dash.Dash(
    __name__,
    title="NJMUDailyHealth",
    update_title=None,
    external_stylesheets=external_stylesheets,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True
)

app.layout = html.Div(
    children=[
        html.H1("自动健康日报打卡", className="display-3 mb-4"),
        html.P("您还在为每日打卡的繁琐而困扰吗？", className="lead"),
        html.P("只需5分钟，上传一些必要的信息和少量必要的操作后，打卡就能每日定时自动完成！", className="lead"),
        html.Hr(className="my-3"),
        html.H4("问题1：上传我的信息安全吗？"),
        html.P("您的信息将通过AES加密保存与服务器，每个人随机生成独立的秘钥。"
               "但由于爬虫登录网上办事大厅时必须使用您的用户名和密码，使用了可逆加密，只能以管理员的人格担保不会使用于任何其它用途。"
               "若您存在顾虑请勿使用本自动程序。", className="lead"),
        html.H4("问题2：自动打卡的原理是什么？"),
        html.P("根据您提供的信息，会有爬虫模拟您的操作，登录网上办事大厅，进入健康打卡网页端进行打卡。"
               "打卡成功后将通过qq消息通知您。", className="lead"),
        html.H4("问题3：自动打卡有什么潜在问题？"),
        html.P("网页端填报的位置信息会显示江苏省南京市，若您在其它省市需要在手机端填报重新保存一下位置信息，目前无法解决。", className="lead"),
        html.H4("问题4：为什么qq消息提示打卡失败？"),
        html.P("有可能是您提交的信息有误或填报内容发生了更改，请检查网页端填报内容并重新提交您的信息。", className="lead"),
        html.Hr(className="my-3"),
        html.H2("第一步：填写信息。"),
        html.P("您的信息将被保存在服务器上，不会被用于任何其它的用途。", className="lead"),
        dbc.Label("学号"),
        dbc.Input(placeholder="登录网上办事大厅所用的学号", type="text", id='userId', className='mb-3'),
        dbc.Label("密码"),
        dbc.Input(placeholder="登录网上办事大厅所用的密码", type="password", id='password', className='mb-3'),
        dbc.Label("qq号"),
        dbc.Input(placeholder="用于接收打卡结果的qq号,请在第三步使用该qq号加群。", type="text", id='qqId', className='mb-3'),
        dbc.Label("填报内容"),
        dbc.Alert("请根据您的自身情况修改下方内容。", color="warning"),
        dbc.Textarea(value="""{
    "今日所在省份": {"default": 0, "option": "江苏省"},
    "今日所在城市": {"default": 0, "option": "南京市"},
    "今日所在区域": {"default": 0, "option": "江宁区"},
    "今日所在位置": {"default": 0, "option": "江宁校区"},
    "今日情况": {"default": 0, "option": "校内学习"},
    "今日疫苗接种情况": {"default": 1, "option": "已完成两针接种"},
    "今日身体状况": {"default": 0, "option": "无发热等新冠十个症状"},
    "今日健康码": {"default": 0, "option": "绿码"},
    "异常情况接触史（多选）": {"default": 0, "option": ["无"]},
    "今日隔离情况": {"default": 0, "option": "未隔离"},
    "今日滞留情况": {"default": 0, "option": "未滞留"},
    "家庭住址（多选）": {"default": 1, "option": ["南京以外江苏省内"]},
    "共同生活人员相关疫情防控信息": {"default": 0 , "option": "无异常信息"},
    "当天是否住校": {"default":  0, "option": "是"},
    "当天居住校区": {"default":  0, "option": "江宁校区学生宿舍"},
    "当天居住地点": {"default":  0, "option": "08幢学生宿舍楼"},
    "今日是否存在出差计划": {"default":  0, "option": "否"}
}""", rows=16, id='form_content'),
        dbc.FormText("注意该项内容与网页端填报内容一一对应，输入为一个字典，键为标签，值为字典"
                     "（default表示是否有默认值，0无1有；option表示标签对应的选项，单选为字符串，多选为字符串列表）", className='mb-3'),
        html.P(dbc.Button("提交", color="primary", outline=True, id='commit-button'), className="lead d-grid"),
        html.H2("第二步：加入打卡结果通知群", className='mt-5'),
        html.P("群号：661553440，每日定时早7打卡，接收打卡结果信息。"
               "也可以通过指令打卡：在群内输入'/健康打卡 <你的学号>'", className="lead"),
        dbc.Toast(header="提交结果", icon="danger", is_open=False, dismissable=True, id='commit-output',
                  style={"position": "fixed", "top": 66, "right": 10, "width": 350}),
    ],
    style={
        "width": "50%",
        "min-width": "320px",
        "margin": "4rem auto"
    }
)


@app.callback(
    [Output("commit-output", "is_open"),
     Output('commit-output', 'children')],
    [Input('commit-button', 'n_clicks')],
    [State('userId', 'value'),
     State('password', 'value'),
     State('qqId', 'value'),
     State('form_content', 'value')],
    prevent_initial_call=True
)
def _(n, user_id, password, qq_id, form_content):
    config = {
        "userId": user_id,
        "password": password,
        "qqId": qq_id,
        "form_content": form_content.replace('\n', '').replace(' ', '')
    }
    if n:
        if user_id and password and qq_id and form_content:
            encrypt.encrypt(
                json.dumps(config, ensure_ascii=False),
                f'{os.getcwd()}/bot/plugins/daily_health/config/{user_id}.bin')
            return True, "信息提交成功！"
        else:
            return True, "以上的信息不能为空！"
    return False, None


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=80, debug=False)
