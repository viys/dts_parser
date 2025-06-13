import sys
import re

def remove_comments(text):
    """去除 /* */ 块注释和 // 行注释"""
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    text = re.sub(r'//.*?$', '', text, flags=re.M)
    return text

def label_to_macro(label):
    """将 label 转为宏名"""
    return label.upper().replace("-", "_")

def parse_numeric(token):
    """尝试将 token 转为 int，支持十进制和十六进制"""
    try:
        return int(token, 0)
    except ValueError:
        return token

def parse_dts(dts_path):
    node_pattern = re.compile(r'(\w+)\s*:\s*(\w+)\s*\{([^}]*)\};', re.S)
    prop_pattern = re.compile(r'(\S+)(\s*=\s*([^;]+))?;')

    with open(dts_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = remove_comments(content)

    nodes = []
    for match in node_pattern.finditer(content):
        label = match.group(1)
        node_type = match.group(2)
        body = match.group(3)
        props = {}

        for pmatch in prop_pattern.finditer(body):
            key = pmatch.group(1)
            raw_val = pmatch.group(3)

            if raw_val is None:
                val = True
                props[key] = {"value": val, "quoted": False}
            else:
                raw_val = raw_val.strip()
                if raw_val.startswith('"') and raw_val.endswith('"'):
                    val = raw_val[1:-1]
                    props[key] = {"value": val, "quoted": True}
                elif raw_val.startswith('<') and raw_val.endswith('>'):
                    nums = raw_val[1:-1].split()
                    parsed = [parse_numeric(n) for n in nums]
                    if len(parsed) == 1:
                        parsed = parsed[0]
                    props[key] = {"value": parsed, "quoted": False}
                else:
                    props[key] = {"value": raw_val, "quoted": False}

        nodes.append({
            "label": label,
            "type": node_type,
            "props": props
        })

    return nodes

def format_macro_value(valobj):
    val = valobj["value"]
    quoted = valobj["quoted"]

    if val is True:
        return "1"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, list):
        return "{" + ", ".join(format_macro_value({"value": v, "quoted": False}) for v in val) + "}"
    if isinstance(val, str):
        return f'"{val}"' if quoted else val
    return f'"{val}"'

def generate_header(nodes, output_path):
    lines = []
    lines.append("/* Auto-generated devicetree header */\n")

    # 分组
    type_groups = {}
    for node in nodes:
        t = node["type"]
        type_groups.setdefault(t, []).append(node)

    for t, group_nodes in type_groups.items():
        lines.append(f"/** {t} **/")
        for node in group_nodes:
            macro_label = label_to_macro(node["label"])
            for k, v in node["props"].items():
                macro_name = k.upper().replace("-", "_")
                macro_val = format_macro_value(v)
                lines.append(f"#define DT_{macro_label}_{macro_name} {macro_val}")
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Header generated at {output_path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python dts_parser.py <input.dts> <output.h>")
        sys.exit(1)

    dts_path = sys.argv[1]
    output_path = sys.argv[2]

    nodes = parse_dts(dts_path)
    generate_header(nodes, output_path)

if __name__ == "__main__":
    main()
