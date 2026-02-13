import os
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import datetime
try:
    from PIL import Image, ImageTk  # 用于图片预览
except ImportError:
    # 未安装Pillow时禁用图片功能
    Image = None
    ImageTk = None

# ========================== 常量定义 ==========================
TODO_FILE = "todo_data_ui.txt"  # 待办数据文件路径
WINDOW_CONFIG_FILE = "window_config.txt"  # 主窗口配置文件路径
DETAIL_WINDOW_CONFIG_FILE = "detail_window_config.txt"  # 详情窗口配置文件路径
HIDE_STATE_FILE = "hide_state_config.txt"  # 隐藏状态配置文件路径
PROJECTS_ROOT = "项目文件夹"  # 项目文件夹根目录

# ========================== 全局变量 ==========================
todo_list = []  # 全局待办列表
task_text_widget = None  # 全局任务显示文本框
root_window = None  # 全局主窗口
hide_completed = False  # 是否隐藏已完成任务

# ========================== 工具函数 ==========================
def darken_color(hex_color, percent=10):
    """将十六进制颜色变暗指定百分比"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    r = max(0, r - int(r * percent / 100))
    g = max(0, g - int(g * percent / 100))
    b = max(0, b - int(b * percent / 100))
    
    return f"#{r:02x}{g:02x}{b:02x}"

def load_todo():
    """读取待办任务（增强容错）- 扩展支持多图片、多视频、多文件附件和项目文件夹路径"""
    global todo_list
    todo_list = []
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("|")
                    # 扩展为7个字段：标题|状态|批注|图片列表|视频列表|文件列表|项目文件夹路径
                    # 图片、视频、文件字段使用分号分隔多个路径
                    task_data = parts + [""] * (7 - len(parts))
                    todo_list.append("|".join(task_data[:7]))
        except Exception as e:
            messagebox.showerror("读取失败", f"加载待办数据出错：{str(e)}", parent=root_window)

def save_todo():
    """保存待办任务"""
    global todo_list
    try:
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            for task in todo_list:
                if task.strip():
                    f.write(task + "\n")
    except Exception as e:
        messagebox.showerror("保存失败", f"保存待办数据出错：{str(e)}", parent=root_window)

def save_window_config():
    """保存窗口配置（尺寸和位置）"""
    global root_window
    if not root_window:
        return
    try:
        # 获取当前窗口尺寸和位置
        width = root_window.winfo_width()
        height = root_window.winfo_height()
        x = root_window.winfo_x()
        y = root_window.winfo_y()
        
        # 只有在窗口已显示且尺寸有效时才保存
        if width > 50 and height > 50:
            geometry_str = f"{width}x{height}+{x}+{y}"
            with open(WINDOW_CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(geometry_str)
    except Exception as e:
        # 静默失败，不影响主要功能
        pass

def load_window_config():
    """加载窗口配置（尺寸和位置）"""
    try:
        if os.path.exists(WINDOW_CONFIG_FILE):
            with open(WINDOW_CONFIG_FILE, "r", encoding="utf-8") as f:
                geometry_str = f.read().strip()
                # 验证格式：宽度x高度+X+Y 或 宽度x高度
                if geometry_str:
                    # 检查是否有位置信息
                    if "+" in geometry_str:
                        parts = geometry_str.split("+")
                        if len(parts) == 3:
                            size_part = parts[0]
                            if "x" in size_part:
                                return geometry_str
                    elif "x" in geometry_str:
                        # 只有尺寸信息
                        return geometry_str
    except Exception as e:
        # 静默失败，返回默认值
        pass
    return "450x700"  # 默认尺寸

def save_detail_window_config(detail_win):
    """保存详情窗口配置（尺寸和位置）"""
    try:
        # 获取当前窗口尺寸和位置
        width = detail_win.winfo_width()
        height = detail_win.winfo_height()
        x = detail_win.winfo_x()
        y = detail_win.winfo_y()
        
        # 只有在窗口已显示且尺寸有效时才保存
        if width > 50 and height > 50:
            geometry_str = f"{width}x{height}+{x}+{y}"
            with open(DETAIL_WINDOW_CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(geometry_str)
    except Exception as e:
        # 静默失败，不影响主要功能
        pass

def load_detail_window_config():
    """加载详情窗口配置（尺寸和位置）"""
    try:
        if os.path.exists(DETAIL_WINDOW_CONFIG_FILE):
            with open(DETAIL_WINDOW_CONFIG_FILE, "r", encoding="utf-8") as f:
                geometry_str = f.read().strip()
                # 验证格式：宽度x高度+X+Y 或 宽度x高度
                if geometry_str:
                    # 检查是否有位置信息
                    if "+" in geometry_str:
                        parts = geometry_str.split("+")
                        if len(parts) == 3:
                            size_part = parts[0]
                            if "x" in size_part:
                                return geometry_str
                    elif "x" in geometry_str:
                        # 只有尺寸信息
                        return geometry_str
    except Exception as e:
        # 静默失败，返回默认值
        pass
    return "750x900"  # 默认尺寸

def save_hide_state(task_index, hide_states):
    """保存任务的隐藏状态"""
    try:
        # 读取现有的隐藏状态
        all_hide_states = {}
        if os.path.exists(HIDE_STATE_FILE):
            with open(HIDE_STATE_FILE, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line:
                        parts = line.split("|")
                        if len(parts) >= 2:
                            idx = int(parts[0])
                            states = parts[1].split(",")
                            all_hide_states[idx] = states
        
        # 更新当前任务的隐藏状态
        all_hide_states[task_index] = hide_states
        
        # 保存所有隐藏状态
        with open(HIDE_STATE_FILE, "w", encoding="utf-8") as f:
            for idx, states in all_hide_states.items():
                states_str = ",".join(states)
                f.write(f"{idx}|{states_str}\n")
    except Exception as e:
        print(f"保存隐藏状态失败: {e}")

def load_hide_state(task_index):
    """加载任务的隐藏状态"""
    try:
        if not os.path.exists(HIDE_STATE_FILE):
            return ["0", "0", "0", "0"]  # 默认全部显示
        
        with open(HIDE_STATE_FILE, "r", encoding="utf-8") as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    parts = line.split("|")
                    if len(parts) >= 2:
                        idx = int(parts[0])
                        if idx == task_index:
                            states = parts[1].split(",")
                            # 确保有4个状态值
                            while len(states) < 4:
                                states.append("0")
                            return states[:4]
        
        # 如果没有找到该任务的隐藏状态，返回默认值
        return ["0", "0", "0", "0"]
    except Exception as e:
        print(f"加载隐藏状态失败: {e}")
        return ["0", "0", "0", "0"]

def parse_path_list(path_string):
    """解析路径列表字符串，返回路径列表"""
    if not path_string or not path_string.strip():
        return []
    # 使用分号分隔多个路径
    paths = [p.strip() for p in path_string.split(";") if p.strip()]
    # 过滤掉不存在的路径
    return [p for p in paths if os.path.exists(p)]

def join_path_list(paths):
    """将路径列表转换为字符串"""
    if not paths:
        return ""
    return ";".join(paths)

def extract_video_thumbnail(video_path, thumbnail_path=None, time_sec=1):
    """使用ffmpeg提取视频缩略图"""
    if not thumbnail_path:
        # 生成临时缩略图路径
        import tempfile
        temp_dir = tempfile.gettempdir()
        video_name = os.path.basename(video_path)
        thumbnail_name = f"thumb_{hash(video_path)}_{video_name}.jpg"
        thumbnail_path = os.path.join(temp_dir, thumbnail_name)
    
    try:
        # 使用ffmpeg提取视频第1秒的帧作为缩略图
        cmd = f'ffmpeg -i "{video_path}" -ss {time_sec} -vframes 1 -q:v 2 "{thumbnail_path}" -y'
        import subprocess
        # 使用二进制模式避免编码问题
        result = subprocess.run(cmd, shell=True, capture_output=True, text=False)
        
        if result.returncode == 0 and os.path.exists(thumbnail_path):
            return thumbnail_path
        else:
            return None
    except Exception as e:
        print(f"提取视频缩略图失败: {e}")
        return None

def get_video_thumbnail(video_path, cache_dir=None):
    """获取视频缩略图，优先从缓存加载"""
    if not os.path.exists(video_path):
        return None
    
    # 创建缓存目录
    if cache_dir is None:
        cache_dir = os.path.join(os.path.expanduser("~"), ".todo_video_thumbs")
    os.makedirs(cache_dir, exist_ok=True)
    
    # 生成缓存文件名
    video_mtime = os.path.getmtime(video_path)
    video_size = os.path.getsize(video_path)
    cache_key = f"{os.path.basename(video_path)}_{video_size}_{video_mtime}"
    import hashlib
    cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{cache_hash}.jpg")
    
    # 检查缓存是否存在
    if os.path.exists(cache_file):
        return cache_file
    
    # 提取缩略图并保存到缓存
    thumbnail = extract_video_thumbnail(video_path, cache_file)
    return thumbnail

# ========================== 项目文件夹管理函数 ==========================
def sanitize_filename(filename):
    """清理文件名，移除非法字符"""
    # Windows文件名非法字符: \ / : * ? " < > |
    illegal_chars = r'[\\/*?:"<>|]'
    import re
    return re.sub(illegal_chars, '_', filename)

def create_project_folder(task_index, task_title):
    """为任务创建项目文件夹"""
    # 确保项目根目录存在
    os.makedirs(PROJECTS_ROOT, exist_ok=True)
    
    # 清理任务标题，用于文件夹名
    safe_title = sanitize_filename(task_title)
    if not safe_title or safe_title.isspace():
        safe_title = f"任务{task_index+1}"
    
    # 创建文件夹名
    folder_name = f"项目{task_index+1}_{safe_title[:50]}"  # 限制长度
    project_path = os.path.join(PROJECTS_ROOT, folder_name)
    
    # 如果文件夹已存在，添加数字后缀
    counter = 1
    original_path = project_path
    while os.path.exists(project_path):
        project_path = f"{original_path}_{counter}"
        counter += 1
    
    # 创建项目文件夹和子文件夹
    try:
        os.makedirs(project_path)
        os.makedirs(os.path.join(project_path, "images"))
        os.makedirs(os.path.join(project_path, "videos"))
        os.makedirs(os.path.join(project_path, "files"))
        os.makedirs(os.path.join(project_path, "docs"))
        
        # 创建项目信息文件
        info_file = os.path.join(project_path, "project_info.txt")
        import datetime
        with open(info_file, "w", encoding="utf-8") as f:
            f.write(f"项目名称: {task_title}\n")
            f.write(f"创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"任务索引: {task_index}\n")
            f.write(f"原始标题: {task_title}\n")
        
        return project_path
    except Exception as e:
        print(f"创建项目文件夹失败: {e}")
        return None

def copy_file_to_project(original_path, project_path, file_type="files"):
    """将文件复制到项目文件夹"""
    if not os.path.exists(original_path):
        return None
    
    try:
        # 获取文件名和扩展名
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)
        
        # 确定目标文件夹
        if file_type == "images":
            target_dir = os.path.join(project_path, "images")
        elif file_type == "videos":
            target_dir = os.path.join(project_path, "videos")
        elif file_type == "docs":
            target_dir = os.path.join(project_path, "docs")
        else:
            target_dir = os.path.join(project_path, "files")
        
        # 确保目标文件夹存在
        os.makedirs(target_dir, exist_ok=True)
        
        # 生成目标路径
        target_path = os.path.join(target_dir, filename)
        
        # 如果文件已存在，添加数字后缀
        counter = 1
        original_target = target_path
        while os.path.exists(target_path):
            target_path = os.path.join(target_dir, f"{name}_{counter}{ext}")
            counter += 1
        
        # 复制文件
        import shutil
        shutil.copy2(original_path, target_path)
        
        return target_path
    except Exception as e:
        print(f"复制文件失败: {e}")
        return None

def get_file_type_from_extension(filepath):
    """根据文件扩展名确定文件类型"""
    ext = os.path.splitext(filepath)[1].lower()
    image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    doc_exts = ['.doc', '.docx', '.pdf', '.txt', '.xls', '.xlsx', '.ppt', '.pptx']
    
    if ext in image_exts:
        return "images"
    elif ext in video_exts:
        return "videos"
    elif ext in doc_exts:
        return "docs"
    else:
        return "files"

def migrate_existing_files(task_index, project_path, img_paths, video_paths, file_paths):
    """迁移现有文件到项目文件夹"""
    migrated_img_paths = []
    migrated_video_paths = []
    migrated_file_paths = []
    
    # 迁移图片
    for img_path in img_paths:
        if os.path.exists(img_path):
            new_path = copy_file_to_project(img_path, project_path, "images")
            if new_path:
                migrated_img_paths.append(new_path)
        else:
            migrated_img_paths.append(img_path)
    
    # 迁移视频
    for video_path in video_paths:
        if os.path.exists(video_path):
            new_path = copy_file_to_project(video_path, project_path, "videos")
            if new_path:
                migrated_video_paths.append(new_path)
        else:
            migrated_video_paths.append(video_path)
    
    # 迁移文件
    for file_path in file_paths:
        if os.path.exists(file_path):
            file_type = get_file_type_from_extension(file_path)
            new_path = copy_file_to_project(file_path, project_path, file_type)
            if new_path:
                migrated_file_paths.append(new_path)
        else:
            migrated_file_paths.append(file_path)
    
    return migrated_img_paths, migrated_video_paths, migrated_file_paths

# ========================== 主界面UI更新函数 ==========================
def update_main_ui():
    """更新主界面"""
    global todo_list, task_text_widget, hide_completed
    if not task_text_widget:
        return
    
    task_text_widget.config(state=tk.NORMAL)
    task_text_widget.delete(1.0, tk.END)
    
    if not todo_list:
        task_text_widget.insert(tk.END, "📌 暂无待办任务，快去添加吧！\n", "empty")
        display_count = 1
    else:
        display_index = 1
        actual_task_indices = []
        
        for i, task in enumerate(todo_list):
            parts = task.split("|")
            title = parts[0] if parts[0] else "无标题任务"
            status = "已完成" if (len(parts)>=2 and parts[1]=="True") else "未完成"
            
            if hide_completed and status == "已完成":
                continue
                
            status_tag = "completed" if status == "已完成" else "uncompleted"
            
            task_text_widget.insert(tk.END, f"{display_index}. 【", "index")
            task_text_widget.insert(tk.END, status, status_tag)
            task_text_widget.insert(tk.END, f"】", "title_end")
            task_text_widget.insert(tk.END, title, f"title_clickable_{i}")
            task_text_widget.insert(tk.END, "\n", "newline")
            
            actual_task_indices.append(i)
            display_index += 1
            
        if display_index == 1 and hide_completed:
            task_text_widget.insert(tk.END, "📌 暂无未完成的任务，太棒了！\n", "empty")
            display_count = 1
        else:
            display_count = display_index - 1
            
        for i, actual_index in enumerate(actual_task_indices):
            def make_click_func(idx):
                def click_func(event):
                    show_task_detail_by_index(actual_task_indices[idx])
                return click_func
            
            tag_name = f"title_clickable_{actual_index}"
            task_text_widget.tag_config(tag_name, foreground="#1a73e8", font=("微软雅黑", 11), underline=True)
            task_text_widget.tag_bind(tag_name, "<Button-1>", make_click_func(i))
            task_text_widget.tag_bind(tag_name, "<Enter>", lambda e, t=tag_name: task_text_widget.tag_config(t, foreground="#0d47a1"))
            task_text_widget.tag_bind(tag_name, "<Leave>", lambda e, t=tag_name: task_text_widget.tag_config(t, foreground="#1a73e8"))
    
    task_text_widget.tag_config("empty", foreground="#666666", font=("微软雅黑", 11))
    task_text_widget.tag_config("index", foreground="#333333", font=("微软雅黑", 11, "bold"))
    task_text_widget.tag_config("completed", foreground="#00C851", font=("微软雅黑", 11, "bold"))
    task_text_widget.tag_config("uncompleted", foreground="#FF6D00", font=("微软雅黑", 11, "bold"))
    task_text_widget.tag_config("title_end", foreground="#333333", font=("微软雅黑", 11))
    task_text_widget.tag_config("newline", font=("微软雅黑", 11))
    
    task_text_widget.config(state=tk.DISABLED)
    
    min_lines = 3
    max_lines = 15
    target_lines = max(min_lines, min(display_count + 1, max_lines))
    task_text_widget.config(height=target_lines)

# -------------------------- 查看待办详情 --------------------------
def show_task_detail_by_index(actual_index):
    """根据实际索引查看待办详情"""
    global todo_list, root_window
    try:
        if not todo_list:
            messagebox.showerror("错误", "暂无待办任务！", parent=root_window)
            return
        
        index = actual_index
        if not (0 <= index < len(todo_list)):
            messagebox.showerror("错误", "序号不存在！", parent=root_window)
            return
        
        # 解析任务数据（扩展为7个字段）
        task_parts = todo_list[index].split("|")
        task_parts = task_parts + [""] * (7 - len(task_parts))
        title, status, comment, img_paths_str, video_paths_str, file_paths_str, project_path = task_parts[0], task_parts[1], task_parts[2], task_parts[3], task_parts[4], task_parts[5], task_parts[6]
        title = title if title.strip() else "无标题任务"
        status = status if status in ["True", "False"] else "False"
        comment = comment if comment.strip() else "无批注内容，直接输入后点击保存即可"
        
        # 解析路径列表
        img_paths = parse_path_list(img_paths_str)
        video_paths = parse_path_list(video_paths_str)
        file_paths = parse_path_list(file_paths_str)
        
        # 如果项目文件夹不存在，尝试创建
        if not project_path or not os.path.exists(project_path):
            project_path = create_project_folder(index, title)
            if project_path:
                # 更新项目文件夹路径
                task_parts[6] = project_path
                todo_list[index] = "|".join(task_parts)
                save_todo()
        
        # 调用详情窗口创建函数，传递项目文件夹路径
        create_detail_window(index, title, status, comment, img_paths, video_paths, file_paths, project_path)
        
    except Exception as e:
        messagebox.showerror("错误", f"打开待办详情失败：{str(e)}", parent=root_window)

def show_task_detail():
    """查看待办详情（通过输入框）"""
    global todo_list, root_window
    try:
        if not todo_list:
            messagebox.showerror("错误", "暂无待办任务！", parent=root_window)
            return
        
        # 输入任务序号
        index_input = simpledialog.askstring("查看详情", "请输入任务序号：", parent=root_window)
        if index_input is None or index_input.strip() == "":
            return
        try:
            index = int(index_input) - 1
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字序号！", parent=root_window)
            return
        
        # 直接调用按索引查看的函数
        show_task_detail_by_index(index)
        
    except Exception as e:
        messagebox.showerror("错误", f"打开待办详情失败：{str(e)}", parent=root_window)

def create_detail_window(index, title, status, comment, img_paths, video_paths, file_paths, project_path=None):
    """创建任务详情窗口（核心UI构建逻辑）- 扩展支持多图片、多视频、多文件附件和项目文件夹"""
    global todo_list, root_window
    
    # 如果项目文件夹不存在，尝试创建
    if not project_path or not os.path.exists(project_path):
        project_path = create_project_folder(index, title)
        if project_path:
            # 更新项目文件夹路径
            task_parts = todo_list[index].split("|")
            task_parts = task_parts + [""] * (7 - len(task_parts))
            task_parts[6] = project_path
            todo_list[index] = "|".join(task_parts)
            save_todo()
    
    # 加载保存的详情窗口配置
    saved_detail_geometry = load_detail_window_config()
    
    # 创建详情窗口
    detail_win = tk.Toplevel(root_window)
    detail_win.title(f"任务详情 - {title[:20]}..." if len(title)>20 else f"任务详情 - {title}")
    detail_win.geometry(saved_detail_geometry)  # 使用保存的尺寸
    detail_win.minsize(650, 750)    # 设置最小尺寸
    detail_win.config(bg="#f8fafc")  # 更柔和的背景色
    detail_win.transient(root_window)
    detail_win.grab_set()
    detail_win.lift()
    
    # 设置窗口图标和样式
    try:
        detail_win.iconbitmap(default=root_window.iconbitmap())
    except:
        pass
    
    # 详情窗口大小变化响应函数
    def on_detail_window_resize(event):
        # 延迟保存窗口配置，避免频繁保存
        if hasattr(detail_win, '_save_timer'):
            detail_win.after_cancel(detail_win._save_timer)
        detail_win._save_timer = detail_win.after(500, lambda: save_detail_window_config(detail_win))
    
    # 绑定窗口大小变化事件
    detail_win.bind("<Configure>", on_detail_window_resize)
    
    # 详情窗口关闭协议处理函数
    def on_detail_window_close():
        # 保存窗口配置
        save_detail_window_config(detail_win)
        # 销毁窗口
        detail_win.destroy()
    
    # 设置窗口关闭协议
    detail_win.protocol("WM_DELETE_WINDOW", on_detail_window_close)

    # 主滚动容器
    main_canvas = tk.Canvas(detail_win, bg="#f8fafc", bd=0, highlightthickness=0)
    main_scrollbar = tk.Scrollbar(detail_win, orient=tk.VERTICAL, command=main_canvas.yview, bg="#e2e8f0")
    main_scrollable_frame = tk.Frame(main_canvas, bg="#f8fafc")

    # 绑定滚动事件
    main_scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )
    main_canvas.create_window((0, 0), window=main_scrollable_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=main_scrollbar.set)
    
    # 鼠标滚轮滚动功能：当鼠标在页面内滚动鼠标的滚轮，页面滚动条上下移动
    def on_mouse_wheel(event):
        # 检查事件是否发生在备注文本框内
        try:
            # 尝试获取comment_text变量，如果不存在则跳过检查
            if 'comment_text' in locals() and (event.widget == comment_text or event.widget == comment_scrollbar):
                # 在备注栏内，不处理滚轮事件（让备注栏自己的滚动条处理）
                return
        except:
            pass
        
        # 在其他地方，滚动主窗口
        if event.delta > 0:
            main_canvas.yview_scroll(-1, "units")
        else:
            main_canvas.yview_scroll(1, "units")
    
    # 绑定鼠标滚轮事件到主画布和可滚动框架
    main_canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    main_scrollable_frame.bind_all("<MouseWheel>", on_mouse_wheel)

    # 布局主滚动容器
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
    main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 主卡片容器（现代化卡片设计）
    main_card = tk.Frame(main_scrollable_frame, bg="#ffffff", bd=0, 
                        highlightbackground="#e2e8f0", highlightthickness=1,
                        padx=30, pady=30)
    main_card.pack(fill=tk.BOTH, padx=25, pady=25)
    
    # 添加阴影效果（通过多层边框模拟）
    shadow_frame = tk.Frame(main_scrollable_frame, bg="#e2e8f0", padx=1, pady=1)
    shadow_frame.pack(fill=tk.BOTH, padx=20, pady=20)
    shadow_frame.lower(main_card)

    # -------------------------- 标题+状态区（现代化设计） --------------------------
    header_frame = tk.Frame(main_card, bg="#ffffff")
    header_frame.pack(fill=tk.X, pady=(0, 30))
    
    # 标题标签（更优雅的字体和颜色）
    title_label = tk.Label(header_frame, text=title, bg="#ffffff", fg="#1e293b",
                          font=("微软雅黑", 22, "bold"), anchor="w", wraplength=650,
                          justify="left")
    title_label.pack(fill=tk.X, pady=(0, 15))
    
    # 状态和元信息行
    meta_frame = tk.Frame(header_frame, bg="#ffffff")
    meta_frame.pack(fill=tk.X)
    
    # 状态标签（现代化胶囊样式）
    status_text = "已完成" if status == "True" else "未完成"
    status_bg = "#10b981" if status == "True" else "#f97316"  # 更现代化的颜色
    status_frame = tk.Frame(meta_frame, bg=status_bg, bd=0, relief=tk.FLAT)
    status_frame.pack(side=tk.LEFT, padx=(0, 15))
    status_label = tk.Label(status_frame, text=f"  {status_text}  ", bg=status_bg, fg="#ffffff",
                            font=("微软雅黑", 11, "bold"), padx=12, pady=5)
    status_label.pack()
    
    # 任务序号标签
    task_number_label = tk.Label(meta_frame, text=f"任务 #{index+1}", bg="#ffffff", fg="#64748b",
                                 font=("微软雅黑", 10))
    task_number_label.pack(side=tk.LEFT)
    
    # 分隔线
    separator = tk.Frame(main_card, bg="#f1f5f9", height=2)
    separator.pack(fill=tk.X, pady=(0, 30))

    # -------------------------- 事项日志/备注区（重新设计） --------------------------
    comment_frame = tk.LabelFrame(main_card, text="📋 事项日志/备注", bg="#ffffff", fg="#475569",
                                  font=("微软雅黑", 14, "bold"), labelanchor="n",
                                  padx=20, pady=15, bd=1, relief=tk.FLAT)
    comment_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 30))
    
    # 事项日志隐藏按钮
    comment_hide_btn_frame = tk.Frame(comment_frame, bg="#ffffff")
    comment_hide_btn_frame.pack(fill=tk.X, pady=(0, 10))
    
    comment_hide_btn = tk.Button(comment_hide_btn_frame, text="隐藏", bg="#94a3b8", fg="#ffffff",
                                 font=("微软雅黑", 9, "bold"), bd=0, padx=10, pady=3,
                                 relief=tk.FLAT, cursor="hand2")
    comment_hide_btn.pack(side=tk.RIGHT)
    
    # 加载保存的隐藏状态
    hide_states = load_hide_state(index)
    comment_hidden = hide_states[0] == "1"
    img_hidden = hide_states[1] == "1"
    video_hidden = hide_states[2] == "1"
    file_hidden = hide_states[3] == "1"
    
    # 根据保存的状态自动隐藏功能区
    def apply_hidden_states():
        # 使用局部变量而不是闭包变量
        try:
            if comment_hidden:
                comment_frame.config(pady=5)
                for widget in comment_frame.winfo_children():
                    if widget != comment_hide_btn_frame:
                        widget.pack_forget()
            
            if img_hidden:
                img_frame.config(pady=5)
                for widget in img_frame.winfo_children():
                    if widget != img_hide_btn_frame:
                        widget.pack_forget()
            
            if video_hidden:
                video_frame.config(pady=5)
                for widget in video_frame.winfo_children():
                    if widget != video_hide_btn_frame:
                        widget.pack_forget()
            
            if file_hidden:
                file_frame.config(pady=5)
                for widget in file_frame.winfo_children():
                    if widget != file_hide_btn_frame:
                        widget.pack_forget()
        except Exception as e:
            print(f"应用隐藏状态时出错: {e}")
    
    # 延迟应用隐藏状态，确保所有组件都已创建
    detail_win.after(100, apply_hidden_states)
    
    # 根据保存的状态设置初始按钮文本（在按钮创建后）
    def set_initial_button_text():
        try:
            if comment_hidden:
                comment_hide_btn.config(text="显示", bg="#64748b")
            if img_hidden:
                img_hide_btn.config(text="显示", bg="#64748b")
            if video_hidden:
                video_hide_btn.config(text="显示", bg="#64748b")
            if file_hidden:
                file_hide_btn.config(text="显示", bg="#64748b")
        except Exception as e:
            print(f"设置按钮文本时出错: {e}")
    
    detail_win.after(150, set_initial_button_text)
    
    # 事项日志隐藏状态
    comment_original_height = None
    comment_original_pady = None
    
    def toggle_comment_hide():
        nonlocal comment_hidden, comment_original_height, comment_original_pady
        if not comment_hidden:
            # 隐藏事项日志区
            comment_hidden = True
            comment_hide_btn.config(text="显示", bg="#64748b")
            comment_frame.config(pady=5)  # 减少内边距
            # 隐藏内部内容但保留框架
            for widget in comment_frame.winfo_children():
                if widget != comment_hide_btn_frame:
                    widget.pack_forget()
        else:
            # 显示事项日志区
            comment_hidden = False
            comment_hide_btn.config(text="隐藏", bg="#94a3b8")
            comment_frame.config(pady=20)  # 恢复内边距
            # 重新显示内部内容
            comment_help.pack(fill=tk.X, pady=(0, 10))
            text_container.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            button_container.pack(fill=tk.X, pady=(15, 0))
        
        # 保存隐藏状态
        save_hide_state(index, [
            "1" if comment_hidden else "0",
            "1" if img_hidden else "0",
            "1" if video_hidden else "0",
            "1" if file_hidden else "0"
        ])
    
    comment_hide_btn.config(command=toggle_comment_hide)
    
    # 按钮悬停效果
    def on_enter_comment_hide(e):
        comment_hide_btn.config(bg="#64748b")
    def on_leave_comment_hide(e):
        comment_hide_btn.config(bg="#94a3b8" if not comment_hidden else "#64748b")
    comment_hide_btn.bind("<Enter>", on_enter_comment_hide)
    comment_hide_btn.bind("<Leave>", on_leave_comment_hide)
    
    # 批注说明文字
    comment_help = tk.Label(comment_frame, text="记录任务的详细说明、进展日志、批准意见等。支持编辑和保存。", 
                           bg="#ffffff", fg="#94a3b8", font=("微软雅黑", 10),
                           anchor="w", justify="left")
    comment_help.pack(fill=tk.X, pady=(0, 10))

    # 日志文本框容器 - 使用更大的容器显示全部内容
    text_container = tk.Frame(comment_frame, bg="#f8fafc")
    text_container.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
    
    # 创建文本框 - 横向尺寸小一倍（宽度减少一半）
    comment_text = tk.Text(text_container, bg="#f8fafc", fg="#334155", font=("微软雅黑", 11),
                           wrap=tk.WORD, bd=1, relief=tk.SOLID, padx=15, pady=15,
                           height=25, width=45, highlightthickness=1, highlightcolor="#3b82f6",
                           undo=True)  # 启用撤销功能
    
    # 创建垂直滚动条
    comment_scrollbar = tk.Scrollbar(text_container, orient=tk.VERTICAL, command=comment_text.yview)
    comment_text.config(yscrollcommand=comment_scrollbar.set)
    
    # 布局：文本框占据大部分空间，滚动条在右侧
    comment_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    comment_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 插入批注内容
    comment_text.insert(1.0, comment)
    
    # 确保滚动条可用并滚动到顶部
    comment_text.yview_moveto(0)
    
    # 自动调整文本框显示
    def adjust_text_display():
        # 获取内容的行数
        line_count = int(comment_text.index('end-1c').split('.')[0])
        
        # 根据内容多少动态调整显示
        if line_count <= 25:
            # 内容不超过25行，完全显示
            comment_text.config(height=min(25, max(15, line_count + 2)))
            comment_scrollbar.pack_forget()  # 内容较少时隐藏滚动条
        else:
            # 内容超过25行，启用滚动条并固定高度
            comment_text.config(height=25)
            comment_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 延迟执行调整
    detail_win.after(100, adjust_text_display)
    
    # 添加文本框右键菜单（复制、粘贴、剪切）
    def show_text_menu(event):
        text_menu = tk.Menu(detail_win, tearoff=0)
        text_menu.add_command(label="复制", command=lambda: comment_text.event_generate("<<Copy>>"))
        text_menu.add_command(label="粘贴", command=lambda: comment_text.event_generate("<<Paste>>"))
        text_menu.add_command(label="剪切", command=lambda: comment_text.event_generate("<<Cut>>"))
        text_menu.add_separator()
        text_menu.add_command(label="全选", command=lambda: comment_text.tag_add("sel", "1.0", "end"))
        text_menu.tk_popup(event.x_root, event.y_root)
    
    # 绑定右键菜单
    comment_text.bind("<Button-3>", show_text_menu)

    # 保存批注按钮（现代化按钮设计）
    def save_comment_func():
        try:
            new_comment = comment_text.get(1.0, tk.END).strip()
            task_parts = todo_list[index].split("|")
            task_parts = task_parts + [""] * (7 - len(task_parts))
            task_parts[2] = new_comment
            todo_list[index] = "|".join(task_parts)
            save_todo()
            # 现代化成功提示
            success_label = tk.Label(comment_frame, text="✓ 批注已保存", bg="#d1fae5", fg="#065f46",
                                    font=("微软雅黑", 9, "bold"), padx=10, pady=5)
            success_label.pack(side=tk.BOTTOM, pady=(10, 0))
            detail_win.after(2000, success_label.destroy)  # 2秒后消失
            
            # 空值处理
            if not new_comment:
                comment_text.delete(1.0, tk.END)
                comment_text.insert(1.0, "无批注内容，直接输入后点击保存即可")
        except Exception as e:
            messagebox.showerror("错误", f"保存批注失败：{str(e)}", parent=detail_win)

    # 按钮容器
    button_container = tk.Frame(comment_frame, bg="#ffffff")
    button_container.pack(fill=tk.X, pady=(15, 0))
    
    save_comment_btn = tk.Button(button_container, text="💾 保存批注", bg="#3b82f6", fg="#ffffff",
                                 font=("微软雅黑", 11, "bold"), bd=0, padx=25, pady=10,
                                 relief=tk.FLAT, cursor="hand2", command=save_comment_func,
                                 activebackground="#2563eb", activeforeground="#ffffff")
    save_comment_btn.pack(side=tk.RIGHT)
    
    # 按钮悬停效果
    def on_enter_save(e):
        save_comment_btn.config(bg="#2563eb")
    def on_leave_save(e):
        save_comment_btn.config(bg="#3b82f6")
    save_comment_btn.bind("<Enter>", on_enter_save)
    save_comment_btn.bind("<Leave>", on_leave_save)

    # -------------------------- 图片显示/操作区（多图预览功能） --------------------------
    img_frame = tk.LabelFrame(main_card, text="🖼️ 图片附件", bg="#ffffff", fg="#475569",
                              font=("微软雅黑", 14, "bold"), labelanchor="n",
                              padx=20, pady=20, bd=1, relief=tk.FLAT)
    img_frame.pack(fill=tk.X, pady=(0, 30))
    
    # 图片附件隐藏按钮
    img_hide_btn_frame = tk.Frame(img_frame, bg="#ffffff")
    img_hide_btn_frame.pack(fill=tk.X, pady=(0, 10))
    
    img_hide_btn = tk.Button(img_hide_btn_frame, text="隐藏", bg="#94a3b8", fg="#ffffff",
                             font=("微软雅黑", 9, "bold"), bd=0, padx=10, pady=3,
                             relief=tk.FLAT, cursor="hand2")
    img_hide_btn.pack(side=tk.RIGHT)
    
    def toggle_img_hide():
        nonlocal img_hidden
        if not img_hidden:
            # 隐藏图片附件区
            img_hidden = True
            img_hide_btn.config(text="显示", bg="#64748b")
            img_frame.config(pady=5)  # 减少内边距
            # 隐藏内部内容但保留框架
            for widget in img_frame.winfo_children():
                if widget != img_hide_btn_frame:
                    widget.pack_forget()
        else:
            # 显示图片附件区
            img_hidden = False
            img_hide_btn.config(text="隐藏", bg="#94a3b8")
            img_frame.config(pady=20)  # 恢复内边距
            # 重新显示内部内容
            img_help.pack(fill=tk.X, pady=(0, 15))
            img_thumbnail_container.pack(fill=tk.X, pady=(0, 20))
            img_btn_frame.pack(fill=tk.X)
        
        # 保存隐藏状态
        save_hide_state(index, [
            "1" if comment_hidden else "0",
            "1" if img_hidden else "0",
            "1" if video_hidden else "0",
            "1" if file_hidden else "0"
        ])
    
    img_hide_btn.config(command=toggle_img_hide)
    
    # 按钮悬停效果
    def on_enter_img_hide(e):
        img_hide_btn.config(bg="#64748b")
    def on_leave_img_hide(e):
        img_hide_btn.config(bg="#94a3b8" if not img_hidden else "#64748b")
    img_hide_btn.bind("<Enter>", on_enter_img_hide)
    img_hide_btn.bind("<Leave>", on_leave_img_hide)
    
    # 图片说明文字
    img_help = tk.Label(img_frame, text="添加任务相关的截图、照片或其他图片附件。点击缩略图查看原图。", 
                       bg="#ffffff", fg="#94a3b8", font=("微软雅黑", 10),
                       anchor="w", justify="left")
    img_help.pack(fill=tk.X, pady=(0, 15))

    # 图片缩略图容器（水平滚动）
    img_thumbnail_container = tk.Frame(img_frame, bg="#f8fafc", height=150)
    img_thumbnail_container.pack(fill=tk.X, pady=(0, 20))
    img_thumbnail_container.pack_propagate(False)
    
    # 创建水平滚动画布用于显示缩略图
    thumbnail_canvas = tk.Canvas(img_thumbnail_container, bg="#f8fafc", height=150, highlightthickness=0)
    thumbnail_scrollbar = tk.Scrollbar(img_thumbnail_container, orient=tk.HORIZONTAL, command=thumbnail_canvas.xview)
    thumbnail_scrollable_frame = tk.Frame(thumbnail_canvas, bg="#f8fafc")
    
    thumbnail_scrollable_frame.bind(
        "<Configure>",
        lambda e: thumbnail_canvas.configure(scrollregion=thumbnail_canvas.bbox("all"))
    )
    thumbnail_canvas.create_window((0, 0), window=thumbnail_scrollable_frame, anchor="nw")
    thumbnail_canvas.configure(xscrollcommand=thumbnail_scrollbar.set)
    
    thumbnail_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    thumbnail_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # 存储缩略图引用
    thumbnail_images = []
    
    # 加载和显示缩略图
    def load_thumbnails():
        # 清空现有缩略图
        for widget in thumbnail_scrollable_frame.winfo_children():
            widget.destroy()
        thumbnail_images.clear()
        
        if not img_paths:
            # 显示无图片提示
            no_img_label = tk.Label(thumbnail_scrollable_frame, text="暂无图片", bg="#f8fafc", fg="#cbd5e1",
                                   font=("微软雅黑", 12), padx=20, pady=50)
            no_img_label.pack()
            return
        
        for i, img_path in enumerate(img_paths):
            # 创建缩略图框架
            thumb_frame = tk.Frame(thumbnail_scrollable_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
            thumb_frame.pack(side=tk.LEFT, padx=5, pady=5)
            
            # 创建缩略图标签
            thumb_label = tk.Label(thumb_frame, bg="#ffffff", cursor="hand2")
            thumb_label.pack(padx=5, pady=5)
            
            # 绑定点击事件查看原图
            def make_click_func(path=img_path):
                def click_func(event):
                    try:
                        os.startfile(path)
                    except:
                        messagebox.showinfo("图片", f"图片路径：{path}", parent=detail_win)
                return click_func
            
            thumb_label.bind("<Button-1>", make_click_func())
            
            # 加载缩略图
            if Image and ImageTk and os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    # 创建缩略图
                    img.thumbnail((100, 100))
                    tk_img = ImageTk.PhotoImage(img)
                    thumb_label.config(image=tk_img)
                    thumb_label.image = tk_img
                    thumbnail_images.append(tk_img)  # 保持引用
                    
                    # 显示文件名
                    file_name = os.path.basename(img_path)
                    name_label = tk.Label(thumb_frame, text=file_name[:15] + "..." if len(file_name) > 15 else file_name,
                                         bg="#ffffff", fg="#475569", font=("微软雅黑", 8))
                    name_label.pack(pady=(0, 5))
                except Exception as e:
                    thumb_label.config(text=f"❌\n加载失败", fg="#ef4444", font=("微软雅黑", 9))
            else:
                thumb_label.config(text=f"📷\n{i+1}", fg="#cbd5e1", font=("微软雅黑", 12))
    
    # 初始加载缩略图
    load_thumbnails()
    
    # 图片操作按钮区
    img_btn_frame = tk.Frame(img_frame, bg="#ffffff")
    img_btn_frame.pack(fill=tk.X)
    
    # 按钮样式函数
    def create_img_button(parent, text, bg_color, command):
        btn = tk.Button(parent, text=text, bg=bg_color, fg="#ffffff",
                       font=("微软雅黑", 11, "bold"), bd=0, padx=25, pady=10,
                       relief=tk.FLAT, cursor="hand2", command=command,
                       activebackground=darken_color(bg_color),
                       activeforeground="#ffffff")
        # 悬停效果
        def on_enter(e):
            btn.config(bg=darken_color(bg_color))
        def on_leave(e):
            btn.config(bg=bg_color)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # 添加图片按钮
    def add_img_func():
        if not Image or not ImageTk:
            messagebox.showwarning("提示", "未安装Pillow库！请执行 pip install pillow 启用图片功能", parent=detail_win)
            return
        file_paths = filedialog.askopenfilenames(
            title="选择图片文件", parent=detail_win,
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                      ("所有文件", "*.*")]
        )
        if file_paths:
            new_img_paths = []
            for file_path in file_paths:
                # 复制文件到项目文件夹
                if project_path and os.path.exists(project_path):
                    copied_path = copy_file_to_project(file_path, project_path, "images")
                    if copied_path:
                        new_img_paths.append(copied_path)
                    else:
                        new_img_paths.append(file_path)
                else:
                    new_img_paths.append(file_path)
            
            # 添加到现有图片列表
            updated_img_paths = img_paths + new_img_paths
            task_parts = todo_list[index].split("|")
            task_parts = task_parts + [""] * (7 - len(task_parts))
            task_parts[3] = join_path_list(updated_img_paths)
            todo_list[index] = "|".join(task_parts)
            save_todo()
            # 更新显示
            img_paths[:] = updated_img_paths
            load_thumbnails()
            # 成功提示
            success_label = tk.Label(img_frame, text=f"✓ 已添加 {len(file_paths)} 张图片到项目文件夹", bg="#d1fae5", fg="#065f46",
                                    font=("微软雅黑", 9, "bold"), padx=10, pady=5)
            success_label.place(relx=0.5, rely=0.92, anchor="center")
            detail_win.after(2000, success_label.destroy)

    # 删除图片按钮
    def del_img_func():
        if not img_paths:
            messagebox.showwarning("提示", "暂无图片可删除！", parent=detail_win)
            return
        
        # 创建删除对话框
        del_win = tk.Toplevel(detail_win)
        del_win.title("删除图片")
        del_win.geometry("400x300")
        del_win.transient(detail_win)
        del_win.grab_set()
        
        # 创建列表框显示图片
        listbox = tk.Listbox(del_win, selectmode=tk.MULTIPLE, font=("微软雅黑", 10))
        scrollbar = tk.Scrollbar(del_win, orient=tk.VERTICAL, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        
        for i, path in enumerate(img_paths):
            file_name = os.path.basename(path)
            listbox.insert(tk.END, f"{i+1}. {file_name}")
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # 删除按钮
        def confirm_delete():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("提示", "请选择要删除的图片！", parent=del_win)
                return
            
            # 确认删除
            if not messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected_indices)} 张图片吗？", parent=del_win):
                return
            
            # 删除选中的图片
            selected_indices = sorted(selected_indices, reverse=True)  # 从后往前删除
            for idx in selected_indices:
                img_paths.pop(idx)
            
            # 更新数据
            task_parts = todo_list[index].split("|")
            task_parts = task_parts + [""] * (7 - len(task_parts))
            task_parts[3] = join_path_list(img_paths)
            todo_list[index] = "|".join(task_parts)
            save_todo()
            
            # 更新显示
            load_thumbnails()
            del_win.destroy()
            
            # 成功提示
            success_label = tk.Label(img_frame, text=f"✓ 已删除 {len(selected_indices)} 张图片", bg="#fee2e2", fg="#991b1b",
                                    font=("微软雅黑", 9, "bold"), padx=10, pady=5)
            success_label.place(relx=0.5, rely=0.92, anchor="center")
            detail_win.after(2000, success_label.destroy)
        
        btn_frame = tk.Frame(del_win)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        delete_btn = tk.Button(btn_frame, text="删除选中", bg="#ef4444", fg="#ffffff",
                              font=("微软雅黑", 11, "bold"), command=confirm_delete)
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="取消", bg="#64748b", fg="#ffffff",
                              font=("微软雅黑", 11, "bold"), command=del_win.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    add_img_btn = create_img_button(img_btn_frame, "📁 添加图片", "#10b981", add_img_func)
    add_img_btn.pack(side=tk.LEFT, padx=(0, 10))

    del_img_btn = create_img_button(img_btn_frame, "🗑️ 删除图片", "#ef4444", del_img_func)
    del_img_btn.pack(side=tk.LEFT)

    # -------------------------- 视频附件区（多视频缩略图功能） --------------------------
    video_frame = tk.LabelFrame(main_card, text="🎬 视频附件", bg="#ffffff", fg="#475569",
                                font=("微软雅黑", 14, "bold"), labelanchor="n",
                                padx=20, pady=20, bd=1, relief=tk.FLAT)
    video_frame.pack(fill=tk.X, pady=(0, 30))
    
    # 视频附件隐藏按钮
    video_hide_btn_frame = tk.Frame(video_frame, bg="#ffffff")
    video_hide_btn_frame.pack(fill=tk.X, pady=(0, 10))
    
    video_hide_btn = tk.Button(video_hide_btn_frame, text="隐藏", bg="#94a3b8", fg="#ffffff",
                               font=("微软雅黑", 9, "bold"), bd=0, padx=10, pady=3,
                               relief=tk.FLAT, cursor="hand2")
    video_hide_btn.pack(side=tk.RIGHT)
    
    def toggle_video_hide():
        nonlocal video_hidden
        if not video_hidden:
            # 隐藏视频附件区
            video_hidden = True
            video_hide_btn.config(text="显示", bg="#64748b")
            video_frame.config(pady=5)  # 减少内边距
            # 隐藏内部内容但保留框架
            for widget in video_frame.winfo_children():
                if widget != video_hide_btn_frame:
                    widget.pack_forget()
        else:
            # 显示视频附件区
            video_hidden = False
            video_hide_btn.config(text="隐藏", bg="#94a3b8")
            video_frame.config(pady=20)  # 恢复内边距
            # 重新显示内部内容
            video_help.pack(fill=tk.X, pady=(0, 15))
            video_thumbnail_container.pack(fill=tk.X, pady=(0, 20))
            video_btn_frame.pack(fill=tk.X)
        
        # 保存隐藏状态
        save_hide_state(index, [
            "1" if comment_hidden else "0",
            "1" if img_hidden else "0",
            "1" if video_hidden else "0",
            "1" if file_hidden else "0"
        ])
    
    video_hide_btn.config(command=toggle_video_hide)
    
    # 按钮悬停效果
    def on_enter_video_hide(e):
        video_hide_btn.config(bg="#64748b")
    def on_leave_video_hide(e):
        video_hide_btn.config(bg="#94a3b8" if not video_hidden else "#64748b")
    video_hide_btn.bind("<Enter>", on_enter_video_hide)
    video_hide_btn.bind("<Leave>", on_leave_video_hide)
    
    # 视频说明文字
    video_help = tk.Label(video_frame, text="添加任务相关的视频文件（支持MP4、AVI、MOV等格式）。点击缩略图播放原视频。", 
                         bg="#ffffff", fg="#94a3b8", font=("微软雅黑", 10),
                         anchor="w", justify="left")
    video_help.pack(fill=tk.X, pady=(0, 15))

    # 视频缩略图容器（水平滚动）
    video_thumbnail_container = tk.Frame(video_frame, bg="#f8fafc", height=180)
    video_thumbnail_container.pack(fill=tk.X, pady=(0, 20))
    video_thumbnail_container.pack_propagate(False)
    
    # 创建水平滚动画布用于显示视频缩略图
    video_thumbnail_canvas = tk.Canvas(video_thumbnail_container, bg="#f8fafc", height=180, highlightthickness=0)
    video_thumbnail_scrollbar = tk.Scrollbar(video_thumbnail_container, orient=tk.HORIZONTAL, command=video_thumbnail_canvas.xview)
    video_thumbnail_scrollable_frame = tk.Frame(video_thumbnail_canvas, bg="#f8fafc")
    
    video_thumbnail_scrollable_frame.bind(
        "<Configure>",
        lambda e: video_thumbnail_canvas.configure(scrollregion=video_thumbnail_canvas.bbox("all"))
    )
    video_thumbnail_canvas.create_window((0, 0), window=video_thumbnail_scrollable_frame, anchor="nw")
    video_thumbnail_canvas.configure(xscrollcommand=video_thumbnail_scrollbar.set)
    
    video_thumbnail_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    video_thumbnail_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # 存储视频缩略图引用
    video_thumbnail_images = []
    
    # 加载和显示视频缩略图
    def load_video_thumbnails():
        # 清空现有缩略图
        for widget in video_thumbnail_scrollable_frame.winfo_children():
            widget.destroy()
        video_thumbnail_images.clear()
        
        if not video_paths:
            # 显示无视频提示
            no_video_label = tk.Label(video_thumbnail_scrollable_frame, text="暂无视频", bg="#f8fafc", fg="#cbd5e1",
                                     font=("微软雅黑", 12), padx=20, pady=70)
            no_video_label.pack()
            return
        
        for i, video_path in enumerate(video_paths):
            # 创建视频缩略图框架
            video_thumb_frame = tk.Frame(video_thumbnail_scrollable_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
            video_thumb_frame.pack(side=tk.LEFT, padx=5, pady=5)
            
            # 创建视频缩略图标签
            video_thumb_label = tk.Label(video_thumb_frame, bg="#1e293b", fg="#ffffff", cursor="hand2")
            video_thumb_label.pack(padx=5, pady=5)
            
            # 绑定双击事件播放视频
            def make_video_click_func(path=video_path):
                def click_func(event):
                    try:
                        os.startfile(path)
                    except:
                        messagebox.showinfo("视频", f"视频路径：{path}", parent=detail_win)
                return click_func
            
            video_thumb_label.bind("<Double-1>", make_video_click_func())
            
            # 显示视频信息
            if os.path.exists(video_path):
                try:
                    file_name = os.path.basename(video_path)
                    file_size = os.path.getsize(video_path)
                    size_mb = file_size / (1024 * 1024)
                    
                    # 尝试获取视频缩略图
                    thumbnail_path = get_video_thumbnail(video_path)
                    
                    if thumbnail_path and os.path.exists(thumbnail_path) and Image and ImageTk:
                        try:
                            # 加载缩略图
                            img = Image.open(thumbnail_path)
                            # 创建缩略图
                            img.thumbnail((120, 120))
                            tk_img = ImageTk.PhotoImage(img)
                            video_thumb_label.config(image=tk_img, text="")
                            video_thumb_label.image = tk_img
                            video_thumbnail_images.append(tk_img)  # 保持引用
                        except Exception as img_e:
                            # 缩略图加载失败，显示图标
                            video_thumb_label.config(text=f"🎬\n{i+1}", font=("微软雅黑", 16))
                    else:
                        # 没有缩略图，显示图标
                        video_thumb_label.config(text=f"🎬\n{i+1}", font=("微软雅黑", 16))
                    
                    # 显示文件名和大小
                    info_text = f"{file_name[:15]}..." if len(file_name) > 15 else file_name
                    info_text += f"\n{size_mb:.1f} MB"
                    
                    info_label = tk.Label(video_thumb_frame, text=info_text, bg="#ffffff", fg="#475569",
                                         font=("微软雅黑", 8), wraplength=120, justify="center")
                    info_label.pack(pady=(0, 5))
                    
                except Exception as e:
                    video_thumb_label.config(text=f"❌\n加载失败", fg="#ef4444", font=("微软雅黑", 9))
            else:
                video_thumb_label.config(text=f"🎬\n{i+1}", fg="#cbd5e1", font=("微软雅黑", 16))
    
    # 初始加载视频缩略图
    load_video_thumbnails()
    
    # 视频操作按钮区
    video_btn_frame = tk.Frame(video_frame, bg="#ffffff")
    video_btn_frame.pack(fill=tk.X)
    
    # 添加视频按钮
    def add_video_func():
        file_paths = filedialog.askopenfilenames(
            title="选择视频文件", parent=detail_win,
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
                      ("所有文件", "*.*")]
        )
        if file_paths:
            new_video_paths = []
            for file_path in file_paths:
                # 复制文件到项目文件夹
                if project_path and os.path.exists(project_path):
                    copied_path = copy_file_to_project(file_path, project_path, "videos")
                    if copied_path:
                        new_video_paths.append(copied_path)
                    else:
                        new_video_paths.append(file_path)
                else:
                    new_video_paths.append(file_path)
            
            # 添加到现有视频列表
            updated_video_paths = video_paths + new_video_paths
            task_parts = todo_list[index].split("|")
            task_parts = task_parts + [""] * (7 - len(task_parts))
            task_parts[4] = join_path_list(updated_video_paths)
            todo_list[index] = "|".join(task_parts)
            save_todo()
            # 更新显示
            video_paths[:] = updated_video_paths
            load_video_thumbnails()
            # 成功提示
            success_label = tk.Label(video_frame, text=f"✓ 已添加 {len(file_paths)} 个视频到项目文件夹", bg="#d1fae5", fg="#065f46",
                                    font=("微软雅黑", 9, "bold"), padx=10, pady=5)
            success_label.place(relx=0.5, rely=0.92, anchor="center")
            detail_win.after(2000, success_label.destroy)

    # 删除视频按钮
    def del_video_func():
        if not video_paths:
            messagebox.showwarning("提示", "暂无视频可删除！", parent=detail_win)
            return
        
        # 创建删除对话框
        del_win = tk.Toplevel(detail_win)
        del_win.title("删除视频")
        del_win.geometry("400x300")
        del_win.transient(detail_win)
        del_win.grab_set()
        
        # 创建列表框显示视频
        listbox = tk.Listbox(del_win, selectmode=tk.MULTIPLE, font=("微软雅黑", 10))
        scrollbar = tk.Scrollbar(del_win, orient=tk.VERTICAL, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        
        for i, path in enumerate(video_paths):
            file_name = os.path.basename(path)
            listbox.insert(tk.END, f"{i+1}. {file_name}")
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # 删除按钮
        def confirm_delete():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("提示", "请选择要删除的视频！", parent=del_win)
                return
            
            # 确认删除
            if not messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected_indices)} 个视频吗？", parent=del_win):
                return
            
            # 删除选中的视频
            selected_indices = sorted(selected_indices, reverse=True)  # 从后往前删除
            for idx in selected_indices:
                video_paths.pop(idx)
            
            # 更新数据
            task_parts = todo_list[index].split("|")
            task_parts = task_parts + [""] * (7 - len(task_parts))
            task_parts[4] = join_path_list(video_paths)
            todo_list[index] = "|".join(task_parts)
            save_todo()
            
            # 更新显示
            load_video_thumbnails()
            del_win.destroy()
            
            # 成功提示
            success_label = tk.Label(video_frame, text=f"✓ 已删除 {len(selected_indices)} 个视频", bg="#fee2e2", fg="#991b1b",
                                    font=("微软雅黑", 9, "bold"), padx=10, pady=5)
            success_label.place(relx=0.5, rely=0.92, anchor="center")
            detail_win.after(2000, success_label.destroy)
        
        btn_frame = tk.Frame(del_win)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        delete_btn = tk.Button(btn_frame, text="删除选中", bg="#ef4444", fg="#ffffff",
                              font=("微软雅黑", 11, "bold"), command=confirm_delete)
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="取消", bg="#64748b", fg="#ffffff",
                              font=("微软雅黑", 11, "bold"), command=del_win.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    add_video_btn = create_img_button(video_btn_frame, "📁 添加视频", "#8b5cf6", add_video_func)
    add_video_btn.pack(side=tk.LEFT, padx=(0, 10))

    del_video_btn = create_img_button(video_btn_frame, "🗑️ 删除视频", "#ef4444", del_video_func)
    del_video_btn.pack(side=tk.LEFT)

    # -------------------------- 文件附件区（多文件菜单功能） --------------------------
    file_frame = tk.LabelFrame(main_card, text="📎 文件附件", bg="#ffffff", fg="#475569",
                               font=("微软雅黑", 14, "bold"), labelanchor="n",
                               padx=20, pady=20, bd=1, relief=tk.FLAT)
    file_frame.pack(fill=tk.X, pady=(0, 30))
    
    # 文件附件隐藏按钮
    file_hide_btn_frame = tk.Frame(file_frame, bg="#ffffff")
    file_hide_btn_frame.pack(fill=tk.X, pady=(0, 10))
    
    file_hide_btn = tk.Button(file_hide_btn_frame, text="隐藏", bg="#94a3b8", fg="#ffffff",
                              font=("微软雅黑", 9, "bold"), bd=0, padx=10, pady=3,
                              relief=tk.FLAT, cursor="hand2")
    file_hide_btn.pack(side=tk.RIGHT)
    
    def toggle_file_hide():
        nonlocal file_hidden
        if not file_hidden:
            # 隐藏文件附件区
            file_hidden = True
            file_hide_btn.config(text="显示", bg="#64748b")
            file_frame.config(pady=5)  # 减少内边距
            # 隐藏内部内容但保留框架
            for widget in file_frame.winfo_children():
                if widget != file_hide_btn_frame:
                    widget.pack_forget()
        else:
            # 显示文件附件区
            file_hidden = False
            file_hide_btn.config(text="隐藏", bg="#94a3b8")
            file_frame.config(pady=20)  # 恢复内边距
            # 重新显示内部内容
            file_help.pack(fill=tk.X, pady=(0, 15))
            file_tree_frame.pack(fill=tk.BOTH, pady=(0, 20), expand=True)
            file_btn_frame.pack(fill=tk.X)
        
        # 保存隐藏状态
        save_hide_state(index, [
            "1" if comment_hidden else "0",
            "1" if img_hidden else "0",
            "1" if video_hidden else "0",
            "1" if file_hidden else "0"
        ])
    
    file_hide_btn.config(command=toggle_file_hide)
    
    # 按钮悬停效果
    def on_enter_file_hide(e):
        file_hide_btn.config(bg="#64748b")
    def on_leave_file_hide(e):
        file_hide_btn.config(bg="#94a3b8" if not file_hidden else "#64748b")
    file_hide_btn.bind("<Enter>", on_enter_file_hide)
    file_hide_btn.bind("<Leave>", on_leave_file_hide)
    
    # 文件说明文字
    file_help = tk.Label(file_frame, text="添加任务相关的文档、压缩包或其他文件。双击文件项查看原文件。", 
                        bg="#ffffff", fg="#94a3b8", font=("微软雅黑", 10),
                        anchor="w", justify="left")
    file_help.pack(fill=tk.X, pady=(0, 15))

    # 文件列表容器（Treeview菜单）
    file_tree_frame = tk.Frame(file_frame, bg="#f8fafc", height=200)
    file_tree_frame.pack(fill=tk.BOTH, pady=(0, 20), expand=True)
    file_tree_frame.pack_propagate(False)
    
    # 创建Treeview显示文件列表
    file_tree = ttk.Treeview(file_tree_frame, columns=("序号", "文件名", "大小", "类型", "路径"), show="headings", height=8)
    file_tree.heading("序号", text="序号")
    file_tree.heading("文件名", text="文件名")
    file_tree.heading("大小", text="大小")
    file_tree.heading("类型", text="类型")
    file_tree.heading("路径", text="路径")
    
    file_tree.column("序号", width=50, anchor="center")
    file_tree.column("文件名", width=180)
    file_tree.column("大小", width=80, anchor="center")
    file_tree.column("类型", width=80, anchor="center")
    file_tree.column("路径", width=250)
    
    # 添加滚动条
    file_scrollbar = ttk.Scrollbar(file_tree_frame, orient=tk.VERTICAL, command=file_tree.yview)
    file_tree.configure(yscrollcommand=file_scrollbar.set)
    
    file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 双击查看文件
    def on_file_double_click(event):
        item = file_tree.selection()[0]
        path = file_tree.item(item, "values")[4]
        if path and os.path.exists(path):
            try:
                os.startfile(path)
            except:
                messagebox.showinfo("文件", f"文件路径：{path}", parent=detail_win)
    
    file_tree.bind("<Double-1>", on_file_double_click)
    
    # 获取文件类型
    def get_file_type(filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.doc', '.docx']:
            return "Word"
        elif ext in ['.xls', '.xlsx']:
            return "Excel"
        elif ext in ['.ppt', '.pptx']:
            return "PPT"
        elif ext in ['.pdf']:
            return "PDF"
        elif ext in ['.txt']:
            return "文本"
        elif ext in ['.zip', '.rar', '.7z']:
            return "压缩包"
        else:
            return "其他"
    
    # 加载文件列表
    def load_file_list():
        # 清空现有列表
        for item in file_tree.get_children():
            file_tree.delete(item)
        
        if not file_paths:
            # 插入空行提示
            file_tree.insert("", tk.END, values=("", "暂无文件", "", "", ""))
            return
        
        for i, file_path in enumerate(file_paths):
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                size_mb = file_size / (1024 * 1024)
                file_type = get_file_type(file_name)
                file_tree.insert("", tk.END, values=(i+1, file_name, f"{size_mb:.2f} MB", file_type, file_path))
    
    # 初始加载文件列表
    load_file_list()
    
    # 文件操作按钮区
    file_btn_frame = tk.Frame(file_frame, bg="#ffffff")
    file_btn_frame.pack(fill=tk.X)
    
    # 添加文件按钮
    def add_file_func():
        file_paths_selected = filedialog.askopenfilenames(
            title="选择文件", parent=detail_win,
            filetypes=[("所有文件", "*.*")]
        )
        if file_paths_selected:
            new_file_paths = []
            for file_path in file_paths_selected:
                # 复制文件到项目文件夹
                if project_path and os.path.exists(project_path):
                    file_type = get_file_type_from_extension(file_path)
                    copied_path = copy_file_to_project(file_path, project_path, file_type)
                    if copied_path:
                        new_file_paths.append(copied_path)
                    else:
                        new_file_paths.append(file_path)
                else:
                    new_file_paths.append(file_path)
            
            # 添加到现有文件列表
            updated_file_paths = file_paths + new_file_paths
            task_parts = todo_list[index].split("|")
            task_parts = task_parts + [""] * (7 - len(task_parts))
            task_parts[5] = join_path_list(updated_file_paths)
            todo_list[index] = "|".join(task_parts)
            save_todo()
            # 更新显示
            file_paths[:] = updated_file_paths
            load_file_list()
            # 成功提示
            success_label = tk.Label(file_frame, text=f"✓ 已添加 {len(file_paths_selected)} 个文件到项目文件夹", bg="#d1fae5", fg="#065f46",
                                    font=("微软雅黑", 9, "bold"), padx=10, pady=5)
            success_label.place(relx=0.5, rely=0.92, anchor="center")
            detail_win.after(2000, success_label.destroy)

    # 删除文件按钮
    def del_file_func():
        if not file_paths:
            messagebox.showwarning("提示", "暂无文件可删除！", parent=detail_win)
            return
        
        selected_items = file_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请选择要删除的文件！", parent=detail_win)
            return
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected_items)} 个文件吗？", parent=detail_win):
            return
        
        # 获取选中的文件索引
        selected_indices = []
        for item in selected_items:
            values = file_tree.item(item, "values")
            if values[0]:  # 确保不是空行
                idx = int(values[0]) - 1
                selected_indices.append(idx)
        
        # 从后往前删除
        selected_indices = sorted(selected_indices, reverse=True)
        for idx in selected_indices:
            if 0 <= idx < len(file_paths):
                file_paths.pop(idx)
        
        # 更新数据
        task_parts = todo_list[index].split("|")
        task_parts = task_parts + [""] * (7 - len(task_parts))
        task_parts[5] = join_path_list(file_paths)
        todo_list[index] = "|".join(task_parts)
        save_todo()
        
        # 更新显示
        load_file_list()
        
        # 成功提示
        success_label = tk.Label(file_frame, text=f"✓ 已删除 {len(selected_indices)} 个文件", bg="#fee2e2", fg="#991b1b",
                                font=("微软雅黑", 9, "bold"), padx=10, pady=5)
        success_label.place(relx=0.5, rely=0.92, anchor="center")
        detail_win.after(2000, success_label.destroy)

    add_file_btn = create_img_button(file_btn_frame, "📁 添加文件", "#0ea5e9", add_file_func)
    add_file_btn.pack(side=tk.LEFT, padx=(0, 10))

    del_file_btn = create_img_button(file_btn_frame, "🗑️ 删除文件", "#ef4444", del_file_func)
    del_file_btn.pack(side=tk.LEFT)

    # -------------------------- 底部操作按钮区 --------------------------
    bottom_frame = tk.Frame(main_card, bg="#ffffff")
    bottom_frame.pack(fill=tk.X, pady=(20, 0))
    
    # 分隔线
    bottom_separator = tk.Frame(bottom_frame, bg="#f1f5f9", height=2)
    bottom_separator.pack(fill=tk.X, pady=(0, 20))

    # 操作按钮容器
    action_btn_frame = tk.Frame(bottom_frame, bg="#ffffff")
    action_btn_frame.pack(fill=tk.X)
    
    # 关闭按钮（现代化设计）
    def create_action_button(parent, text, bg_color, command):
        btn = tk.Button(parent, text=text, bg=bg_color, fg="#ffffff",
                       font=("微软雅黑", 12, "bold"), bd=0, padx=35, pady=12,
                       relief=tk.FLAT, cursor="hand2", command=command,
                       activebackground=darken_color(bg_color),
                       activeforeground="#ffffff")
        # 悬停效果
        def on_enter(e):
            btn.config(bg=darken_color(bg_color))
        def on_leave(e):
            btn.config(bg=bg_color)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    close_btn = create_action_button(action_btn_frame, "✅ 完成查看", "#64748b", detail_win.destroy)
    close_btn.pack(side=tk.RIGHT)
    
    # 恢复隐藏按钮
    def restore_hidden_func():
        # 恢复所有被隐藏的功能区
        if comment_hidden:
            toggle_comment_hide()
        if img_hidden:
            toggle_img_hide()
        if video_hidden:
            toggle_video_hide()
        if file_hidden:
            toggle_file_hide()
        
        # 显示成功提示
        success_label = tk.Label(bottom_frame, text="✓ 已恢复所有隐藏的功能区", bg="#d1fae5", fg="#065f46",
                                font=("微软雅黑", 9, "bold"), padx=10, pady=5)
        success_label.place(relx=0.5, rely=0.95, anchor="center")
        detail_win.after(2000, success_label.destroy)
    
    restore_btn = create_action_button(action_btn_frame, "🔄 恢复隐藏", "#0ea5e9", restore_hidden_func)
    restore_btn.pack(side=tk.RIGHT, padx=(0, 10))
    
    # 标记完成/未完成按钮
    def toggle_status_func():
        task_parts = todo_list[index].split("|")
        task_parts = task_parts + [""] * (7 - len(task_parts))
        new_status = "False" if task_parts[1] == "True" else "True"
        task_parts[1] = new_status
        todo_list[index] = "|".join(task_parts)
        save_todo()
        update_main_ui()
        detail_win.destroy()
        messagebox.showinfo("成功", f"任务已标记为{'已完成' if new_status == 'True' else '未完成'}！", parent=root_window)
    
    status_btn_text = "标记为未完成" if status == "True" else "标记为已完成"
    status_btn_color = "#f97316" if status == "True" else "#10b981"
    status_btn = create_action_button(action_btn_frame, status_btn_text, status_btn_color, toggle_status_func)
    status_btn.pack(side=tk.RIGHT, padx=(0, 10))

# -------------------------- 其他功能函数 --------------------------
def add_todo():
    """添加待办并创建项目文件夹"""
    global todo_list, root_window
    try:
        task_content = simpledialog.askstring("添加待办", "请输入任务标题：", parent=root_window)
        if task_content is None or task_content.strip() == "":
            return
        
        # 获取当前时间（精确到日）
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 创建新任务（7个字段，第7个是项目文件夹路径），在标题后添加时间
        task_title_with_time = f"{task_content.strip()} ({current_time})"
        new_task = f"{task_title_with_time}|False|||||"
        todo_list.append(new_task)
        
        # 获取任务索引
        task_index = len(todo_list) - 1
        
        # 创建项目文件夹（使用原始标题，不含时间）
        project_path = create_project_folder(task_index, task_content.strip())
        
        if project_path:
            # 更新任务数据，添加项目文件夹路径
            task_parts = new_task.split("|")
            task_parts = task_parts + [""] * (7 - len(task_parts))
            task_parts[6] = project_path
            todo_list[task_index] = "|".join(task_parts)
            
            # 保存数据
            save_todo()
            update_main_ui()
            messagebox.showinfo("成功", f"✅ 任务「{task_content.strip()}」添加成功！\n添加时间：{current_time}\n项目文件夹已创建：{project_path}", parent=root_window)
        else:
            # 项目文件夹创建失败，但仍然保存任务
            save_todo()
            update_main_ui()
            messagebox.showwarning("警告", f"任务「{task_content.strip()}」添加成功，但项目文件夹创建失败。\n添加时间：{current_time}", parent=root_window)
            
    except Exception as e:
        messagebox.showerror("错误", f"添加待办失败：{str(e)}", parent=root_window)

def delete_todo():
    """删除待办"""
    global todo_list, root_window
    try:
        if not todo_list:
            messagebox.showerror("错误", "暂无待办任务！", parent=root_window)
            return
        index_input = simpledialog.askstring("删除待办", "请输入任务序号：", parent=root_window)
        if index_input is None or index_input.strip() == "":
            return
        try:
            index = int(index_input) - 1
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字序号！", parent=root_window)
            return
        if 0 <= index < len(todo_list):
            # 获取任务数据
            task_parts = todo_list[index].split("|")
            task_parts = task_parts + [""] * (7 - len(task_parts))
            title = task_parts[0]
            project_path = task_parts[6]  # 第7个字段是项目文件夹路径
            
            # 删除项目文件夹（如果存在）
            folder_deleted = False
            if project_path and os.path.exists(project_path):
                try:
                    import shutil
                    shutil.rmtree(project_path)
                    folder_deleted = True
                except Exception as folder_e:
                    print(f"删除项目文件夹失败: {folder_e}")
                    # 继续删除任务，即使文件夹删除失败
            
            # 删除任务
            todo_list.pop(index)
            save_todo()
            update_main_ui()
            
            # 显示成功消息
            if folder_deleted:
                messagebox.showinfo("成功", f"✅ 任务「{title}」已删除！\n项目文件夹也已删除：{project_path}", parent=root_window)
            else:
                messagebox.showinfo("成功", f"✅ 任务「{title}」已删除！", parent=root_window)
        else:
            messagebox.showerror("错误", "序号不存在！", parent=root_window)
    except Exception as e:
        messagebox.showerror("错误", f"删除待办失败：{str(e)}", parent=root_window)

def edit_todo():
    """修改待办"""
    global todo_list, root_window
    try:
        if not todo_list:
            messagebox.showerror("错误", "暂无待办任务！", parent=root_window)
            return
        index_input = simpledialog.askstring("修改待办", "请输入任务序号：", parent=root_window)
        if index_input is None or index_input.strip() == "":
            return
        try:
            index = int(index_input) - 1
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字序号！", parent=root_window)
            return
        if 0 <= index < len(todo_list):
            old_parts = todo_list[index].split("|")
            old_title_with_time = old_parts[0] if len(old_parts)>=1 else "无标题任务"
            
            # 从标题中提取原始标题（去掉时间部分）
            # 假设时间格式为 "标题 (YYYY-MM-DD)"
            import re
            time_pattern = r'\s*\(\d{4}-\d{2}-\d{2}\)$'
            old_title = re.sub(time_pattern, '', old_title_with_time)
            
            new_title = simpledialog.askstring("修改标题", f"当前标题：{old_title}\n请输入新标题：", parent=root_window)
            if new_title is None or new_title.strip() == "":
                return
            
            # 从原标题中提取时间信息（如果有的话）
            time_match = re.search(r'\((\d{4}-\d{2}-\d{2})\)$', old_title_with_time)
            if time_match:
                # 保留原来的时间信息
                time_str = time_match.group(1)
                new_title_with_time = f"{new_title.strip()} ({time_str})"
            else:
                # 如果没有时间信息，添加当前时间
                current_time = datetime.datetime.now().strftime("%Y-%m-%d")
                new_title_with_time = f"{new_title.strip()} ({current_time})"
            
            old_parts[0] = new_title_with_time
            todo_list[index] = "|".join(old_parts)
            save_todo()
            update_main_ui()
            messagebox.showinfo("成功", "✅ 任务标题已修改！", parent=root_window)
        else:
            messagebox.showerror("错误", "序号不存在！", parent=root_window)
    except Exception as e:
        messagebox.showerror("错误", f"修改待办失败：{str(e)}", parent=root_window)

def complete_todo():
    """标记完成"""
    global todo_list, root_window
    try:
        if not todo_list:
            messagebox.showerror("错误", "暂无待办任务！", parent=root_window)
            return
        index_input = simpledialog.askstring("标记完成", "请输入任务序号：", parent=root_window)
        if index_input is None or index_input.strip() == "": 
            return
        try:
            index = int(index_input) - 1
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字序号！", parent=root_window)
            return
        if 0 <= index < len(todo_list):
            parts = todo_list[index].split("|")
            parts = parts + [""] * (6 - len(parts))
            new_status = "True" if parts[1] == "False" else "False"
            parts[1] = new_status
            todo_list[index] = "|".join(parts)
            save_todo()
            update_main_ui()
            status_text = "已完成" if new_status=="True" else "未完成"
            messagebox.showinfo("成功", f"✅ 任务已标记为{status_text}！", parent=root_window)
        else:
            messagebox.showerror("错误", "序号不存在！", parent=root_window)
    except Exception as e:
        messagebox.showerror("错误", f"标记完成失败：{str(e)}", parent=root_window)

def toggle_hide_completed():
    """切换隐藏/显示已完成任务"""
    global hide_completed, root_window
    try:
        # 切换隐藏状态
        hide_completed = not hide_completed
        
        # 更新UI
        update_main_ui()
        
        # 返回新状态以便更新按钮文本
        return hide_completed
    except Exception as e:
        messagebox.showerror("错误", f"切换隐藏状态失败：{str(e)}", parent=root_window)
        return hide_completed

def hide_completed_func():
    """隐藏/显示已完成任务的包装函数，用于动态更新按钮文本"""
    hide_state = toggle_hide_completed()
    # 返回新状态（这里只执行切换，按钮文本更新在按钮创建时处理）
    return hide_state

def exit_app():
    """退出应用"""
    global todo_list, root_window
    try:
        if messagebox.askyesno("退出", "确定退出？所有任务会自动保存", parent=root_window):
            save_todo()
            save_window_config()
            root_window.destroy()
    except Exception as e:
        messagebox.showerror("错误", f"退出失败：{str(e)}", parent=root_window)

# -------------------------- 首页UI --------------------------
def create_main_ui():
    global root_window, task_text_widget, todo_list
    # 初始化全局变量
    root_window = tk.Tk()
    root_window.title("KP项目管理")
    
    # 加载保存的窗口配置
    saved_geometry = load_window_config()
    root_window.geometry(saved_geometry)
    
    root_window.resizable(True, True)
    root_window.config(bg="#f5f5f5")
    
    # 加载待办数据
    load_todo()
    
    # 标题栏
    title_bar = tk.Frame(root_window, bg="#2196F3", height=80)
    title_bar.pack(fill=tk.X)
    title_bar.pack_propagate(False)
    
    title_label = tk.Label(title_bar, text="📋 KP项目管理", bg="#2196F3", fg="#ffffff",
                           font=("微软雅黑", 24, "bold"))
    title_label.pack(expand=True)
    
    # 任务显示区
    task_container = tk.Frame(root_window, bg="#f5f5f5", padx=15, pady=15)
    task_container.pack(fill=tk.BOTH, expand=True)
    
    task_card = tk.Frame(task_container, bg="#ffffff", bd=0, 
                         highlightbackground="#e0e0e0", highlightthickness=1)
    task_card.pack(fill=tk.BOTH, expand=True)
    
    task_scrollbar = tk.Scrollbar(task_card, bg="#f5f5f5", width=12, bd=0)
    task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    task_text_widget = tk.Text(task_card, bg="#ffffff", fg="#333333",
                        font=("微软雅黑", 12), wrap=tk.WORD,
                        yscrollcommand=task_scrollbar.set,
                        bd=0, padx=20, pady=20)
    task_text_widget.pack(fill=tk.BOTH, expand=True)
    task_scrollbar.config(command=task_text_widget.yview)
    
    # 底部容器（包含功能按钮区和退出按钮）
    bottom_container = tk.Frame(root_window, bg="#f5f5f5")
    bottom_container.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)
    
    # 功能按钮区
    btn_container = tk.Frame(bottom_container, bg="#ffffff", padx=15, pady=15)
    btn_container.pack(fill=tk.X, pady=(0, 0))
    
    # 统一按钮创建函数（支持动态文本更新）
    def create_func_button(parent, text, bg_color, func, update_text_func=None):
        btn = tk.Button(parent, text=text, bg=bg_color, fg="#ffffff",
                        font=("微软雅黑", 12, "bold"),
                        bd=0, padx=10, pady=8,
                        relief=tk.FLAT, cursor="hand2")
        # hover效果
        def on_enter(e):
            btn.config(bg=darken_color(bg_color))
        def on_leave(e):
            btn.config(bg=bg_color)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        # 支持动态更新按钮文本的函数
        def wrapped_func():
            if update_text_func:
                new_text = update_text_func()
                btn.config(text=new_text)
            if func:
                func()
        
        btn.config(command=wrapped_func if update_text_func else func)
        return btn
    
    # 第一行按钮
    row1 = tk.Frame(btn_container, bg="#ffffff")
    row1.pack(fill=tk.X, pady=(0, 10))
    
    btn1 = create_func_button(row1, "查看待办", "#2196F3", show_task_detail)
    btn1.pack(side=tk.LEFT, expand=True, padx=5)
    
    btn2 = create_func_button(row1, "添加待办", "#4CAF50", add_todo)
    btn2.pack(side=tk.LEFT, expand=True, padx=5)
    
    btn3 = create_func_button(row1, "删除待办", "#FF5252", delete_todo)
    btn3.pack(side=tk.LEFT, expand=True, padx=5)
    
    # 第二行按钮
    row2 = tk.Frame(btn_container, bg="#ffffff")
    row2.pack(fill=tk.X)
    
    btn4 = create_func_button(row2, "修改待办", "#FF9800", edit_todo)
    btn4.pack(side=tk.LEFT, expand=True, padx=5)
    
    btn5 = create_func_button(row2, "标记完成", "#00C851", complete_todo)
    btn5.pack(side=tk.LEFT, expand=True, padx=5)
    
    # 隐藏/显示已完成按钮（可切换）- 使用统一按钮创建函数
    def get_hide_completed_text():
        return "恢复全部" if hide_completed else "隐藏完成"
    
    btn6 = create_func_button(row2, get_hide_completed_text(), "#9C27B0", hide_completed_func, get_hide_completed_text)
    btn6.pack(side=tk.LEFT, expand=True, padx=5)
    
    # 退出按钮（在功能按钮区下方）
    exit_btn = tk.Button(bottom_container, text="🚪 退出应用", bg="#607D8B", fg="#ffffff",
                         font=("微软雅黑", 14, "bold"), bd=0, height=2,
                         relief=tk.FLAT, cursor="hand2", command=exit_app)
    exit_btn.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    # 初始化任务显示
    update_main_ui()
    
    # 提示Pillow未安装
    if not Image:
        messagebox.showwarning("提示", "未检测到Pillow库，图片功能已禁用！\n可执行 pip install pillow 启用图片功能。", parent=root_window)
    
    # 窗口大小变化响应函数 - 确保按钮大小一致对称且跟随窗口变化
    def on_window_resize(event):
        # 获取当前窗口宽度
        win_width = root_window.winfo_width()
        
        # 定义所有功能按钮的列表
        all_func_buttons = [btn1, btn2, btn3, btn4, btn5, btn6]
        
        # 根据窗口宽度动态调整按钮大小和布局
        if win_width < 400:
            # 超小屏幕：更小的按钮和边距，保持对称
            font_size = 9
            padx_val = 4
            pady_val = 4
            container_pad = 6
        elif win_width < 500:
            # 小屏幕：适中调整
            font_size = 10
            padx_val = 6
            pady_val = 6
            container_pad = 8
        elif win_width < 600:
            # 中等屏幕
            font_size = 11
            padx_val = 8
            pady_val = 6
            container_pad = 10
        elif win_width < 700:
            # 大屏幕
            font_size = 12
            padx_val = 10
            pady_val = 8
            container_pad = 12
        else:
            # 超大屏幕：最大设置
            font_size = 13
            padx_val = 12
            pady_val = 10
            container_pad = 15
        
        # 统一调整所有功能按钮的样式（确保大小一致对称）
        for btn in all_func_buttons:
            btn.config(font=("微软雅黑", font_size, "bold"), padx=padx_val, pady=pady_val)
        
        # 调整退出按钮
        exit_font_size = font_size + 2  # 退出按钮比功能按钮稍大
        exit_btn.config(font=("微软雅黑", exit_font_size, "bold"), padx=padx_val * 2, pady=pady_val)
        
        # 调整容器边距
        btn_container.config(padx=container_pad, pady=container_pad)
        task_container.config(padx=container_pad, pady=container_pad)
        bottom_container.config(padx=container_pad)
        
        # 更新布局，确保按钮均匀分布
        btn_container.update_idletasks()
        row1.update_idletasks()
        row2.update_idletasks()
        
        # 延迟保存窗口配置，避免频繁保存
        if hasattr(root_window, '_save_timer'):
            root_window.after_cancel(root_window._save_timer)
        root_window._save_timer = root_window.after(500, save_window_config)  # 500ms后保存
    
    # 绑定窗口大小变化事件
    root_window.bind("<Configure>", on_window_resize)
    
    # 窗口关闭协议处理函数
    def on_window_close():
        # 保存窗口配置
        save_window_config()
        # 保存待办数据
        save_todo()
        # 销毁窗口
        root_window.destroy()
    
    # 设置窗口关闭协议
    root_window.protocol("WM_DELETE_WINDOW", on_window_close)
    
    # 启动主循环
    root_window.mainloop()

# -------------------------- 程序入口 --------------------------
if __name__ == "__main__":
    try:
        create_main_ui()
    except Exception as e:
        # 捕获启动异常
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("启动异常", f"程序启动失败：{str(e)}\n请检查Python环境是否正常。")
        root.destroy()
