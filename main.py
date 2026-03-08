import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import os
import sys
from pystray import Icon, MenuItem as Item, Menu
from PIL import Image
import ctypes

class ShutdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows定时关机/重启工具")
        self.root.geometry("520x450")
        self.root.resizable(False, False)
        
        self.task_running = False
        self.shutdown_time = None
        self.operation_type = "shutdown"
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="定时关机/重启设置", font=("微软雅黑", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        date_frame = ttk.LabelFrame(main_frame, text="日期设置", padding="8")
        date_frame.pack(fill=tk.X, pady=(0, 8))
        
        now = datetime.now()
        
        ttk.Label(date_frame, text="年:").grid(row=0, column=0, padx=5, pady=5)
        self.year_var = tk.StringVar(value=str(now.year))
        year_entry = ttk.Entry(date_frame, textvariable=self.year_var, width=8)
        year_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(date_frame, text="月:").grid(row=0, column=2, padx=5, pady=5)
        self.month_var = tk.StringVar(value=str(now.month).zfill(2))
        month_entry = ttk.Entry(date_frame, textvariable=self.month_var, width=5)
        month_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(date_frame, text="日:").grid(row=0, column=4, padx=5, pady=5)
        self.day_var = tk.StringVar(value=str(now.day).zfill(2))
        day_entry = ttk.Entry(date_frame, textvariable=self.day_var, width=5)
        day_entry.grid(row=0, column=5, padx=5, pady=5)
        
        time_frame = ttk.LabelFrame(main_frame, text="时间设置", padding="8")
        time_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(time_frame, text="时:").grid(row=0, column=0, padx=5, pady=5)
        self.hour_var = tk.StringVar(value=str(now.hour).zfill(2))
        hour_entry = ttk.Entry(time_frame, textvariable=self.hour_var, width=5)
        hour_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(time_frame, text="分:").grid(row=0, column=2, padx=5, pady=5)
        self.minute_var = tk.StringVar(value=str(now.minute).zfill(2))
        minute_entry = ttk.Entry(time_frame, textvariable=self.minute_var, width=5)
        minute_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(time_frame, text="秒:").grid(row=0, column=4, padx=5, pady=5)
        self.second_var = tk.StringVar(value="00")
        second_entry = ttk.Entry(time_frame, textvariable=self.second_var, width=5)
        second_entry.grid(row=0, column=5, padx=5, pady=5)
        
        operation_frame = ttk.LabelFrame(main_frame, text="操作类型", padding="8")
        operation_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.operation_var = tk.StringVar(value="shutdown")
        shutdown_radio = ttk.Radiobutton(operation_frame, text="关机", variable=self.operation_var, value="shutdown")
        shutdown_radio.pack(side=tk.LEFT, padx=30)
        restart_radio = ttk.Radiobutton(operation_frame, text="重启", variable=self.operation_var, value="restart")
        restart_radio.pack(side=tk.LEFT, padx=30)
        
        self.status_var = tk.StringVar(value="等待设置任务...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="blue")
        status_label.pack(pady=(0, 3))
        
        self.countdown_var = tk.StringVar(value="")
        countdown_label = ttk.Label(main_frame, textvariable=self.countdown_var, foreground="red", font=("微软雅黑", 9, "bold"))
        countdown_label.pack(pady=(0, 8))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.confirm_btn = ttk.Button(button_frame, text="确定", command=self.start_task)
        self.confirm_btn.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True, ipady=6)
        
        self.cancel_btn = ttk.Button(button_frame, text="撤销", command=self.cancel_task, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.RIGHT, padx=15, fill=tk.X, expand=True, ipady=6)
        
        self.setup_tray()
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.root.bind("<Unmap>", lambda e: self.minimize_to_tray() if self.root.state() == 'iconic' else None)
        
    def validate_time(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            second = int(self.second_var.get())
            
            target_time = datetime(year, month, day, hour, minute, second)
            now = datetime.now()
            
            if target_time <= now:
                messagebox.showerror("错误", "设置的时间必须晚于当前时间！")
                return None
                
            return target_time
            
        except ValueError as e:
            messagebox.showerror("错误", f"时间格式不正确：{str(e)}")
            return None
    
    def start_task(self):
        target_time = self.validate_time()
        if not target_time:
            return
            
        self.shutdown_time = target_time
        self.operation_type = self.operation_var.get()
        self.task_running = True
        
        self.confirm_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        
        operation_text = "关机" if self.operation_type == "shutdown" else "重启"
        self.status_var.set(f"已设置定时{operation_text}任务，执行时间：{target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        threading.Thread(target=self.countdown_task, daemon=True).start()
        
    def countdown_task(self):
        while self.task_running:
            now = datetime.now()
            remaining = self.shutdown_time - now
            
            if remaining.total_seconds() <= 0:
                self.execute_operation()
                break
                
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            seconds = remaining.seconds % 60
            
            countdown_text = f"剩余时间：{remaining.days}天 {hours:02d}:{minutes:02d}:{seconds:02d}"
            self.countdown_var.set(countdown_text)
            
            threading.Event().wait(1)
    
    def execute_operation(self):
        self.status_var.set("正在执行操作...")
        self.root.update()
        
        if self.operation_type == "shutdown":
            os.system("shutdown /s /t 1")
        else:
            os.system("shutdown /r /t 1")
            
        self.root.quit()
    
    def cancel_task(self):
        self.task_running = False
        self.confirm_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.status_var.set("任务已取消")
        self.countdown_var.set("")
        
        os.system("shutdown /a")
        
    def create_icon(self):
        icon = Image.new('RGB', (64, 64), color = (73, 109, 137))
        return icon
        
    def setup_tray(self):
        menu = Menu(
            Item('显示窗口', self.restore_window),
            Item('退出程序', self.quit_app)
        )
        self.icon = Icon("定时关机工具", self.create_icon(), "定时关机/重启工具", menu)
        self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.tray_thread.start()
        
    def minimize_to_tray(self):
        self.root.withdraw()
        
    def restore_window(self, icon, item):
        self.root.after(0, self.root.deiconify)
        
    def quit_app(self, icon, item):
        self.task_running = False
        self.icon.stop()
        self.root.quit()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ShutdownApp(root)
    root.mainloop()
