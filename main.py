# !/usr/local/lib/ python3.11

from pigpio import *
import tkinter as tk
import os
import sys
import tkinter.messagebox as messagebox
from delayline import *
import time
import updateService

# os.system("sudo pigpiod")
# time.sleep(0.01)

if os.environ.get('DISPLAY','') == '':
    os.environ.__setitem__('DISPLAY', ':0.0')  # sets display environment variable to 0.0

# START
# definition of fonts
normal = "Lato 18"
titles = "Lato 22"
outputfont = "Lato 24 bold"
outputminifont = "Lato 16 bold"
normalminifont = "Lato 16"
menufont = "Lato 16 bold"
settingsfont = "Lato 16"
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

def restart_program():
    """
    Restarts the current program.
    Note: this function does not return. Any cleanup action (like saving data) must be done before calling this function.
    """
    python = sys.executable
    os.execl(python, python, *sys.argv)

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

        options = ["Select", "808 nm", "660 nm"]
        selected_var = tk.StringVar(setts_page)
        selected_var.set(options[self.select_index])

        def select_chip(chip):
            if chip == "808 nm":
                try:
                    del self.chip
                except:
                    pass
                self.chip = SY89297U()
                self.select_index = 1

            elif chip == "660 nm":
                try:
                    del self.chip
                except:
                    pass
                
                self.chip = MCP23S17(0)
                rpi.write(self.CS, 0)
                rpi.spi_write(self.hspi, self.chip.setIO())
                rpi.write(self.CS, 1)
                time.sleep(0.1)
                self.enable = 1
                self.select0 = 1
                self.select1 = 1

                """ Opening the line. Setting the delay to 0. """
               
                self.reset_delay(0)
                print("Reset left.")
                self.reset_delay(1)
                print("Reset right.")

                self.select_index = 2
                

            elif chip == "Select":
                try:
                    del self.chip
                    self.chip = NOCHIP()
                except:
                    pass
                self.select_index = 0

            else:
                messagebox.showinfo(title="Chip not initialized.", 
                                    message="Selected chip has not been initialized.")

            if chip == "660 nm":                
                self.b_en_color = red
                self.f_en_color = white_ish
                self.b_s0_color = red
                self.f_s0_color = white_ish
                self.b_s1_color = red
                self.f_s1_color = white_ish
                self.button_enable.config(fg=self.f_en_color, bg=self.b_en_color, activebackground=self.b_en_color, activeforeground=self.f_en_color)
                self.button_select0.config(fg=self.f_s0_color, bg=self.b_s0_color, activebackground=self.b_s0_color, activeforeground=self.f_s0_color)
                self.button_select1.config(fg=self.f_s1_color, bg=self.b_s1_color, activebackground=self.b_s1_color, activeforeground=self.f_s1_color)

            else:
                self.b_en_color = dark_gray
                self.f_en_color = white_ish
                self.b_s0_color = dark_gray
                self.f_s0_color = white_ish
                self.b_s1_color = dark_gray
                self.f_s1_color = white_ish
                self.button_enable.config(fg=self.f_en_color, bg=self.b_en_color, activebackground=self.b_en_color, activeforeground=self.f_en_color)
                self.button_select0.config(fg=self.f_s0_color, bg=self.b_s0_color, activebackground=self.b_s0_color, activeforeground=self.f_s0_color)
                self.button_select1.config(fg=self.f_s1_color, bg=self.b_s1_color, activebackground=self.b_s1_color, activeforeground=self.f_s1_color)


            return

        select_delayline_msg = tk.Message(setts_page,  # toggle auto detection message
            text="Select device: ", 
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

        try:
            _ = self.chip.get_name()
        except:
            messagebox.showwarning(title="Chip not selected.",
                                   message="Please select a delay line chip before you set the value of a delay.")
            return

        set_pulse = tk.Toplevel(
            bg=white_ish,
            relief='flat')

        set_pulse.title('Set delay')
        set_pulse.geometry(f'247x210+200+140')

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
            width=11,
            height=2,
            command=lambda: confirm_value(num))

        pw.place(relwidth=1, relheight=0.25,relx=0.5, rely=0.1, anchor='center')
        btn_0.place(relwidth=0.2, relheight=0.25, relx=0, rely=0.22)
        btn_1.place(relwidth=0.2, relheight=0.25, relx=0.2, rely=0.22)
        btn_2.place(relwidth=0.2, relheight=0.25, relx=0.4, rely=0.22)
        btn_3.place(relwidth=0.2, relheight=0.25, relx=0.6, rely=0.22)
        btn_4.place(relwidth=0.2, relheight=0.25, relx=0.8, rely=0.22)
        btn_5.place(relwidth=0.2, relheight=0.25, relx=0, rely=0.48)
        btn_6.place(relwidth=0.2, relheight=0.25, relx=0.2, rely=0.48)
        btn_7.place(relwidth=0.2, relheight=0.25, relx=0.4, rely=0.48)
        btn_8.place(relwidth=0.2, relheight=0.25, relx=0.6, rely=0.48)
        btn_9.place(relwidth=0.2, relheight=0.25, relx=0.8, rely=0.48)
        btn_ps.place(relwidth=0.2, relheight=0.25, relx=0, rely=0.74)
        btn_ns.place(relwidth=0.2, relheight=0.25, relx=0.2, rely=0.74)
        btn_OK.place(relwidth=0.6, relheight=0.25, relx=0.4, rely=0.74)

        def set_unit(unit):
            pw['text'] = f'{self.pulse_width} {unit}'
            self.unit = unit

        def confirm_value(num):
            # print(self.chip.get_name())
            if self.chip.get_name() == "SY89297U":
                if (self.unit == "ps" and self.pulse_width > 5000):
                    messagebox.showwarning(title="Delay out of bounds.", 
                                           message="The delay you try to set is too long. Maximum delay is 5 ns.")
                    self.pulse_width = 0
                    self.unit = ""
                    return
                if (self.unit == "ns" and self.pulse_width > 5):
                    messagebox.showwarning(title="Delay out of bounds.", 
                                           message="The delay you try to set is too long. Maximum delay is 5 ns.")
                    self.pulse_width = 0
                    self.unit = ""
                    return
                else:
                    pass
            
            elif self.chip.get_name() == "MCP23S17":
                if (self.unit == "ps" and self.pulse_width > 10230):
                    messagebox.showwarning(title="Delay out of bounds.", 
                                           message="The delay you try to set is too long. Maximum delay is 10,230 ns.")
                    self.pulse_width = 0
                    self.unit = ""
                    return
                if (self.unit == "ns" and self.pulse_width > 10):
                    messagebox.showwarning(title="Delay out of bounds.", 
                                           message="The delay you try to set is too long. Maximum delay is 10,230 ns.")
                    self.pulse_width = 0
                    self.unit = ""
                    return
                else:
                    pass
                    
            
            if num == 0:
                self.unit_left = self.unit
                self.pw_str_left.set(f'{self.pulse_width} {self.unit_left}') 
                self.delay_left = self.pulse_width
                self.set_left = 1
            elif num == 1:                
                self.unit_right = self.unit
                self.pw_str_right.set(f'{self.pulse_width} {self.unit_right}')
                self.delay_right = self.pulse_width
                self.set_right = 1

            self.update_widgets()
            self.pulse_width = 0
            self.unit = ""
            set_pulse.destroy()
            self.set_delay(num)

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
            if self.chip.get_name() == "SY89297U":
                latch_A = 0x00
                latch_B = 0x00

                latch_A = self.chip.calc_delay(self.delay_left, self.unit_left == "ns")
                latch_A = self.chip.define_latch_A(latch_A)

                latch_B = self.chip.calc_delay(self.delay_right, self.unit_right == "ns")
                latch_B = self.chip.define_latch_B(latch_B)

                first_byte = (latch_B >> 6) & 0b1111
                second_byte = ((latch_B & (2**6-1))<<2) | ((latch_A >> 8) & (2**2-1))
                third_byte = latch_A & 0b11111111
                rpi.write(self.CS, 0)
                rpi.spi_write(self.hspi, data=[first_byte, second_byte, third_byte])
                
                rpi.write(self.SLOAD, 1)
                rpi.write(self.SLOAD, 0)
                rpi.write(self.CS, 1)

            elif self.chip.get_name() == "MCP23S17":
                latch_A = 0x00
                latch_B = 0x00

                rpi.write(self.CS, 0)

                if num == 0:
                    print(f"en: {self.enable}, sel0: {self.select0}, sel1: {self.select1}")
                    writeval = self.chip.calc_delay(self.delay_left, self.unit_left == "ns", 0, self.enable, self.select0, self.select1)
                    print(f"SPI left: {[bin(x) for x in writeval]}.")
                    rpi.spi_write(self.hspi, writeval[0:4])
                    rpi.write(self.CS, 1)
                    time.sleep(0.001)
                    rpi.write(self.CS, 0)
                    rpi.spi_write(self.hspi, writeval[4:8])
                    rpi.write(self.CS, 1)
                    time.sleep(0.001)
                    rpi.write(self.CS, 0)
                    rpi.spi_write(self.hspi, writeval[8:])
                    self.set_left = 0

                if num == 1:
                    print(f"en: {self.enable}, sel0: {self.select0}, sel1: {self.select1}")
                    writeval = self.chip.calc_delay(self.delay_right, self.unit_right == "ns", 1, self.enable, self.select0, self.select1)
                    print(f"SPI right: {[bin(x) for x in writeval]}.")
                    rpi.spi_write(self.hspi, writeval[0:4])
                    rpi.write(self.CS, 1)
                    time.sleep(0.001)
                    rpi.write(self.CS, 0)
                    rpi.spi_write(self.hspi, writeval[4:8])
                    rpi.write(self.CS, 1)
                    time.sleep(0.001)
                    rpi.write(self.CS, 0)
                    rpi.spi_write(self.hspi, writeval[8:])
                    self.set_right = 0
                
                rpi.write(self.CS, 1)
                
            else:
                # print(self.chip)
                pass
        except AttributeError:
            messagebox.showerror(title="Invalid chip",
                                 message="The selected delay line chip is not valid.")
        except Exception as e:
            print(e)

        return    


    def toggle_states(self):
        rpi.write(self.CS, 0)
        data = self.chip.set_bits(self.enable, self.select0, self.select1)
        rpi.spi_write(self.hspi, data)
        print(f"data on toggle: {[bin(x) for x in data]}")
        rpi.write(self.CS, 1)
        return


######
######
######
###### RESET DELAY FUNCTION
            
    def reset_delay(self, num):
        """ Resetting the delays to 0."""
        if num == 0:
            self.delay_left = 0            
            self.unit_left = ""
            self.set_delay(num)
            self.set_left = 0
            self.pw_str_left.set("Delay")
            self.pw_button_left['text'] = self.pw_str_left.get()

        if num == 1:
            self.delay_right = 0
            self.unit_right = 0
            self.set_delay(num)
            self.set_right = 0
            self.pw_str_right.set("Delay")
            self.pw_button_right['text'] = self.pw_str_right.get()

        self.pulse_width = 0
        self.unit = ""

        return 

######
######
######
###### TOGGLE BUTTONS FUNCTIONS

    def toggle_enable(self):
        if self.chip.get_name() == "MCP23S17":
            if self.enable == 0:
                self.enable = 1
            else:
                self.enable = 0
            
            if self.enable == 0:
                self.b_en_color = teal
                self.f_en_color = white_ish
            else:
                self.b_en_color = red
                self.f_en_color = white_ish

            self.toggle_states()

            self.button_enable.config(fg=self.f_en_color, bg=self.b_en_color, activebackground=self.b_en_color, activeforeground=self.f_en_color)
            self.pw_label_left.focus_set()
        else:
            return
        

    def toggle_select0(self):
        if self.chip.get_name() == "MCP23S17":
            if self.select0 == 0:
                self.select0 = 1
            else:
                self.select0 = 0

            if self.select0:
                self.b_s0_color = red
                self.f_s0_color = white_ish
            else:
                self.b_s0_color = teal
                self.f_s0_color = white_ish
            
            self.toggle_states()

            self.button_select0.config(fg=self.f_s0_color, bg=self.b_s0_color, activebackground=self.b_s0_color, activeforeground=self.f_s0_color)
        else:
            return


    def toggle_select1(self):
        if self.chip.get_name() == "MCP23S17":
            if self.select0 == 0:
                self.select0 = 1
            else:
                self.select0 = 0

            if self.select1:
                self.b_s1_color = red
                self.f_s1_color = white_ish
            else:
                self.b_s1_color = teal
                self.f_s1_color = white_ish

            self.toggle_states()

            self.button_select1.config(fg=self.f_s1_color, bg=self.b_s1_color, activebackground=self.b_s1_color, activeforeground=self.f_s1_color)
        else:
            return


###### 
######
######
###### CREATE WIDGETS FUNCTION

    def create_widgets(self):
        """      
        Adds frames, labels and text widgets to frames.

        """

        self.pw_str_left = tk.StringVar(self, value="Delay")
        self.pw_str_right = tk.StringVar(self, value="Delay")
        self.tbits = 0x3ffff
        self.delay_left = 0
        self.delay_right = 0
        self.enable = 1
        self.select0 = 1
        self.select1 = 1
        self.unit_left = ""
        self.unit_right = ""
        self.set_left = 0
        self.set_right = 0
        self.select_index = 0

        self.b_en_color = dark_gray
        self.f_en_color = white_ish
        self.b_s0_color = dark_gray
        self.f_s0_color = white_ish
        self.b_s1_color = dark_gray
        self.f_s1_color = white_ish

        self.chip = NOCHIP()

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
        LEVA STRAN DELAY
        """        
        self.pulse_frame_left = tk.Frame(self, 
                                         width=f'{self.width*ptomm}m',
                                         height=f'{self.height*ptomm}m',
                                         relief='flat',
                                         bg=light_gray)
        self.pulse_frame_left.place(relx=0.03,
                                    rely=0.05,
                                    relwidth=0.35,
                                    relheight=0.90)
        
        self.pw_label_left = tk.Label(self.pulse_frame_left,
                                          text='DELAY LINE A',
                                          font=titles,
                                          fg=space_blue,
                                          bg=light_gray,
                                          justify='center',
                                          height=20,
                                          width=20)
        self.pw_label_left.place(relx=0.5, 
                                 rely=0.1, 
                                 anchor='center')
        
        self.pw_button_left = tk.Button(self.pulse_frame_left,
                                        #    width=26,
                                        height=1,
                                        fg=space_blue,
                                        bg=white_ish,
                                        font=outputfont,
                                        text=self.pw_str_left.get(),
                                        relief='flat',
                                        command=lambda: self.set_delayval(0))
        self.pw_button_left.place(relx=0.5,
                                  rely=0.45,
                                  relwidth=0.9,
                                  anchor='center')

        self.reset_pw_button_left = tk.Button(self.pulse_frame_left,
                                              height=1,
                                              fg=space_blue,
                                              bg=light_gray,
                                              font=normal,
                                              text="RESET",
                                              relief='flat',
                                              command=lambda: self.reset_delay(0))
        self.reset_pw_button_left.place(relx=0.5,
                                      rely=0.75,
                                      relwidth=0.4,
                                      anchor='center')
        
        """
        DESNA STRAN DELAY
        """        
        self.pulse_frame_right = tk.Frame(self, 
                                         width=f'{self.width*ptomm}m',
                                         height=f'{self.height*ptomm}m',
                                         relief='flat',
                                         bg=light_gray)
        self.pulse_frame_right.place(relx=0.39,
                                    rely=0.05,
                                    relwidth=0.35,
                                    relheight=0.90)
        
        self.pw_label_right = tk.Label(self.pulse_frame_right,
                                          text='DELAY LINE B',
                                          font=titles,
                                          fg=space_blue,
                                          bg=light_gray,
                                          justify='center',
                                          height=20,
                                          width=20)
        self.pw_label_right.place(relx=0.5, 
                                 rely=0.1, 
                                 anchor='center')
        
        self.pw_button_right = tk.Button(self.pulse_frame_right,
                                        #    width=26,
                                        height=1,
                                        fg=space_blue,
                                        bg=white_ish,
                                        font=outputfont,
                                        text=self.pw_str_right.get(),
                                        relief='flat',
                                        command=lambda: self.set_delayval(1))
        self.pw_button_right.place(relx=0.5,
                                  rely=0.45,
                                  relwidth=0.9,
                                  anchor='center')

        self.reset_pw_button_right = tk.Button(self.pulse_frame_right,
                                              height=1,
                                              fg=space_blue,
                                              bg=light_gray,
                                              font=normal,
                                              text="RESET",
                                              relief='flat',
                                              command=lambda: self.reset_delay(1))
        self.reset_pw_button_right.place(relx=0.5,
                                      rely=0.75,
                                      relwidth=0.4,
                                      anchor='center')
        
        """
        DODATNI GUMBI
        """
        self.extra_buttons_frame = tk.Frame(self,
                                            width=f'{self.width*ptomm}m',
                                            height=f'{self.height*ptomm}m',
                                            relief='flat',
                                            bg=light_gray
                                            )
        self.extra_buttons_frame.place(relx=0.75,
                                       rely=0.05,
                                       relwidth=0.22,
                                       relheight=0.90)
        
        self.button_enable = tk.Button(self.extra_buttons_frame,
                                       height=2,
                                       fg=self.f_en_color,
                                       bg=self.b_en_color,
                                       font=normal,
                                       text="ENABLE",
                                       relief='flat',
                                       highlightcolor=self.f_en_color,
                                       highlightbackground=self.b_en_color,
                                       highlightthickness=0,
                                       activebackground=self.b_en_color,
                                       activeforeground=self.f_en_color,
                                       command=lambda: self.toggle_enable())
        self.button_enable.place(relx=0.5,
                                 rely=0.25,
                                 relwidth=0.8,
                                 anchor='center')
        
        self.button_select0 = tk.Button(self.extra_buttons_frame,
                                       height=2,
                                       fg=self.f_s0_color,
                                       bg=self.b_s0_color,
                                       font=normal,
                                       text="SELECT 0",
                                       relief='flat',
                                       highlightcolor=self.f_s0_color,
                                       highlightbackground=self.b_s0_color,
                                       highlightthickness=0,
                                       activebackground=self.b_s0_color,
                                       activeforeground=self.f_s0_color,
                                       command=lambda: self.toggle_select0())
        self.button_select0.place(relx=0.5,
                                  rely=0.5,
                                  relwidth=0.8,
                                  anchor='center')
        
        self.button_select1 = tk.Button(self.extra_buttons_frame,
                                       height=2,
                                       fg=self.f_s1_color,
                                       bg=self.b_s1_color,
                                       font=normal,
                                       text="SELECT 1",
                                       relief='flat',
                                       highlightcolor=self.f_s1_color,
                                       highlightbackground=self.b_s1_color,
                                       highlightthickness=0,
                                       activebackground=self.b_s1_color,
                                       activeforeground=self.f_s1_color,
                                       command=lambda: self.toggle_select1())
        self.button_select1.place(relx=0.5,
                                  rely=0.75,
                                  relwidth=0.8,
                                  anchor='center')

        return

###### 
######
######
###### MAIN WINDOW INITIALIZATION

    def __init__(self):

        tk.Tk.__init__(self)  # self = root window

        if updateService.is_branch_behind():
            update = messagebox.askyesno(title="New version available", message="New version od this app is available. Do you want to update now?")
            if update:
                updateService.git_pull()
                restart_program()
                
        # SPI
        global hspi
        self.hspi = rpi.spi_open(0, 100000)  # initialize SPI with 1 MHz freq in mode 0
        self.CS = 9
        self.SLOAD = 25
        rpi.set_mode(self.SLOAD, OUTPUT)
        rpi.set_mode(self.CS, OUTPUT)
        rpi.write(self.SLOAD, 0)
        rpi.write(self.CS, 1) 

        # GUI
        self.title('Delay Line Programator')
        self.attributes("-fullscreen", True)  # app window starts in borderless fullscreen mode
        self.bind("<F11>", lambda event: self.attributes("-fullscreen", not self.attributes("-fullscreen")))
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))  # keyboard key bindings for exiting fullscreen mode
        self.update_idletasks() 
        self.configure(bg=space_blue)

        # create widgets
        self.create_widgets()

###### 
######
######
###### START OF THE APPLICATION
        
if __name__ == '__main__':
    app = delayProgramator_app()
    app.mainloop()
###### END
