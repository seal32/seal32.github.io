import requests
import re
import json
import hashlib
# import demjson

# 创建全局 session 并设置浏览器 UA
session = requests.Session()
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
session.headers.update(COMMON_HEADERS)
session.cookies.set("visited", "1")  # 提高拟真度

# 下载伪 JSON 文本
def fetch_raw_json():
    url = "http://www.xn--sss604efuw.art/jm/jiemi.php?url=http%3A%2F%2Fwww.%E9%A5%AD%E5%A4%AA%E7%A1%AC.art%2Ftv"
    resp = session.get(url, timeout=30, allow_redirects=True)
    resp.encoding = 'utf-8'
    return resp.text

# 下载 spider 文件
def extract_and_save_spider(json_text):
    match = re.search(r'"spider"\s*:\s*"([^"]+)"', json_text)
    if not match:
        raise ValueError("未找到 spider 字段")
    full_spider = match.group(1)
    spider_url = full_spider.split(";")[0]
    print(f"📥 下载 spider 文件: {spider_url}")
    resp = session.get(spider_url, timeout=30, allow_redirects=True)
    with open("fan.txt", "wb") as f:
        f.write(resp.content)
    print("✅ 已保存为 fan.txt")

# 计算本地文件 MD5
def get_md5(filepath):
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            md5.update(chunk)
    return md5.hexdigest()

# 删除不需要的 sites 项 + 替换链接
def clean_data(raw_text):
    # 统一把各种 GitHub 代理壳替换掉
    raw_text = re.sub(
        r'https?://[^/]+/https://raw\.githubusercontent\.com/fantaiying7/EXT/refs/heads/main',
        './FTY',
        raw_text
    )
    
    try:
        # 尝试标准JSON解析
        data = json.loads(raw_text)
    except:
        # 失败则使用 demjson
        data = demjson.decode(raw_text)

    # 如果之前注释的代码要启用，修复如下：
    # keywords = ["豆", "饭太硬", "广告", "PanSso", "YpanSo", "xzso", "米搜", "夸搜", "Aliso", "YiSo"]
    # original_count = len(data.get("sites", []))
    # data["sites"] = [
    #     s for s in data["sites"]
    #     if not any(kw in s.get("key", "") or kw in s.get("name", "") for kw in keywords)
    # ]
    # print(f"🧹 清理 {original_count - len(data['sites'])} 条 sites")
    
    return data

# 格式美化保存
class CompactJSONEncoder(json.JSONEncoder):
    def iterencode(self, o, _one_shot=False):
        def _compact_list(lst, indent_level):
            pad = '  ' * indent_level
            if all(isinstance(i, dict) for i in lst):
                return '[\n' + ',\n'.join([pad + '  ' + json.dumps(i, ensure_ascii=False, separators=(',', ': ')) for i in lst]) + '\n' + pad + ']'
            return json.dumps(lst, ensure_ascii=False, indent=2)
        def _encode(obj, indent_level=0):
            pad = '  ' * indent_level
            if isinstance(obj, dict):
                lines = [f'"{k}": {_encode(v, indent_level+1)}' for k, v in obj.items()]
                return '{\n' + pad + '  ' + (',\n' + pad + '  ').join(lines) + '\n' + pad + '}'
            elif isinstance(obj, list):
                return _compact_list(obj, indent_level)
            return json.dumps(obj, ensure_ascii=False)
        return iter([_encode(o)])

def save_json(data, filename="tvbox_cleaned.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, cls=CompactJSONEncoder)
    print(f"✅ 最终 JSON 保存为 {filename}")

# 主流程
if __name__ == "__main__":
    import traceback
    try:
        raw_text = fetch_raw_json()
        print(f"获取到的原始数据长度: {len(raw_text)}")
        
        extract_and_save_spider(raw_text)
        
        data = clean_data(raw_text)
        print(f"解析成功，包含 {len(data.get('sites', []))} 个站点")
        
        md5_value = get_md5("fan.txt")
        data["spider"] = f"./fan.txt;md5;{md5_value}"
        save_json(data)
    except Exception as e:
        print(f"❌ 错误: {e}")
        traceback.print_exc()  # 打印完整错误堆栈
