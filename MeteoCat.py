import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from tkcalendar import DateEntry
import os
import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


sec = datetime.timedelta(seconds=1)

def convertTextDate(value):
    value = value.split(" ")
    time = value[4].split(":")
    match value[2]:
        case "January":
            month = 1
        case "February":
            month = 2
        case "March":
            month = 3
        case "April":
            month = 4
        case "May":
            month = 5
        case "June":
            month = 6
        case "July":
            month = 7
        case "August":
            month = 8
        case "September":
            month = 9
        case "October":
            month = 10
        case "November":
            month = 11
        case "December":
            month = 12
    return(datetime.datetime(
        int(value[3]), month, int(value[1]), \
        int(time[0]), int(time[1]), int(time[2])
        ))

class Wastage():
    def __init__(self, start_date: datetime.datetime, \
        end_date: datetime.datetime, value: float):
        self.start_date = start_date
        self.end_date = end_date
        self.length = int((end_date-start_date).total_seconds()) - 1
        self.value = value
    def append_wastage(self, dictionary: dict) -> dict:
        for i in range(self.length):
            dictionary[self.start_date + sec*(i+1)] = self.value
        return dictionary

class Application:
    def __init__(self, root):
        self.root = root
        self.file_dict = {}  # Словарь для хранения полных путей к файлам
        self.files = []
        self.losses = []  # Список для хранения потерь
        self.output = {}
        self.graph_window = None  # Окно с графиком
        self.selected_type = tk.IntVar(value=6)  # Устанавливаем значение по умолчанию
        self.start_date = ""
        self.start_time = ""
        self.countExport = 0
        self.newlist = []

        # Добваление цветов для темы по умолчанию
        self.MenuBg = "#465458"
        self.Font = "white"
        self.List = "#465458"
        self.Button = "#465458"
        self.Label = "#465458"
        self.Date = "#465458"

        # Создание меню
        self.create_menu()

        # Создание виджетов
        self.create_listbox()
        self.create_losses_listbox()
        self.create_radiobuttons()
        self.create_date_frame(
            "Выберите Начальную Дату", 
            row=0, 
            column=2, 
            rowspan=1, 
            callback=self.set_start_date
            )
        self.create_time()
        self.create_report_count_frame()
        self.create_plot_canvas()
        self.create_push_button()
        self.create_export_button()

    def create_menu(self):
        # Создание основного меню
        menu_bar = tk.Menu(self.root, bg=self.MenuBg, fg=self.Font)

        # Создание подменю "File"
        file_menu = tk.Menu(
            menu_bar, 
            tearoff=0, 
            bg=self.MenuBg, 
            fg=self.Font
            )
        help_menu = tk.Menu(
            menu_bar, 
            tearoff=0, 
            bg=self.MenuBg, 
            fg=self.Font
            )
       
        # Добавление подменю к основному меню
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Добавление команд в подменю "File"
        file_menu.add_command(
            label="Open", 
            command=self.open_file_dialog
            )
        file_menu.add_command(
            label="Clear", 
            command=self.clear
            )

        help_menu.add_command(label="Help")

        # Создание подменю "Theme"
        theme_menu = tk.Menu(menu_bar, tearoff=0, bg=self.MenuBg, fg=self.Font)
        menu_bar.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(
            label="Тёмная тема", 
            command=lambda: self.change_theme("dark")
            )  # Тема "arc"
        theme_menu.add_command(
            label="Светлая тема", 
            command=lambda: self.change_theme("light")
            )  # Тема "default"

        # Назначение основного меню окну приложения
        self.root.config(menu=menu_bar)

    def create_push_button(self):
        push_button = tk.Button(self.root, text="Пуск", command=self.push_process)
        push_button.grid(
            row=6, 
            column=0, 
            rowspan=1, 
            padx=5, 
            pady=5, 
            ipadx=150
            )

    def create_export_button(self):
        push_button = tk.Button(self.root, text="Экспорт", command=self.export_process)
        push_button.grid(
            row=6, 
            column=1, 
            rowspan=1, 
            padx=5, 
            pady=5, 
            ipadx=150
            )

    def export_process(self):
        stdt = self.start_date.split(sep=".")
        sttm = self.start_time.split(sep = ":")
        start_date = datetime.datetime(
            int(stdt[2]),
            int(stdt[1]),
            int(stdt[0]),
            int(sttm[0]),
            int(sttm[1]),
            int(sttm[2]))
        filenameExample = str(start_date).replace(':', "-") \
    + "_" + str(self.countExport) + ".txt"
        wayR = filedialog.asksaveasfilename(
            title="Save file",
            initialfile=filenameExample,
            defaultextension="txt")
        file = open(wayR, "a")
        for i in self.newlist:
            file.write(str(i) + "\n")
        file.close()

    def push_process(self):
        self.newlist = []
        stdt = self.start_date.split(sep=".")
        sttm = self.start_time.split(sep = ":")
        start_date = datetime.datetime(
            int(stdt[2]),
            int(stdt[1]),
            int(stdt[0]),
            int(sttm[0]),
            int(sttm[1]),
            int(sttm[2]))
        count = 0
        firstDate = sorted(self.output.keys())[0]
        if start_date < firstDate:
            how_many = int((firstDate-start_date).total_seconds())
            valu = self.output[firstDate]
            for i in range(how_many):
                self.newlist.append(valu)
                count += 1   
            start_date += sec * how_many
        for i in range(int(self.countExport)-count):
            try:
                start_date += sec
                val = self.output[start_date]
                self.newlist.append(val)
                count += 1
                prev_val = val 
            except KeyError:
                break
        if count < int(self.countExport):
            for i in range(int(self.countExport)-count):
                self.newlist.append(prev_val)
        figure = self.plot_canvas.figure
        figure.clear()
        ax = figure.add_subplot(111)
        ax.plot(range(len(self.newlist)), self.newlist)
        self.plot_canvas.draw()
        
    def clear(self):
        self.listbox.delete(0, tk.END)
        self.files.clear()
        self.losses_listbox.delete(0, tk.END)
        self.losses.clear()

    def open_file_dialog(self):
        # Открытие диалогового окна выбора файлов
        file_paths = filedialog.askopenfilenames(
            title = "Select a File",
            filetypes = (
                ("Log files", "*.log"),
                ("Text files", "*.txt*"),
                ("All files", "*.*")
                ))
        for file_path in file_paths:
            if file_path not in self.files:
                file_name = os.path.basename(file_path)  # Получение только имени файла
                self.listbox.insert(tk.END, file_name)
                self.file_dict[file_name] = file_path  # Сохранение полного пути в словаре
                self.files.append(file_path)

    def process_files(self):
        self.output = {}
        self.losses_listbox.delete(0, tk.END)
        self.losses.clear()
        figure = self.plot_canvas.figure
        figure.clear()
        self.plot_canvas.draw()
        current, total = 1, len(self.files)
        for f in self.files:
            self.losses_listbox.insert(tk.END, \
                "Обрабатывается файл: " + str(current)+"/"+str(total)
                )
            self.losses_listbox.update()
            current += 1
            with open(f, "r", encoding="utf-8") as file:
                for line in file:
                    if (not line[:5].isdigit()) \
                        or (line == "\n") or (line == "Logfile\n"):
                        continue
                    line = line.split(",")
                    date = convertTextDate(line[1])
                    data = float(line[self.selected_type.get()])
                    try:
                        if date - prev_date == sec:
                            self.output[date] = data
                            prev_date = date
                            prev_val = data
                        elif date - prev_date < sec:
                            pass
                        elif date - prev_date == sec*2:
                            self.output[date - sec] = prev_val
                            self.output[date] = data
                            prev_date = date
                            prev_val = data
                        else:
                            self.losses.append(
                                Wastage(prev_date, date, prev_val)
                                )
                            self.output = \
                                self.losses[-1].append_wastage(self.output)
                            self.output[date] = data
                            prev_date = date
                            prev_val = data
                    except:
                        prev_date = date
                        prev_val = data
                        self.output[date] = data
                file.close()
                self.losses_listbox.delete(0, tk.END)
        if self.losses == []:
            self.losses_listbox.insert(tk.END, "Потерь данных не обнарожено")
            self.losses_listbox.update()
        for i in self.losses:
            self.losses_listbox.insert(tk.END, 
            str(i.start_date)+" – "+ str(i.end_date)
            )



    def change_theme(self, theme):
        # Метод для изменения темы приложения
        if theme == "dark":
            self.root.config(bg="#333333")
            self.MenuBg = "#465458"
            self.Font = "white"
            self.List = "#465458"
            self.Button = "#465458"
            self.Label = "#465458"
            self.Date = "#465458"

        elif theme == "light":
            self.root.config(bg="#A8D0E6")
            self.MenuBg = "#F76C6C"
            self.Font = "white"
            self.List = "#F76C6C"
            self.Button = "#F76C6C"
            self.Label = "#F76C6C"
            self.Date = "#F76C6C"

        # Обновление свойств виджетов
        self.listbox.config(bg=self.List, fg=self.Font)
        self.losses_listbox.config(bg=self.List, fg=self.Font)
        self.root.update()

    def create_listbox(self):
        frame_list = tk.LabelFrame(
            self.root, 
            text="Список файлов", 
            bg=self.Label, 
            fg=self.Font
            )
        frame_list.grid(
            row=0, 
            column=0, 
            rowspan=3, 
            padx=10, 
            pady=10, 
            sticky="nsew"
            )

        self.listbox = tk.Listbox(
            frame_list, 
            height=15, 
            width=50, 
            bg=self.List, 
            fg=self.Font
            )
        self.listbox.grid(
            row=0, 
            column=0, 
            padx=5, 
            pady=5, 
            sticky="nsew"
            )

        scrollbar_y = tk.Scrollbar(frame_list, command=self.listbox.yview)
        scrollbar_y.grid(
            row=0, 
            column=1, 
            sticky="ns"
            )
        self.listbox.config(yscrollcommand=scrollbar_y.set)

        self.listbox.bind("<Double-Button-1>", lambda event: self.view_file())

        process_button = tk.Button(
            frame_list, 
            text="Обработать", 
            command=self.process_files
            )
        process_button.grid(
            row=1, 
            column=0, 
            padx=5, 
            pady=5, 
            ipadx=120, 
            ipady=5, 
            sticky="s"
            )

    def create_losses_listbox(self):
        # Создание списка потерь
        frame_losses = tk.LabelFrame(
            self.root, 
            text="Список потерь", 
            bg=self.Label, 
            fg=self.Font
            )
        frame_losses.grid(
            row=1, 
            column=1, 
            rowspan=2, 
            padx=10, 
            pady=10, 
            sticky="nsew"
            )

        self.losses_listbox = tk.Listbox(
            frame_losses, 
            height=8, 
            width=58, 
            bg=self.List, 
            fg=self.Font
            )
        self.losses_listbox.pack(
            side=tk.LEFT, 
            fill=tk.BOTH, 
            padx=5, 
            pady=5
            )

        scrollbar_y = tk.Scrollbar(frame_losses, \
            command=self.losses_listbox.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.losses_listbox.config(yscrollcommand=scrollbar_y.set)

    def create_radiobuttons(self):
        # Создание переключателей (radiobuttons) для выбора типа данных
        frame_radiobuttons = tk.LabelFrame(
            self.root, 
            text="Выберите тип данных", 
            bg=self.Label, 
            fg = self.Font
            )
        frame_radiobuttons.grid(
            row=0, 
            column=1, 
            padx=10, 
            pady=10, 
            sticky="w"
            )

        self.selected_type = tk.IntVar(value=6)  # Устанавливаем значение по умолчанию

        wind_speed_radiobutton = tk.Radiobutton(
            frame_radiobuttons, 
            text="Скорость Ветра", 
            variable=self.selected_type,
            value=4, 
            indicatoron=True, 
            width=50, 
            anchor="w"
            )
        wind_speed_radiobutton.pack(anchor="w")

        pressure_radiobutton = tk.Radiobutton(
            frame_radiobuttons, 
            text="Давление", 
            variable=self.selected_type, 
            value=6, 
            indicatoron=True, 
            width=50, 
            anchor="w"
            )
        pressure_radiobutton.pack(anchor="w")

        humidity_radiobutton = tk.Radiobutton(
            frame_radiobuttons, 
            text="Влажность", 
            variable=self.selected_type,
            value=7, 
            indicatoron=True, 
            width=50, 
            anchor="w"
            )
        humidity_radiobutton.pack(anchor="w")

        temperature_radiobutton = tk.Radiobutton(
            frame_radiobuttons, 
            text="Температура", 
            variable=self.selected_type,
            value=8, 
            indicatoron=True, 
            width=50, 
            anchor="w"
            )
        temperature_radiobutton.pack(anchor="w")


    def create_date_frame(self, title, row, column,rowspan, callback):
        # Создание фрейма для выбора даты
        frame_date = tk.LabelFrame(
            self.root, 
            text=title, 
            bg=self.Date, 
            fg=self.Font
            )
        frame_date.grid(
            row=row, 
            column=column, 
            rowspan=rowspan, 
            padx=10, 
            sticky="w"
            )

        date_entry = DateEntry(
            frame_date, 
            width=30, 
            bg=self.Date, 
            fg=self.Font
            )  # Используем DateEntry для выбора даты
        date_entry.grid(
            row=2, 
            column=0, 
            padx=5, 
            pady=5
            )

        send_button = tk.Button(
            frame_date, 
            text="Отправить", 
            command=lambda: callback(date_entry.get()), 
            bg=self.Date, 
            fg=self.Font
            )
        send_button.grid(
            row=2, 
            column=1, 
            padx=5, 
            pady=5
            )

    def create_time(self):
        # Задаём время
        frame_report_count = tk.LabelFrame(
            self.root, 
            text="Введите время", 
            bg=self.Label, 
            fg=self.Font
            )
        frame_report_count.grid(
            row=1, 
            column=2, 
            rowspan=1, 
            padx=10, 
            pady=5, 
            sticky="w"
            )
        self.report_time = tk.Entry(
            frame_report_count,
            width=30, 
            bg=self.Button, 
            fg=self.Font
            )
        self.report_time.grid(
            row=0, 
            column=0, 
            padx=5, 
            pady=5
            )
        send_button = tk.Button(
            frame_report_count, 
            text="Отправить", 
            command=self.set_report_time, 
            bg=self.Button, 
            fg=self.Font)
        send_button.grid(
            row=0, 
            column=1, 
            padx=5, 
            pady=5
            )

    def create_report_count_frame(self):
        # Создание фрейма для ввода количества отчетов
        frame_report_count = tk.LabelFrame(
            self.root, 
            text="Введите количество отчетов", 
            bg=self.Label, 
            fg=self.Font)
        frame_report_count.grid(
            row=2, 
            column=2, 
            rowspan=1, 
            padx=10, 
            pady=5, 
            sticky="w"
            )
        self.report_count_entry = tk.Entry(
            frame_report_count, 
            width=30, 
            bg=self.Button, 
            fg=self.Font
            )
        self.report_count_entry.grid(
            row=0, 
            column=0, 
            padx=5, 
            pady=5
            )
        send_button = tk.Button(
            frame_report_count, 
            text="Отправить", 
            command=self.set_report_count, 
            bg=self.Button, 
            fg=self.Font
            )
        send_button.grid(
            row=0, 
            column=1, 
            padx=5, 
            pady=5
            )


    def create_plot_canvas(self):
        # Создание холста для построения графика
        frame_plot = tk.Frame(self.root)
        frame_plot.grid(
            row=4, 
            column=0, 
            columnspan=3, 
            padx=10, 
            pady=5, 
            sticky="nsew"
            )

        fig = Figure(figsize=(4, 2), dpi=100)
        self.plot_canvas = FigureCanvasTkAgg(fig, master=frame_plot)
        self.plot_canvas.get_tk_widget().pack(
            side=tk.TOP, 
            fill=tk.BOTH, 
            expand=True
            )

        toolbar = NavigationToolbar2Tk(self.plot_canvas, frame_plot)
        toolbar.update()
        self.plot_canvas.get_tk_widget().pack(
            side=tk.TOP, 
            fill=tk.BOTH, 
            expand=True
            )

    def view_file(self):
        # Просмотр выбранного файла
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_file = self.listbox.get(selected_index)
            file_path = self.file_dict.get(selected_file)
            if file_path:
                with open(file_path, "r") as file:
                    file_contents = file.read()
                    text_editor = tk.Toplevel(self.root)
                    text_editor.title(selected_file)
                    text_widget = ScrolledText(text_editor)
                    text_widget.insert(tk.END, file_contents)
                    text_widget.pack(expand=True, fill="both")

    def set_start_date(self, date):
        # Установка выбранной начальной даты
        self.start_date = date
        print(self.start_date)

    def set_report_time(self):
        self.start_time = self.report_time.get()
        print(self.report_time.get())


    def set_report_count(self):
        # Установка введенного количества отчетов
        self.countExport = self.report_count_entry.get()


# Создание экземпляра приложения
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Обработка данных метеостанции")
    root.geometry("1112x680")  # Задайте желаемый размер окна (например, 800x600)

    root.resizable(width=False, height=False)  # Запрет изменения размеров окна

    app = Application(root)

    root.configure(bg="#333333")  # Задаем фон для корневого виджета

    root.mainloop()