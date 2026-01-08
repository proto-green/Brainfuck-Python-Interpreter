import threading
import time
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

symbols = ["+", "-", ">", "<", ",", ".", "[", "]"]
script_thread = None
script_running = False
script_stop_call = False
console = ""

root = Tk()
root.title("Brainfuck Interpreter")
root.minsize(300, 250)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

frame = ttk.Frame(root, padding="20 7 20 20")
frame.grid(column=0, row=0, sticky=N+S+E+W)
frame.columnconfigure(1, weight=1)
frame.rowconfigure(2, weight=1)


def browse_files():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a Brainfuck Script",
                                          filetypes = [("Brainfuck Scripts", "*.brainfuck* *.bf*")])
    return filename


def open_script(*args):
    filename = browse_files()
    if not filename:
        return
    file = open(filename)
    contents = file.read()
    file.close()
    scriptEntry.delete("1.0", END) # Row.column based indices where row is 1-based
    scriptEntry.insert("1.0", contents)
    scriptEntry.focus_set()


def save_script(*args):
    filename = filedialog.asksaveasfilename(initialdir = "/",
                                            title="Save Script",
                                            filetypes=[("Brainfuck Scripts", "*.brainfuck* *.bf*")])
    if not str.endswith(filename, ".bf") and not str.endswith(filename, ".brainfuck"):
        filename += ".bf"
    if not filename:
        return
    file = open(filename, "w")
    file.write(scriptEntry.get("1.0", END))
    file.close()


def update_console(kind, output=None):
    global console
    if kind == "Clear":
        console = ""
    elif kind == "Print":
        console = console + output
    elif kind == "Override":
        console = output
    consoleEntry.delete("1.0", END)
    consoleEntry.insert("1.0", console)
    consoleEntry.see(END)


def run_script(*args):
    global script_thread, script_running, script_stop_call
    if script_running:
        update_console("Print", "Stopping Script\n")
        runText.set("Stopping..")
        script_stop_call = True
    else:
        update_console("Clear")
        script_running = True
        code = scriptEntry.get("1.0", END)
        # Filter through the script to get the raw code
        temp = ""
        for letter in code:
            if letter in symbols:
                temp += letter
        code = temp
        runText.set("Stop Script")
        script_thread = threading.Thread(target=parse_script, args=[code])
        script_thread.start()


def parse_script(code):
    global script_thread, script_running, script_stop_call
    index = 0
    # Code handling section
    mem = [0]
    pointer = 0
    saved_console = ""
    while index < len(code) and not script_stop_call:
        symbol = code[index]
        if symbol == "+":
            if pointer > len(mem) - 1:
                while pointer > len(mem) - 1:
                    mem.append(0)
            mem[pointer] += 1
        elif symbol == "-":
            if pointer > len(mem) - 1:
                while pointer > len(mem) - 1:
                    mem.append(0)
            mem[pointer] = max(0, mem[pointer] - 1)
        elif symbol == ">":
            pointer += 1
            if pointer > len(mem) - 1:
                while pointer > len(mem) - 1:
                    mem.append(0)
        elif symbol == "<":
            pointer = max(0, pointer - 1)
        elif symbol == "[":
            if mem[pointer] == 0:
                found_bracket = False
                bracket_sum = 1
                while not found_bracket and index < len(code) - 1:
                    index += 1
                    if code[index] == "[":
                        bracket_sum += 1
                    elif code[index] == "]":
                        bracket_sum -= 1
                        if bracket_sum == 0:
                            found_bracket = True
                            index -= 1
        elif symbol == "]":
            if mem[pointer] != 0:
                found_bracket = False
                bracket_sum = -1
                while not found_bracket and index > 0:
                    index -= 1
                    if code[index] == "[":
                        bracket_sum += 1
                        if bracket_sum == 0:
                            found_bracket = True
                            index -= 1
                    elif code[index] == "]":
                        bracket_sum -= 1
        elif symbol == ".":
            update_console("Print", chr(mem[pointer]) + "\n")
        elif symbol == ",":
            index -= 1 # Stall the advancement of the index
            time.sleep(0.03)
            current_console = consoleEntry.get("1.0", END)
            if saved_console == "":
                saved_console = current_console
            elif saved_console != current_console:
                mem[pointer] = ord(current_console[len(current_console) - 2])
                saved_console = ""
                index += 1
        index += 1
    # ----------------------
    print(mem, pointer)
    runText.set("Run Script")
    update_console("Print", "Script Stopped\n")
    scriptEntry.focus()
    script_thread = None
    script_running = False
    script_stop_call = False


browse = ttk.Button(frame, text="Browse..", command=open_script)
browse.grid(row=0, column=0, sticky=W)

runText = StringVar()
runText.set("Run Script")
run = ttk.Button(frame, textvariable=runText, command=run_script)
run.grid(row=0, column=3, columnspan=2, sticky=W)

save = ttk.Button(frame, text="Save", command=save_script)
save.grid(row=0, column=1, sticky=W)

root.bind("<Control-s>", save_script)
root.bind("<Control-r>", run_script)
root.bind("<Control-o>", open_script)

scriptLabel = ttk.Label(frame, text="Script")
scriptLabel.grid(row=1, column=1, columnspan=2)

scriptEntry = Text(frame, wrap="none", height=12)
scriptEntry.grid(row=2, column=0, columnspan=4, sticky=N+W+E+S)

# Having to type literals instead of using tkinter variables because pycharm doesn't like me
scriptScrolly = ttk.Scrollbar(frame, orient="vertical", command=scriptEntry.yview)
scriptScrolly.grid(row=2, column=4, sticky=N+S+E)
scriptEntry.configure(yscrollcommand=scriptScrolly.set)

scriptScrollx = ttk.Scrollbar(frame, orient="horizontal", command=scriptEntry.xview)
scriptScrollx.grid(row=3, column=0, columnspan=4, sticky=E+W+N)
scriptEntry.configure(xscrollcommand=scriptScrollx.set)

consoleLabel = ttk.Label(frame, text="Console")
consoleLabel.grid(row=4, column=1, columnspan=2)

consoleEntry = Text(frame, height=5)
consoleEntry.grid(row=5, column=0, columnspan=4, sticky=N+W+E+S)

consoleScroll = ttk.Scrollbar(frame, orient="vertical", command=consoleEntry.yview)
consoleScroll.grid(row=5, column=4, sticky=N+S+E)
consoleEntry.configure(yscrollcommand=consoleScroll.set)

scriptEntry.focus()

root.mainloop()
