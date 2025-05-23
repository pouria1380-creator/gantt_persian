import tkinter as tk
import customtkinter as ctk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import jdatetime as jdt
import matplotlib.font_manager as fm
from bidi.algorithm import get_display
from arabic_reshaper import reshape

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

try:
    font_path = "B-NAZANIN.TTF"
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    print(f"Error loading font: {e}")


def persian_text(text):
    reshaped_text = reshape(text)
    return get_display(reshaped_text)


class GanttChartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("تولید کننده نمودار گانت پیشرفته")
        self.root.geometry("1200x800")
        self.create_frames()
        self.tasks = []
        self.figure = None
        self.canvas = None
        self.ax = None
        self.current_vline = None
        self.vline_text = None
        self.dragging_vline = False
        self.set_default_dates()

    def create_frames(self):
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.pack(pady=10, padx=10, fill="x")

        self.button_frame = ctk.CTkFrame(self.root)
        self.button_frame.pack(pady=5, padx=10, fill="x")

        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(pady=10, padx=10, expand=True, fill="both")

        self.tasks_tab = self.tabview.add(persian_text("تسک‌ها"))
        self.chart_tab = self.tabview.add(persian_text("نمودار گانت"))

        self.configure_tasks_tab()
        self.configure_chart_tab()
        self.create_input_widgets()
        self.create_action_buttons()

    def configure_tasks_tab(self):
        self.tasks_canvas = ctk.CTkCanvas(self.tasks_tab)
        self.tasks_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(self.tasks_tab, orientation="vertical", command=self.tasks_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.tasks_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.tasks_canvas.bind('<Configure>',
                               lambda e: self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox("all")))

        self.tasks_frame = ctk.CTkFrame(self.tasks_canvas)
        self.tasks_canvas.create_window((0, 0), window=self.tasks_frame, anchor="nw")

    def configure_chart_tab(self):
        self.chart_frame = ctk.CTkFrame(self.chart_tab)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.chart_placeholder = ctk.CTkLabel(
            self.chart_frame,
            text=persian_text("برای مشاهده نمودار گانت، آن را تولید کنید"),
            font=("B-NAZANIN", 14)
        )
        self.chart_placeholder.pack(expand=True)

    def set_default_dates(self):
        today_shamsi = jdt.datetime.now().strftime("%Y-%m-%d")
        next_week_shamsi = (jdt.datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.start_date_entry.delete(0, "end")
        self.start_date_entry.insert(0, today_shamsi)
        self.end_date_entry.delete(0, "end")
        self.end_date_entry.insert(0, next_week_shamsi)

    def create_input_widgets(self):
        for i in range(8):
            self.input_frame.grid_columnconfigure(i, weight=1 if i % 2 == 1 else 0)

        ctk.CTkLabel(self.input_frame, text=persian_text("نام تسک:"), font=("B-NAZANIN", 14)).grid(row=0, column=0,
                                                                                                   padx=5, pady=5,
                                                                                                   sticky="e")
        self.task_name_entry = ctk.CTkEntry(self.input_frame, font=("B-NAZANIN", 14))
        self.task_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.input_frame, text=persian_text("تاریخ شروع (شمسی):"), font=("B-NAZANIN", 14)).grid(row=0,
                                                                                                             column=2,
                                                                                                             padx=5,
                                                                                                             pady=5,
                                                                                                             sticky="e")
        self.start_date_entry = ctk.CTkEntry(self.input_frame, font=("B-NAZANIN", 14), placeholder_text="YYYY-MM-DD")
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.input_frame, text=persian_text("تاریخ پایان (شمسی):"), font=("B-NAZANIN", 14)).grid(row=0,
                                                                                                              column=4,
                                                                                                              padx=5,
                                                                                                              pady=5,
                                                                                                              sticky="e")
        self.end_date_entry = ctk.CTkEntry(self.input_frame, font=("B-NAZANIN", 14), placeholder_text="YYYY-MM-DD")
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.input_frame, text=persian_text("رنگ:"), font=("B-NAZANIN", 14)).grid(row=0, column=6, padx=5,
                                                                                               pady=5, sticky="e")
        self.color_combobox = ctk.CTkComboBox(
            self.input_frame,
            values=["آبی", "سبز", "قرمز", "نارنجی", "بنفش", "زرد", "فیروزه‌ای", "ارغوانی"],
            width=100,
            font=("B-NAZANIN", 14)
        )
        self.color_combobox.grid(row=0, column=7, padx=5, pady=5, sticky="w")
        self.color_combobox.set("آبی")

    def create_action_buttons(self):
        button_config = {
            "width": 120,
            "height": 32,
            "corner_radius": 8,
            "font": ("B-NAZANIN", 14)
        }

        self.add_button = ctk.CTkButton(
            self.button_frame,
            text="➕ افزودن تسک",
            command=self.add_task,
            **button_config
        )
        self.add_button.pack(side="right", padx=5, pady=5)

        self.generate_button = ctk.CTkButton(
            self.button_frame,
            text="📊 تولید نمودار",
            command=self.generate_gantt,
            **button_config
        )
        self.generate_button.pack(side="right", padx=5, pady=5)

        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="🧹 پاک کردن همه",
            command=self.clear_all,
            fg_color="#D35B58",
            hover_color="#C77C78",
            **button_config
        )
        self.clear_button.pack(side="right", padx=5, pady=5)

        self.export_button = ctk.CTkButton(
            self.button_frame,
            text="💾 ذخیره PNG",
            command=self.export_chart,
            **button_config
        )
        self.export_button.pack(side="right", padx=5, pady=5)

    def add_task(self):
        try:
            task_name = self.task_name_entry.get().strip()
            if not task_name:
                raise ValueError("نام تسک نمی‌تواند خالی باشد")

            start_date_str = self.start_date_entry.get().strip()
            end_date_str = self.end_date_entry.get().strip()

            try:
                start_jdate = jdt.datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError:
                raise ValueError("فرمت تاریخ شروع نامعتبر است. دقت کنید 12 ماه داریم و حداکثر 31 روز در6 ماه اول سال و 30 روز در 6 ماه دوم سال")
            try:
                end_jdate = jdt.datetime.strptime(end_date_str, "%Y-%m-%d")
            except ValueError:
                raise ValueError("فرمت تاریخ پایان نامعتبر است. دقت کنید 12 ماه داریم و حداکثر 31 روز در6 ماه اول سال و 30 روز در 6 ماه دوم سال")

            start_date = start_jdate.togregorian()
            end_date = end_jdate.togregorian()

            if end_date < start_date:
                raise ValueError("تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد")

            duration = (end_date - start_date).days + 1

            color_map = {
                "آبی": "blue",
                "سبز": "green",
                "قرمز": "red",
                "نارنجی": "orange",
                "بنفش": "purple",
                "زرد": "yellow",
                "فیروزه‌ای": "cyan",
                "ارغوانی": "magenta"
            }
            color = color_map[self.color_combobox.get()]

            task = {
                'name': task_name,
                'start': start_date,
                'end': end_date,
                'color': color,
                'duration': duration
            }

            self.tasks.append(task)
            self.display_task(task)
            self.task_name_entry.delete(0, "end")
            self.set_default_dates()

        except Exception as e:
            self.show_error(str(e))

    def display_task(self, task):
        task_frame = ctk.CTkFrame(self.tasks_frame)
        task_frame.pack(fill="x", pady=2, padx=5)

        for i in range(5):
            task_frame.grid_columnconfigure(i, weight=1)

        name_label = ctk.CTkLabel(
            task_frame,
            text=task['name'],
            width=200,
            anchor="w",
            font=("B-NAZANIN", 14)
        )
        name_label.grid(row=0, column=0, padx=5, sticky="e")

        start_jdate = jdt.datetime.fromgregorian(date=task['start'])
        start_str = start_jdate.strftime("%Y-%m-%d")
        start_label = ctk.CTkLabel(
            task_frame,
            text=f"شروع: {start_str}",
            anchor="w",
            font=("B-NAZANIN", 14)
        )
        start_label.grid(row=0, column=1, padx=5, sticky="e")

        end_jdate = jdt.datetime.fromgregorian(date=task['end'])
        end_str = end_jdate.strftime("%Y-%m-%d")
        end_label = ctk.CTkLabel(
            task_frame,
            text=f"پایان: {end_str}",
            anchor="w",
            font=("B-NAZANIN", 14)
        )
        end_label.grid(row=0, column=2, padx=5, sticky="e")

        duration_label = ctk.CTkLabel(
            task_frame,
            text=f"مدت: {task['duration']} روز",
            anchor="w",
            font=("B-NAZANIN", 14)
        )
        duration_label.grid(row=0, column=3, padx=5, sticky="e")

        color_frame = ctk.CTkFrame(
            task_frame,
            width=20,
            height=20,
            fg_color=task['color'],
            corner_radius=3
        )
        color_frame.grid(row=0, column=4, padx=5, sticky="e")

        delete_btn = ctk.CTkButton(
            task_frame,
            text="✕",
            width=30,
            fg_color="transparent",
            hover_color="#D35B58",
            text_color=("gray10", "gray90"),
            command=lambda: self.remove_task(task_frame, task),
            font=("B-NAZANIN", 14)
        )
        delete_btn.grid(row=0, column=5, padx=5, sticky="e")
        self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox("all"))

    def remove_task(self, task_frame, task):
        task_frame.destroy()
        self.tasks.remove(task)

    def generate_gantt(self):
        if not self.tasks:
            self.show_error("تسکی برای نمایش وجود ندارد. لطفا ابتدا تسک اضافه کنید.")
            return

        self.tabview.set(persian_text("نمودار گانت"))

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            plt.close(self.figure)

        fig_height = max(4, len(self.tasks) * 0.6)
        self.figure, self.ax = plt.subplots(figsize=(12, fig_height))
        self.figure.subplots_adjust(right=0.9)

        for i, task in enumerate(self.tasks):
            start_date = mdates.date2num(task['start'])
            end_date = mdates.date2num(task['end'])
            duration = end_date - start_date
            task_name = persian_text(task['name'])

            bar = self.ax.barh(
                task_name,
                duration,
                left=start_date,
                height=0.6,
                color=task['color'],
                edgecolor='black',
                alpha=0.8
            )

            mid_point = start_date + duration / 2
            duration_text = persian_text(f"{task['duration']} روز")
            self.ax.text(
                mid_point, i,
                duration_text,
                ha='center', va='center',
                color='black',
                fontsize=36,
                fontweight='bold'
            )

        all_dates = [task['start'] for task in self.tasks] + [task['end'] for task in self.tasks]
        min_date_gregorian = min(all_dates)
        max_date_gregorian = max(all_dates)
        min_date_shamsi = jdt.datetime.fromgregorian(date=min_date_gregorian)
        max_date_shamsi = jdt.datetime.fromgregorian(date=max_date_gregorian)
        total_days_shamsi = (max_date_shamsi - min_date_shamsi).days + 1

        self.ax.xaxis_date()
        self.ax.set_axisbelow(True)
        self.ax.yaxis.set_label_position("right")
        self.ax.yaxis.tick_right()

        if total_days_shamsi <= 8:
            self.ax.xaxis.set_major_locator(mdates.DayLocator())
            self.ax.xaxis.set_major_formatter(plt.FuncFormatter(
                lambda x, _: persian_text(jdt.datetime.fromgregorian(date=mdates.num2date(x)).strftime("%A"))
            ))
            self.ax.text(mdates.date2num(min_date_gregorian), -1.5,
                         persian_text(min_date_shamsi.strftime("%b %Y")),
                         ha='left', va='top')
            self.ax.text(mdates.date2num(max_date_gregorian), -1.5,
                         persian_text(max_date_shamsi.strftime("%b %Y")),
                         ha='right', va='top')
        elif total_days_shamsi <= 32:
            self.ax.xaxis.set_major_locator(mdates.MonthLocator())
            self.ax.xaxis.set_major_formatter(plt.FuncFormatter(
                lambda x, _: persian_text(jdt.datetime.fromgregorian(date=mdates.num2date(x)).strftime("%b"))
            ))
            self.ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
            self.ax.xaxis.set_minor_formatter(plt.FuncFormatter(
                lambda x, _: persian_text(jdt.datetime.fromgregorian(date=mdates.num2date(x)).strftime("%d"))
            ))
        else:
            self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            self.ax.xaxis.set_major_formatter(plt.FuncFormatter(
                lambda x, _: persian_text(jdt.datetime.fromgregorian(date=mdates.num2date(x)).strftime("%Y-%m-%d"))
            ))
            plt.xticks(rotation=45, ha='right')

        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.set_title(persian_text('نمودار گانت پروژه'), pad=20, fontsize=14, fontweight='bold', loc='right')
        self.ax.set_xlabel(persian_text('زمان'), labelpad=10, loc='left')
        plt.tight_layout()
        self.figure.patch.set_facecolor('white')
        self.ax.set_facecolor('white')

        for label in self.ax.get_yticklabels():
            label.set_ha('right')
            label.set_position((1, 0))

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('button_release_event', self.on_release)

        if hasattr(self, 'chart_placeholder'):
            self.chart_placeholder.pack_forget()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return

        if self.current_vline:
            self.current_vline.remove()
            if self.vline_text:
                self.vline_text.remove()

        self.current_vline = self.ax.axvline(x=event.xdata, color='red', linestyle='--', linewidth=1)
        greg_date = mdates.num2date(event.xdata)
        shamsi_date = jdt.datetime.fromgregorian(date=greg_date)
        date_str = shamsi_date.strftime("%Y-%m-%d")

        self.vline_text = self.ax.text(
            event.xdata, 0.98,
            persian_text(f"تاریخ: {date_str}"),
            transform=self.ax.get_xaxis_transform(),
            ha='center', va='top',
            bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8)
        )

        self.dragging_vline = True
        self.canvas.draw()

    def on_motion(self, event):
        if not self.dragging_vline or event.inaxes != self.ax:
            return

        if self.current_vline:
            self.current_vline.set_xdata([event.xdata, event.xdata])
            greg_date = mdates.num2date(event.xdata)
            shamsi_date = jdt.datetime.fromgregorian(date=greg_date)
            date_str = shamsi_date.strftime("%Y-%m-%d")

            if self.vline_text:
                self.vline_text.set_text(persian_text(f"تاریخ: {date_str}"))
                self.vline_text.set_x(event.xdata)

            self.canvas.draw()

    def on_release(self, event):
        self.dragging_vline = False

    def export_chart(self):
        if not self.figure:
            self.show_error("نموداری برای ذخیره وجود ندارد. لطفا ابتدا نمودار تولید کنید.")
            return

        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="ذخیره نمودار به عنوان PNG"
        )

        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight', facecolor='white')
                self.show_info(f"نمودار با موفقیت ذخیره شد:\n{file_path}")
            except Exception as e:
                self.show_error(f"خطا در ذخیره نمودار: {str(e)}")

    def clear_all(self):
        self.tasks = []
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            plt.close(self.figure)
            self.canvas = None
            self.figure = None
            self.current_vline = None
            self.vline_text = None
            self.dragging_vline = False
        if hasattr(self, 'chart_placeholder'):
            self.chart_placeholder.pack(expand=True)

    def show_error(self, message):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(persian_text("خطا"))
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=message, wraplength=380, font=("B-NAZANIN", 14)).pack(pady=20, padx=10)
        ctk.CTkButton(dialog, text=persian_text("تایید"), command=dialog.destroy, font=("B-NAZANIN", 14)).pack(pady=5)

    def show_info(self, message):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(persian_text("اطلاعات"))
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=message, wraplength=380, font=("B-NAZANIN", 14)).pack(pady=20, padx=10)
        ctk.CTkButton(dialog, text=persian_text("تایید"), command=dialog.destroy, font=("B-NAZANIN", 14)).pack(pady=5)


if __name__ == "__main__":
    root = ctk.CTk()
    app = GanttChartApp(root)
    root.mainloop()