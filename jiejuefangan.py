import requests
import json
import os

def evaluate_plan(file_path, prompt):
    """
    评估计划书并返回评估报告
    
    Args:
        file_path: 上传的计划书文件路径
        prompt: 用户输入的提示词
        
    Returns:
        dict: 评估报告
    """
    # 根据文件类型读取内容
    file_extension = file_path.split('.')[-1].lower()
    content = ""
    
    try:
        if file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif file_extension in ['doc', 'docx']:
            # 需要安装python-docx库: pip install python-docx
            try:
                import docx
                doc = docx.Document(file_path)
                content = '\n'.join([para.text for para in doc.paragraphs])
            except ImportError:
                return {
                    "总体评分": 0,
                    "创新性": 0,
                    "可行性": 0,
                    "市场潜力": 0,
                    "团队能力": 0,
                    "详细评价": "需要安装python-docx库来处理Word文档。请尝试安装: pip install python-docx"
                }
        elif file_extension == 'pdf':
            # 需要安装PyPDF2库: pip install PyPDF2
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(file_path)
                content = ""
                for page in reader.pages:
                    content += page.extract_text()
            except ImportError:
                return {
                    "总体评分": 0,
                    "创新性": 0,
                    "可行性": 0,
                    "市场潜力": 0,
                    "团队能力": 0,
                    "详细评价": "需要安装PyPDF2库来处理PDF文档。请尝试安装: pip install PyPDF2"
                }
        else:
            return {
                "总体评分": 0,
                "创新性": 0,
                "可行性": 0,
                "市场潜力": 0,
                "团队能力": 0,
                "详细评价": f"不支持的文件类型: {file_extension}"
            }
    except Exception as e:
        return {
            "总体评分": 0,
            "创新性": 0,
            "可行性": 0,
            "市场潜力": 0,
            "团队能力": 0,
            "详细评价": f"文件处理出错: {str(e)}"
        }
    
    # 如果内容为空或太短，可能不是有效的商业计划书
    if len(content) < 100:
        return {
            "总体评分": 0,
            "创新性": 0,
            "可行性": 0,
            "市场潜力": 0,
            "团队能力": 0,
            "详细评价": "文档内容太少，无法进行有效评估。请上传完整的商业计划书。"
        }
    
    # 尝试调用外部API进行评估
    try:
        api_result = call_external_api(content, prompt)
        if api_result:
            return api_result
    except Exception as e:
        print(f"API调用失败，使用内部逻辑进行评估: {str(e)}")
    
    # 如果API调用失败或者没有配置API，使用内部逻辑进行评估
    # 示例评估逻辑 - 实际应用中可以使用更复杂的分析
    innovation_score = analyze_innovation(content)
    feasibility_score = analyze_feasibility(content)
    market_score = analyze_market(content)
    team_score = analyze_team(content)
    
    # 计算总体评分
    overall_score = (innovation_score + feasibility_score + market_score + team_score) // 4
    
    # 生成详细评价
    detailed_review = generate_review(content, prompt, innovation_score, feasibility_score, market_score, team_score)
    
    return {
        "总体评分": overall_score,
        "创新性": innovation_score,
        "可行性": feasibility_score,
        "市场潜力": market_score,
        "团队能力": team_score,
        "详细评价": detailed_review
    }

def call_external_api(content, prompt):
    """
    调用外部API评估商业计划书
    
    Args:
        content: 商业计划书内容
        prompt: 用户输入的提示词
        
    Returns:
        dict: 评估结果，如果API调用失败则返回None
    """
    url = "https://wss.lke.cloud.tencent.com/v1/qbot/chat/sse"
    headers = {
        "Content-Type": "application/json"
    }
    
    # 构建发送给API的请求内容，将用户提示词和计划书内容结合
    api_prompt = f"{prompt}\n\n以下是需要评估的商业计划书内容:\n\n{content[:3000]}..."
    
    data = {
        "session_id": "a29bae68-cb1c-489d-8097-6be78f136acf",
        "bot_app_key": "qoStjmXYqhBMfTVtudTwWJGmtHUgjKzIwGTBUuRqCGXRHQJgPBxLlbvPYreZBGpbhahzHOtSHEgFVIunnQBjCbUdfepHUwtqzpctvIfhfGvIVhDzYsmwJOBGHxhTtAHa",
        "visitor_biz_id": "a29bae68-cb1c-489d-8097-6be78f136acf",
        "content": api_prompt,  # 使用用户的提示词
        "incremental": True,
        "streaming_throttle": 10,
        "visitor_labels": [],
        "custom_variables": {}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print("API请求成功！")
            content_text = response.content.decode('utf-8')
            # 拼接每个 event:reply 中的 content 字段
            events = content_text.split("\n\n")
            full_response = ""
            for event in events[1:]:
                if "event:reply" in event:
                    parts = event.split("data:")
                    if len(parts) > 1:
                        data_part = parts[1].strip()
                        data_json = json.loads(data_part)
                        if "payload" in data_json and "content" in data_json["payload"]:
                            content_part = data_json["payload"]["content"]
                            full_response += content_part
            
            # 简单解析API返回的结果，实际情况可能需要更复杂的处理
            # 这里假设API返回的是一个文本格式的评估报告
            # 我们需要将其转换为我们需要的格式
            
            # 临时方案：直接将API返回的内容作为详细评价
            return {
                "详细评价": full_response
            }
        else:
            print("API请求失败，状态码：", response.status_code)
            return None
    except Exception as e:
        print(f"API调用异常: {str(e)}")
        return None

def analyze_innovation(content):
    """分析创新性得分"""
    # 简单示例，实际应用中可以使用更复杂的算法
    innovation_keywords = ["创新", "新技术", "专利", "突破", "独特", "颠覆", "革新"]
    score = 60  # 基础分
    
    for keyword in innovation_keywords:
        if keyword in content:
            score += 5
    
    return min(score, 100)  # 最高100分

def analyze_feasibility(content):
    """分析可行性得分"""
    feasibility_keywords = ["实现", "成本", "资源", "技术路线", "计划", "方案", "步骤"]
    score = 60
    
    for keyword in feasibility_keywords:
        if keyword in content:
            score += 5
    
    return min(score, 100)

def analyze_market(content):
    """分析市场潜力得分"""
    market_keywords = ["市场", "需求", "用户", "客户", "规模", "增长", "竞争", "营销"]
    score = 60
    
    for keyword in market_keywords:
        if keyword in content:
            score += 4
    
    return min(score, 100)

def analyze_team(content):
    """分析团队能力得分"""
    team_keywords = ["团队", "经验", "专业", "人才", "背景", "能力", "合作"]
    score = 60
    
    for keyword in team_keywords:
        if keyword in content:
            score += 5
    
    return min(score, 100)

def generate_review(content, prompt, innovation_score, feasibility_score, market_score, team_score):
    """生成详细评价"""
    review = f"基于提示词「{prompt}」的评估:\n\n"
    
    # 1. 项目优势
    review += "1. 项目优势:\n"
    if innovation_score >= 80:
        review += "   - 项目具有较高的创新性，有潜力在市场中脱颖而出\n"
    if feasibility_score >= 80:
        review += "   - 项目实施方案完善，技术路线清晰\n"
    if market_score >= 80:
        review += "   - 目标市场定位准确，市场潜力巨大\n"
    if team_score >= 80:
        review += "   - 团队成员能力互补，执行力强\n"
    if innovation_score < 80 and feasibility_score < 80 and market_score < 80 and team_score < 80:
        review += "   - 项目整体结构完整，覆盖了商业计划的基本要素\n"
    
    # 2. 存在问题
    review += "\n2. 存在问题:\n"
    if innovation_score < 70:
        review += "   - 项目创新性不足，难以形成核心竞争力\n"
    if feasibility_score < 70:
        review += "   - 项目可行性分析不够充分，实施路径需要进一步明确\n"
    if market_score < 70:
        review += "   - 市场分析深度不够，未能充分论证市场需求和规模\n"
    if team_score < 70:
        review += "   - 团队能力展示不足，需要补充团队核心成员的专业背景\n"
    if innovation_score >= 70 and feasibility_score >= 70 and market_score >= 70 and team_score >= 70:
        review += "   - 项目各方面表现均衡，但缺乏突出亮点\n"
    
    # 3. 改进建议
    review += "\n3. 改进建议:\n"
    if innovation_score < 85:
        review += "   - 建议深入挖掘项目的创新点，强化技术壁垒或商业模式创新\n"
    if feasibility_score < 85:
        review += "   - 完善项目实施路径，增加里程碑计划和资源需求分析\n"
    if market_score < 85:
        review += "   - 补充市场调研数据，加强竞品分析和目标用户画像\n"
    if team_score < 85:
        review += "   - 突出团队核心成员的专业背景和行业经验\n"
    review += "   - 建议增加财务预测部分，包括投资回报周期和盈利模式分析\n"
    
    return review

url = "https://wss.lke.cloud.tencent.com/v1/qbot/chat/sse"
headers = {
    "Content-Type": "application/json"
}
data = {
    "session_id": "a29bae68-cb1c-489d-8097-6be78f136acf",
    "bot_app_key": "qoStjmXYqhBMfTVtudTwWJGmtHUgjKzIwGTBUuRqCGXRHQJgPBxLlbvPYreZBGpbhahzHOtSHEgFVIunnQBjCbUdfepHUwtqzpctvIfhfGvIVhDzYsmwJOBGHxhTtAHa",
    "visitor_biz_id": "a29bae68-cb1c-489d-8097-6be78f136acf",
    "content": "你知道武汉理工大学吗",
    "incremental": True,
    "streaming_throttle": 10,
    "visitor_labels": [],
    "custom_variables": {}

}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("请求成功！")
    try:
        content = response.content.decode('utf-8')
        # 拼接每个 event:reply 中的 content 字段
        events = content.split("\n\n")
        full_response = ""
        for event in events[1:]:
            if "event:reply" in event:
                parts = event.split("data:")
                if len(parts) > 1:
                    data_part = parts[1].strip()
                    data_json = json.loads(data_part)
                    if "payload" in data_json and "content" in data_json["payload"]:
                        content = data_json["payload"]["content"]
                        # 如果content里面的内容有两个换行符，那么删掉一个
                        # content = content.replace("\n\n", "\n")
                        full_response += content
        print("完整回复内容：", full_response)
    except UnicodeDecodeError:
        print("解码失败，可能是编码问题。")
    except json.JSONDecodeError as e:
        print(f"JSON解析失败：{e}")
else:
    print("请求失败，状态码：", response.status_code)

