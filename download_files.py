import os
import requests

# 源文件 URL 与目标路径的映射
FILES = {
    "https://github.com/qist/tvbox/raw/refs/heads/master/fty.json": "fty.json",
    "https://github.com/qist/tvbox/raw/refs/heads/master/jar/fan.txt": "jar/fan.txt"
}

def download_file(url, dest_path):
    # 确保目标目录存在（例如 jar/ 目录）
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    
    print(f"正在下载: {url} -> {dest_path}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # 检查 HTTP 错误
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        print(f"成功: {dest_path}")
    except Exception as e:
        print(f"失败: {dest_path}，错误: {e}")
        raise  # 抛出异常以便 Actions 标记为失败

if __name__ == "__main__":
    for url, path in FILES.items():
        download_file(url, path)