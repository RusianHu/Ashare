"""
Ashare MCP 服务入口点
"""

import argparse
from .server import mcp

def main():
    """启动 Ashare MCP 服务"""
    parser = argparse.ArgumentParser(description="Ashare MCP 服务")
    parser.add_argument("--stdio", action="store_true", help="使用标准输入输出模式")

    args = parser.parse_args()

    if args.stdio:
        print("启动 Ashare MCP 服务 (stdio 模式)")
    else:
        print("启动 Ashare MCP 服务 (stdio 模式)")
        print("注意: 要使用 HTTP 模式，请使用 'fastmcp serve' 命令")

    # 使用标准输入输出模式
    mcp.run()

if __name__ == "__main__":
    main()
