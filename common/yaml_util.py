# YAML 测试数据加载与参数化用例 ID 工具
import os
import yaml

def load_yaml(file_path):
    with open(file_path, "r", encoding='utf-8') as f:
        data = yaml.safe_load(f)

    return data


def load_case_data(file_name):
    current_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(current_dir)
    case_file = os.path.join(project_root, "data", file_name)

    data = load_yaml(case_file)

    assert data is not None, "YAML文件为空或读取失败"

    return data


def get_case_ids(cases):
    return [case["case_name"] for case in cases]


