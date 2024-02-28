# 导入pytest模块
import pytest
# 导入flask服务器的代码
from server import app, data

# 定义一个测试增加数据的函数，使用pytest模块
def test_add_data():
    # 创建一个测试客户端
    client = app.test_client()
    # 定义一个测试数据，包含id和text两个键
    test_data = {'id': 2, 'text': 'world'}
    # 发送一个post请求，传入测试数据，获取响应
    response = client.post('/add', json=test_data)
    # 检查响应的状态码是否为200，表示成功
    assert response.status_code == 200
    # 检查响应的数据是否包含成功的信息，和添加的数据
    assert response.json == {'success': 'Data added', 'data': test_data}
    # 检查列表中是否包含测试数据
    assert test_data in data

# 定义一个测试删除数据的函数，使用pytest模块
def test_delete_data():
    # 创建一个测试客户端
    client = app.test_client()
    # 定义一个测试id，为1
    test_id = 1
    # 发送一个delete请求，传入测试id，获取响应
    response = client.delete(f'/delete/{test_id}')
    # 检查响应的状态码是否为200，表示成功
    assert response.status_code == 200
    # 检查响应的数据是否包含成功的信息，和删除的id
    assert response.json == {'success': 'Data deleted', 'id': test_id}
    # 检查列表中是否不包含测试id对应的数据
    assert not any(d['id'] == test_id for d in data)

# 定义一个测试修改数据的函数，使用pytest模块
def test_update_data():
    # 创建一个测试客户端
    client = app.test_client()
    # 定义一个测试id，为2
    test_id = 2
    # 定义一个测试数据，包含text键，值为'hello world'
    test_data = {'text': 'hello world'}
    # 发送一个put请求，传入测试id和测试数据，获取响应
    response = client.put(f'/update/{test_id}', json=test_data)
    # 检查响应的状态码是否为200，表示成功
    assert response.status_code == 200
    # 检查响应的数据是否包含成功的信息，和修改的数据
    assert response.json == {'success': 'Data updated', 'data': {'id': test_id, 'text': test_data['text']}}
    # 检查列表中是否包含测试id对应的数据，且其text值为'hello world'
    assert any(d['id'] == test_id and d['text'] == 'hello world' for d in data)

# 定义一个测试查询数据的函数，使用pytest模块
def test_query_data():
    # 创建一个测试客户端
    client = app.test_client()
    # 定义一个测试id，为2
    test_id = 2
    # 发送一个get请求，传入测试id，获取响应
    response = client.get(f'/query/{test_id}')
    # 检查响应的状态码是否为200，表示成功
    assert response.status_code == 200
    # 检查响应的数据是否包含成功的信息，和查询的数据
    assert response.json == {'success': 'Data found', 'data': {'id': test_id, 'text': 'hello world'}}
    # 检查列表中是否包含测试id对应的数据
    assert any(d['id'] == test_id for d in data)


# 定义测试函数
def test_text_api():
    # 要发送的JSON数据
    data = {'content': 'hellow word'}
    # 发送POST请求
    client = app.test_client()
    response = client.post('/text', json=data)
    # 获取响应中的JSON数据
    assert response.status_code == 200
    # 检查响应的数据是否包含成功的信息，和添加的数据
    assert response.json == {'data':'hellow word'}
