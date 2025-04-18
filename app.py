from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename
import jiejuefangan
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'doc', 'docx', 'ppt', 'pptx'}

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 检查文件扩展名是否合法
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    """网站首页"""
    return render_template('index.html')

@app.route('/plan-evaluation')
def plan_evaluation():
    """商业计划书评估页面"""
    return render_template('plan_evaluation.html')

@app.route('/ppt-guide')
def ppt_guide():
    """商业演示PPT指导页面"""
    return render_template('ppt_guide.html')

@app.route('/virtual-coach')
def virtual_coach():
    """虚拟路演教练页面"""
    return render_template('virtual_coach.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message', '')
    file_data = request.json.get('file_data', None)
    
    if not user_message and not file_data:
        return jsonify({'error': '消息不能为空'}), 400
    
    # 如果包含文件数据和评估需求，进行文件评估
    if file_data and "评估" in user_message:
        try:
            # 从base64字符串中提取文件内容和文件名
            import base64
            file_content = base64.b64decode(file_data['content'])
            filename = secure_filename(file_data['name'])
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            # 检查文件类型
            if not allowed_file(filename):
                return jsonify({'reply': '不支持的文件类型，请上传TXT、PDF、DOC或DOCX格式的文件。'})
            
            # 提取提示词
            prompt = user_message
            
            try:
                # 使用jiejuefangan模块进行评估
                result = jiejuefangan.evaluate_plan(filepath, prompt)
                
                # 将评估结果转换为易读的格式
                response = f"评估报告：\n\n"
                response += f"总体评分: {result['总体评分']}分\n"
                response += f"创新性: {result['创新性']}分\n"
                response += f"可行性: {result['可行性']}分\n"
                response += f"市场潜力: {result['市场潜力']}分\n"
                response += f"团队能力: {result['团队能力']}分\n\n"
                response += result['详细评价']
                
                return jsonify({'reply': response, 'is_evaluation': True})
            except Exception as e:
                return jsonify({'reply': f'评估过程出错: {str(e)}'})
            finally:
                # 评估后删除上传的文件
                if os.path.exists(filepath):
                    os.remove(filepath)
        except Exception as e:
            return jsonify({'reply': f'处理文件时出错: {str(e)}'})
    
    # 根据当前页面提供不同的回复
    page_type = request.json.get('page_type', 'plan')
    
    if page_type == 'ppt':
        # PPT指导的回复逻辑
        response = "您好！我是智汇创翼PPT指导助手。我可以帮您优化商业演示PPT的内容和设计。"
        
        if "模板" in user_message:
            response = "我们提供多种专业的商业演示PPT模板，您可以根据不同场景选择合适的模板。请问您需要哪种类型的模板？"
        elif "设计" in user_message:
            response = "优秀的PPT设计应遵循简洁明了、重点突出的原则。建议使用统一的配色方案，每页控制在3-5个要点，使用高质量的图表和图片来支持您的论点。"
        elif "结构" in user_message:
            response = "商业演示PPT的标准结构通常包括：1)封面; 2)问题/痛点; 3)解决方案; 4)产品/服务介绍; 5)市场分析; 6)商业模式; 7)团队介绍; 8)财务预测; 9)融资计划; 10)联系方式。"
        
    elif page_type == 'virtual-coach':
        # 虚拟路演教练的回复逻辑
        response = "您好！我是智汇创翼虚拟路演教练。我可以帮您准备投资人路演，提供演讲技巧和反馈。"
        
        if "技巧" in user_message:
            response = "成功的路演技巧包括：1)控制时间在10分钟内; 2)使用故事化叙事; 3)清晰表达核心价值主张; 4)展示真实数据和成果; 5)保持自信但不傲慢; 6)准备充分的问答环节。"
        elif "练习" in user_message:
            response = "您可以上传您的路演视频或音频，我将为您提供详细的反馈和改进建议。或者您可以告诉我您的路演内容，我们可以进行模拟问答练习。"
        elif "问题" in user_message:
            response = "投资人常见问题包括：1)你的市场规模有多大？2)竞争优势是什么？3)如何获客及获客成本？4)商业模式如何盈利？5)资金将如何使用？6)团队核心成员背景？准备好这些问题的简短有力回答非常重要。"
    
    else:  # 默认为计划书评估
        # 普通聊天回复逻辑
        response = "您好！我是智汇创翼商业计划书评估助手。您可以直接在聊天框中发送消息和上传文件，我将为您提供专业评估。"
        
        if "评估" in user_message or "分析" in user_message:
            response = "请点击上传按钮，选择您的商业计划书文档，然后告诉我您想重点评估哪些方面，我会为您提供详细的评估报告。"
        elif "你好" in user_message or "您好" in user_message:
            response = "您好！我是智汇创翼商业计划书评估助手，很高兴为您服务。您可以直接上传商业计划书，我将帮您分析其优势、不足，并提供改进建议。"
        elif "功能" in user_message or "能做什么" in user_message:
            response = "我可以帮您评估商业计划书的创新性、可行性、市场潜力和团队能力等方面，并提供专业的改进建议。只需上传文件并提出您的评估需求即可。"
        elif "如何" in user_message and "使用" in user_message:
            response = "使用方法很简单：\n1. 在聊天框右侧点击上传图标\n2. 选择您的商业计划书文件（支持PDF、DOC、DOCX和TXT格式）\n3. 输入您的评估需求\n4. 发送消息即可获得评估报告"
    
    return jsonify({
        'reply': response
    })

@app.route('/evaluate', methods=['POST'])
def evaluate():
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    prompt = request.form.get('prompt', '')
    if not prompt:
        return jsonify({'error': '提示词不能为空'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # 使用jiejuefangan模块进行评估
            result = jiejuefangan.evaluate_plan(filepath, prompt)
            return jsonify({'result': result})
        except Exception as e:
            return jsonify({'error': f'评估过程出错: {str(e)}'}), 500
        finally:
            # 评估后删除上传的文件
            if os.path.exists(filepath):
                os.remove(filepath)
    else:
        return jsonify({'error': '不支持的文件类型'}), 400

@app.route('/profile')
def profile():
    """用户个人中心页面"""
    # 这里可以添加用户认证逻辑
    # 假设我们有一些示例数据
    user_data = {
        'username': '林思影',
        'membership': '高级会员',
        'usage_stats': {
            'plan_evaluations': 15,
            'ppt_guides': 8,
            'coaching_sessions': 5
        },
        'usage_records': [
            {'date': '2025-4-18', 'type': '商业计划书评估', 'document': '创业项目计划书.pdf'},
            {'date': '2025-4-18', 'type': 'PPT指导', 'document': '融资路演演示.pptx'},
            {'date': '2025-4-20', 'type': '虚拟路演教练', 'document': '路演练习反馈.docx'}
        ]
    }
    return render_template('profile.html', user=user_data)

@app.route('/feedback')
def feedback():
    """用户反馈页面"""
    return render_template('feedback.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080) 