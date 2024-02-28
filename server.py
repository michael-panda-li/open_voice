# 导入flask和pytest模块
from flask import Flask, request, jsonify, send_file
import os, json
import torch
from openvoice import se_extractor
from openvoice.api import BaseSpeakerTTS, ToneColorConverter

# 创建一个flask应用
app = Flask(__name__)

# 定义一个数据结构，是一个列表，每个元素是一个字典，包含id和text两个键
data = [{'id': 1, 'text': 'hello'}]

# 定义一个增加数据的函数，接受一个json格式的请求，返回一个json格式的响应
@app.route('/add', methods=['POST'])
def add_data():
    # 获取请求中的json数据
    json_data = request.get_json()
    # 检查数据是否合法，必须包含id和text两个键，且id不能重复
    if 'id' not in json_data or 'text' not in json_data:
        return jsonify({'error': 'Invalid data, must contain id and text keys'})
    if any(d['id'] == json_data['id'] for d in data):
        return jsonify({'error': 'Duplicate id, id must be unique'})
    # 将数据添加到列表中
    data.append(json_data)
    # 返回成功的响应，包含添加的数据
    return jsonify({'success': 'Data added', 'data': json_data})

@app.route('/text', methods=['POST'])
def text_api():
    # 获取请求中的JSON数据
    data = request.get_json()
    # 获取参数content的值
    content = data.get('content')
    # 返回结果给客户端
    return jsonify({'data': content})

# 定义一个删除数据的函数，接受一个id作为参数，返回一个json格式的响应
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_data(id):
    # 检查id是否存在于列表中
    if not any(d['id'] == id for d in data):
        return jsonify({'error': 'Invalid id, id does not exist'})
    # 从列表中删除对应的数据
    data.remove(next(d for d in data if d['id'] == id))
    # 返回成功的响应，包含删除的id
    return jsonify({'success': 'Data deleted', 'id': id})

# 定义一个修改数据的函数，接受一个id作为参数，和一个json格式的请求，返回一个json格式的响应
@app.route('/update/<int:id>', methods=['PUT'])
def update_data(id):
    # 获取请求中的json数据
    json_data = request.get_json()
    # 检查数据是否合法，必须包含text键
    if 'text' not in json_data:
        return jsonify({'error': 'Invalid data, must contain text key'})
    # 检查id是否存在于列表中
    if not any(d['id'] == id for d in data):
        return jsonify({'error': 'Invalid id, id does not exist'})
    # 从列表中找到对应的数据，并修改其text值
    data_item = next(d for d in data if d['id'] == id)
    data_item['text'] = json_data['text']
    # 返回成功的响应，包含修改的数据
    return jsonify({'success': 'Data updated', 'data': data_item})

# 定义一个查询数据的函数，接受一个id作为参数，返回一个json格式的响应
@app.route('/query/<int:id>', methods=['GET'])
def query_data(id):
    # 检查id是否存在于列表中
    if not any(d['id'] == id for d in data):
        return jsonify({'error': 'Invalid id, id does not exist'})
    # 从列表中找到对应的数据，并返回
    data_item = next(d for d in data if d['id'] == id)
    return jsonify({'success': 'Data found', 'data': data_item})

@app.route('/getfile', methods=['POST'])
def getfile_api():
    # 获取请求中的JSON数据
    data = request.get_json()
    # 获取参数content的值
    sentence = data.get('content')
    # 返回结果给客户端
    # 根据获得的句子生成语音文件
    try:
        gen_audio(sentence)
    except Exception as e:
        return str(e)
    # 返回文件
    print('音频发送中')
    filename = "output_en_default.wav"
    root_path  = os.path.dirname(os.path.realpath(__file__))
    file_path = root_path.replace('\\', '/') + "/outputs/" + filename
    print(file_path)
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e)


# 定义一个路由，接收文件名作为参数
@app.route("/getfile/<sentence>")
def getfile(sentence):
    # 根据获得的句子生成语音文件
    try:
        gen_audio(sentence)
    except Exception as e:
        return str(e)
    # 返回文件
    print('音频发送中')
    filename = "output_en_default.wav"
    root_path  = os.path.dirname(os.path.realpath(__file__))
    file_path = root_path.replace('\\', '/') + "/outputs/" + filename
    print(file_path)
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e)
    
def init_gen_audio():
    # 初始化
    ckpt_base = 'checkpoints/base_speakers/EN'
    ckpt_converter = 'checkpoints/converter'
    device="cuda:0" if torch.cuda.is_available() else "cpu"
    output_dir = 'outputs'

    base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)
    base_speaker_tts.load_ckpt(f'{ckpt_base}/checkpoint.pth')

    tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
    tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

    os.makedirs(output_dir, exist_ok=True)

    source_se = torch.load(f'{ckpt_base}/en_default_se.pth').to(device)

    reference_speaker = 'resources/male_voice.mp3'
    target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, target_dir='processed', vad=True)
    return base_speaker_tts, tone_color_converter, source_se, target_se
    

def gen_audio(sentence):
    output_dir = 'outputs'
    save_path = f'{output_dir}/output_en_default.wav'
    base_speaker_tts, tone_color_converter, source_se, target_se = init_gen_audio()
    # Run the base speaker tts
    text = sentence
    src_path = f'{output_dir}/tmp.wav'
    base_speaker_tts.tts(text, src_path, speaker='friendly', language='English', speed=1.0)

    # Run the tone color converter
    encode_message = "@MyShell"
    tone_color_converter.convert(
        audio_src_path=src_path, 
        src_se=source_se, 
        tgt_se=target_se, 
        output_path=save_path,
        message=encode_message)
    print('音频已生成')
    
if __name__ == '__main__':
   app.run(port=5000)