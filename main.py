# !/usr/local/lib/ python3.11

from pigpio import *
import tkinter as tk
import os
import tkinter.messagebox as messagebox
from delayline import *
import time

# os.system("sudo pigpiod")
# time.sleep(0.01)

if os.environ.get('DISPLAY','') == '':
    os.environ.__setitem__('DISPLAY', ':0.0')  # sets display environment variable to 0.0

# START
# definition of fonts
normal = "Lato 18"
titles = "Lato 20"
outputfont = "Lato 36 bold"
outputminifont = "Lato 16 bold"
normalminifont = "Lato 16"
menufont = "Lato 16 bold"
settingsfont = "Lato 14"
ampfont = "Lato 12"
# END

ptomm = 0.19375  # pixel size in [mm]

# START
# definition of colors
teal = '#538083'
red = '#E3170A' 
light_gray = '#CDD6D0'
dark_gray = '#89909f'
black = '#13070c'
orange = '#E16036'
space_blue = '#0d0f16'
dark_blue = '#767b91'
light_blue = '#c7ccdb'
white_ish = '#e1e5ee'
# END

# START
# pi() object initialization
rpi = pi()
# END

class delayProgramator_app(tk.Tk):

    def close_app(self):
        """Closes the app."""
        if self.hspi:
            rpi.spi_close(self.hspi)
        self.quit()


    def update_widgets(self):
        self.pw_button_left['text'] = self.pw_str_left.get()
        self.pw_button_right['text'] = self.pw_str_right.get()
###### 
######
######
###### SETTINGS POP-UP WINDOW
        
    def settings_page(self):
        """Opens a new Toplevel window on top of root window. 
        
        Contains settings for delay line programator.
        """

        setts_page = tk.Toplevel(  # new Toplevel window
            bg=light_gray,
            name='settings',
            relief='flat')

        setts_page.title('Settings')
        setts_page.geometry('500x300+150+50')

        options = ["Select", "SY89297", "Option 2", "Option 3"]
        selected_var = tk.StringVar(setts_page)
        selected_var.set(options[0])

        def select_chip(chip):
            if chip == "SY89297":
                try:
                    del self.chip
                except:
                    pass
                self.chip = SY89297U()

            elif chip == "Select":
                try:
                    del self.chip
                except:
                    pass
                pass

            else:
                messagebox.showinfo(title="Chip not initialized.", 
                                    message="Selected chip has not been initialized.")
            return

        select_delayline_msg = tk.Message(setts_page,  # toggle auto detection message
            text="Select chip: ", 
            width=120,
            bg=light_gray,
            fg=black,
            justify='center')
        select_delayline_msg.place(relx=0.2, 
                                   rely=0.16, 
                                   anchor='center')

        select_delayline_menu = tk.OptionMenu(setts_page,
                                              selected_var,
                                              *options,
                                              command=select_chip)        
        select_delayline_menu.config(bg=light_gray,
                                     fg=space_blue,
                                     borderwidth=0,
                                     border=0,
                                     relief="flat")
        select_delayline_menu.place(relx=0.5,
                                    rely=0.12)
        
        """
        MANJKA KODA!!!
        """

        """MISCELLANEOUS BUTTONS"""

        back_btn = tk.Button(setts_page, 
            bg=red,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='back',
            width=3,
            height=1,
            command=lambda:setts_page.destroy())
        back_btn.place(relx=0.9, rely=0.9, anchor='center')


###### 
######
######
###### DELAY SETTINGS POP-UP WINDOW

    def set_delayval(self, num):
        "Displays a new Toplevel window in which user sets the pulse width."

        self.pulse_width = 0
        self.unit = ""

        set_pulse = tk.Toplevel(
            bg=white_ish,
            relief='flat')

        set_pulse.title('.')
        set_pulse.geometry(f'247x210+277+140')

        pw = tk.Label(set_pulse,
            font=outputminifont,
            fg=space_blue,
            bg=light_gray, 
            justify='center',
            height=2,
            width=20,
            text='')

        btn_0 = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='0',
            width=2,
            height=2,
            command=lambda: add_to_value(0))

        btn_1 = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='1',
            width=2,
            height=2,
            command=lambda: add_to_value(1))

        btn_2 = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='2',
            width=2,
            height=2,
            command=lambda: add_to_value(2))

        btn_3 = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='3',
            width=2,
            height=2,
            command=lambda: add_to_value(3))

        btn_4 = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='4',
            width=2,
            height=2,
            command=lambda: add_to_value(4))

        btn_5 = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='5',
            width=2,
            height=2,
            command=lambda: add_to_value(5))

        btn_6 = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='6',
            width=2,
            height=2,
            command=lambda: add_to_value(6))

        btn_7 = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='7',
            width=2,
            height=2,
            command=lambda: add_to_value(7))

        btn_8 = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='8',
            width=2,
            height=2,
            command=lambda: add_to_value(8))

        btn_9 = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='9',
            width=2,
            height=2,
            command=lambda: add_to_value(9))
        
        btn_ps = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='ps',
            width=2,
            height=2,
            command=lambda: set_unit("ps"))
        
        btn_ns = tk.Button(set_pulse, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='ns',
            width=2,
            height=2,
            command=lambda: set_unit("ns"))

        btn_OK = tk.Button(set_pulse, 
            bg=space_blue,
            fg=red,
            font=settingsfont,
            justify='center',
            text='ok',
            width=10,
            height=2,
            command=lambda: confirm_value(num))

        pw.place(relx=0.5, rely=0.1, anchor='center')
        btn_0.place(relx=0, rely=0.22)
        btn_1.place(relx=0.2, rely=0.22)
        btn_2.place(relx=0.4, rely=0.22)
        btn_3.place(relx=0.6, rely=0.22)
        btn_4.place(relx=0.8, rely=0.22)
        btn_5.place(relx=0, rely=0.48)
        btn_6.place(relx=0.2, rely=0.48)
        btn_7.place(relx=0.4, rely=0.48)
        btn_8.place(relx=0.6, rely=0.48)
        btn_9.place(relx=0.8, rely=0.48)
        btn_ps.place(relx=0, rely=0.74)
        btn_ns.place(relx=0.2, rely=0.74)
        btn_OK.place(relx=0.4, rely=0.74)

        def set_unit(unit):
            pw['text'] = f'{self.pulse_width} {unit}'
            self.unit = unit

        def confirm_value(num):
            if num == 0:
                self.pw_str_left.set(f'{self.pulse_width} {self.unit}') 
                self.delay_left = self.pulse_width
                self.unit_left = self.unit
            elif num == 1:
                self.pw_str_right.set(f'{self.pulse_width} {self.unit}')
                self.delay_right = self.pulse_width
                self.unit_right = self.unit

            """
            MANJKA KODA!!
            """
            self.update_widgets()
            self.pulse_width = 0
            self.unit = ""
            set_pulse.destroy()

        def add_to_value(val):
            if self.unit != "":
                self.pulse_width = 0
                
            self.pulse_width = (10 * self.pulse_width) + val
            pw['text'] = self.pulse_width


######
######
######
###### SET DELAY FUNCTION
            
    def set_delay(self, num):

        try:
            if self.chip.get_name() == "SY89297":
                latch_A = 0x0
                latch_B = 0x0
                print("latching")
                latch_A = self.chip.calc_delay(self.delay_left, self.unit_left == "ns")
                print(latch_A)
                latch_A = self.chip.define_latch_A(latch_A)
                print(latch_A)

                print(self.delay_right)
                latch_B = self.chip.calc_delay(self.delay_right, self.unit_right == "ns")
                print(latch_B)
                latch_B = self.chip.define_latch_B(latch_B)
                print(latch_B)


                data = (latch_B | latch_A) & self.tbits
                print(data)
                first_byte = (latch_B >> 6) & 0b1111
                second_byte = ((latch_B & (2**6-1))<<2) | ((latch_A >> 8) & (2**2-1))
                third_byte = latch_A & 0b11111111
                # data_binary = data.zfill(20)
                rpi.write(self.CS, 0)
                print(hex(first_byte), "  ", hex(second_byte), "  ", hex(third_byte), "  \n")
                rpi.spi_write(self.hspi, data=[first_byte, second_byte, third_byte])
                
                rpi.write(self.SLOAD, 1)
                rpi.write(self.SLOAD, 0)
                rpi.write(self.CS, 1)
                print("written")
                data = 0
            else:
                print(self.chip)
        except AttributeError:
            messagebox.showerror(title="Invalid chip",
                                 message="The selected delay line chip is not valid.")
        except Exception as e:
            print(e)

        return            


######
######
######
###### RESET DELAY FUNCTION
            
    def reset_delay(self, num):
        self.pulse_width = 0
        self.unit = ""
        self.pw_button_left['text'] = "Delay"
        self.pw_button_right['text'] = "Delay"

        return   

###### 
######
######
###### CREATE WIDGETS FUNCTION

    def create_widgets(self):
        """      
        Adds labels and text widgets to frames.

        Initializes SPI.
        """

        global hspi
        self.hspi = rpi.spi_open(0, 1000000)  # initialize SPI with 10 MHz freq in mode 0
        self.CS = 9
        self.SLOAD = 25
        rpi.set_mode(self.SLOAD, OUTPUT)
        rpi.set_mode(self.CS, OUTPUT)
        rpi.write(self.SLOAD, 0)
        rpi.write(self.CS, 1) 
        
        self.pw_str_left = tk.StringVar(self, value="Delay")
        self.pw_str_right = tk.StringVar(self, value="Delay")
        self.tbits = 0x3ffff
        self.delay_left = 0
        self.delay_right = 0
        self.unit_left = ""
        self.unit_right = ""

        (self.width, self.height) = (self.winfo_width(), self.winfo_height())  # get self.width and self.height of screen in pixels

        """
        DROP-DOWN MENU
        """
        self.menu = tk.Menu(self, 
            bg=light_gray, 
            fg=space_blue, 
            activebackground=teal,
            font=menufont)

        self.config(menu=self.menu)
        settsMenu = tk.Menu(self.menu)
        exitMenu = tk.Menu(self.menu)
        settsMenu.add_command(label='Settings', command=self.settings_page, font=menufont)
        self.menu.add_cascade(label='Settings', menu=settsMenu)
        exitMenu.add_command(label='Exit', command=self.close_app, background=red, font=menufont, activebackground=red)
        self.menu.add_cascade(label='Exit', menu=exitMenu)

        """
        LEVA STRAN
        """        
        self.pulse_frame_left = tk.Frame(self, 
                                         width=f'{self.width*ptomm}m',
                                         height=f'{self.height*ptomm}m',
                                         relief='flat',
                                         bg=light_gray)
        self.pulse_frame_left.place(relx=0.05,
                                    rely=0.05,
                                    relwidth=0.43,
                                    relheight=0.90)
        
        self.pw_label_left = tk.Label(self.pulse_frame_left,
                                          text='DELAY LINE 1',
                                          font=titles,
                                          fg=space_blue,
                                          bg=light_gray,
                                          justify='center',
                                          height=20,
                                          width=20)
        self.pw_label_left.place(relx=0.5, 
                                 rely=0.05, 
                                 anchor='center')
        
        self.pw_button_left = tk.Button(self.pulse_frame_left,
                                        #    width=26,
                                        height=1,
                                        fg=space_blue,
                                        bg=white_ish,
                                        font=normal,
                                        text=self.pw_str_left.get(),
                                        relief='flat',
                                        command=lambda: self.set_delayval(0))
        self.pw_button_left.place(relx=0.5,
                                  rely=0.35,
                                  relwidth=0.9,
                                  anchor='center')

        self.set_pw_button_left = tk.Button(self.pulse_frame_left,
                                            height=1,
                                            fg=space_blue,
                                            bg=light_gray,
                                            font=normal,
                                            text="SET",
                                            relief='flat',
                                            command=lambda: self.set_delay(0))
        self.set_pw_button_left.place(relx=0.25,
                                      rely=0.6,
                                      relwidth=0.4,
                                      anchor='center')
        
        self.reset_pw_button_left = tk.Button(self.pulse_frame_left,
                                              height=1,
                                              fg=space_blue,
                                              bg=light_gray,
                                              font=normal,
                                              text="RESET",
                                              relief='flat',
                                              command=lambda: self.reset_delay(0))
        self.reset_pw_button_left.place(relx=0.75,
                                      rely=0.6,
                                      relwidth=0.4,
                                      anchor='center')
        
        """
        DESNA STRAN UI
        """        
        self.pulse_frame_right = tk.Frame(self, 
                                         width=f'{self.width*ptomm}m',
                                         height=f'{self.height*ptomm}m',
                                         relief='flat',
                                         bg=light_gray)
        self.pulse_frame_right.place(relx=0.52,
                                    rely=0.05,
                                    relwidth=0.43,
                                    relheight=0.90)
        
        self.pw_label_right = tk.Label(self.pulse_frame_right,
                                          text='DELAY LINE 2',
                                          font=titles,
                                          fg=space_blue,
                                          bg=light_gray,
                                          justify='center',
                                          height=20,
                                          width=20)
        self.pw_label_right.place(relx=0.5, 
                                 rely=0.05, 
                                 anchor='center')
        
        self.pw_button_right = tk.Button(self.pulse_frame_right,
                                        #    width=26,
                                        height=1,
                                        fg=space_blue,
                                        bg=white_ish,
                                        font=normal,
                                        text=self.pw_str_right.get(),
                                        relief='flat',
                                        command=lambda: self.set_delayval(1))
        self.pw_button_right.place(relx=0.5,
                                  rely=0.35,
                                  relwidth=0.9,
                                  anchor='center')

        self.set_pw_button_right = tk.Button(self.pulse_frame_right,
                                            height=1,
                                            fg=space_blue,
                                            bg=light_gray,
                                            font=normal,
                                            text="SET",
                                            relief='flat',
                                            command=lambda: self.set_delay(1))
        self.set_pw_button_right.place(relx=0.25,
                                      rely=0.6,
                                      relwidth=0.4,
                                      anchor='center')
        
        self.reset_pw_button_right = tk.Button(self.pulse_frame_right,
                                              height=1,
                                              fg=space_blue,
                                              bg=light_gray,
                                              font=normal,
                                              text="RESET",
                                              relief='flat',
                                              command=lambda: self.reset_delay(1))
        self.reset_pw_button_right.place(relx=0.75,
                                      rely=0.6,
                                      relwidth=0.4,
                                      anchor='center')

        return

###### 
######
######
###### MAIN WINDOW INITIALIZATION

    def __init__(self):
        tk.Tk.__init__(self)  # self = root window

        #GUI
        self.title('Delay Line Programator')
        self.attributes("-fullscreen", True)  # app window starts in borderless fullscreen mode
        self.bind("<F11>", lambda event: self.attributes("-fullscreen", not self.attributes("-fullscreen")))
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))  # keyboard key bindings for exiting fullscreen mode
        self.update_idletasks() 
        self.configure(bg=space_blue)
        self.config(cursor="none")
        self.chip = SY89297U()

        # create widget
        self.create_widgets()

###### 
######
######
###### START OF THE APPLICATION
        
if __name__ == '__main__':
    app = delayProgramator_app()
    app.mainloop()
###### END
