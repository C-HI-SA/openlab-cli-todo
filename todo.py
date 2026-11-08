#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""带文件持久化的命令行待办清单程序"""

import json
import os

TODO_FILE = "todo.json"

"""load_tasks()  程序启动时调用，从 todo.json 读取任务列表。数据从磁盘文件来，到内存列表。文件不存在或格式错误时返回空列表，避免程序崩溃。"""

def load_tasks():
    """从 todo.json 读取任务；文件不存在或读取失败时返回空列表。"""
    if not os.path.exists(TODO_FILE):
        return []

    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"读取 {TODO_FILE} 失败，将从空列表开始：{exc}")
        return []

    if not isinstance(data, list):
        print(f"{TODO_FILE} 内容格式不正确，将从空列表开始。")
        return []

    tasks = []
    for item in data:
        if isinstance(item, dict):
            content = str(item.get("content", "")).strip()
            if not content:
                continue
            tasks.append({
                "content": content,
                "done": item.get("done", False) is True,
            })
        elif isinstance(item, str):
            # 兼容旧版本保存的纯字符串任务
            content = item.strip()
            if content:
                tasks.append({"content": content, "done": False})

    return tasks

"""save_tasks(): 每次添加、完成、删除后调用，把内存里的任务列表写回 todo.json。数据从内存列表来，到磁盘文件。"""

def save_tasks(tasks):
    """把任务列表写回 todo.json。"""
    try:
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"保存 {TODO_FILE} 失败：{exc}")


def show_menu():
    print("\n===== 待办清单 =====")
    print("1. 添加任务")
    print("2. 查看任务")
    print("3. 退出")
    print("4. 标记任务完成")
    print("5. 删除任务")


def input_index(prompt, tasks):
    """让用户输入任务序号（从 1 开始），返回合法索引；非法则返回 None。"""
    if not tasks:
        print("暂无任务。")
        return None

    raw = input(prompt).strip()
    if not raw:
        print("输入不能为空，已取消操作。")
        return None

    if not raw.isdigit():
        print("请输入有效的序号（正整数）。")
        return None

    number = int(raw)
    if number < 1 or number > len(tasks):
        print(f"序号超出范围，请输入 1 到 {len(tasks)} 之间的数字。")
        return None

    return number - 1  # 转换为列表索引


def add_task(tasks):
    """添加任务，并立即写入 todo.json。"""
    content = input("请输入任务内容：").strip()
    if not content:
        print("任务内容不能为空，已取消添加。")
        return

    tasks.append({
        "content": content,
        "done": False,
    })
    save_tasks(tasks)
    print(f"已添加：{content}（当前共 {len(tasks)} 条任务）")


def show_tasks(tasks):
    """按序号打印所有任务及完成状态：[x] 表示已完成，[ ] 表示未完成。"""
    if not tasks:
        print("暂无任务。")
        return

    print(f"共 {len(tasks)} 条任务：")
    for index, task in enumerate(tasks, start=1):
        mark = "x" if task.get("done", False) else " "
        print(f"{index}. [{mark}] {task['content']}")


def mark_done(tasks):
    """把指定序号的任务标记为已完成，并写回 todo.json。"""
    index = input_index("请输入要标记完成的任务序号：", tasks)
    if index is None:
        return

    if tasks[index].get("done", False):
        print(f"任务 {index + 1} 已经是已完成状态。")
        return

    tasks[index]["done"] = True
    save_tasks(tasks)
    print(f"任务 {index + 1} 已标记为完成：{tasks[index]['content']}")


def delete_task(tasks):
    """删除指定序号的任务，并写回 todo.json。"""
    index = input_index("请输入要删除的任务序号：", tasks)
    if index is None:
        return

    removed = tasks.pop(index)
    save_tasks(tasks)
    print(f"已删除任务 {index + 1}：{removed['content']}（剩余 {len(tasks)} 条）")

"""main(): 程序入口，负责打印菜单、读取用户输入、根据输入调用对应功能（添加/查看/完成/删除）。数据从终端输入来，分发到各个功能函数，最后回到终端输出。"""

def main():
    tasks = load_tasks()

    while True:
        show_menu()
        choice = input("请选择操作（1-5）：").strip()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            show_tasks(tasks)
        elif choice == "3":
            print("已退出，再见！")
            break
        elif choice == "4":
            mark_done(tasks)
        elif choice == "5":
            delete_task(tasks)
        else:
            print("无效的输入，请输入 1 到 5 之间的数字。")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n程序已退出。")