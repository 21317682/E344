from tkinter import Tk, ttk, mainloop, Frame, Text, END
from connection import ConnectionStatus, BeetleConnection

from time import sleep

class ConnectionFrame(Frame):
    def __create_connection(self):
        self.connection = BeetleConnection()

        def connection_callback(state):
            if state == ConnectionStatus.DISCONNECTED:
                self.event_disconnected()
            elif state == ConnectionStatus.CONNECTED:
                self.event_connected()
            elif state == ConnectionStatus.FAILED_TO_CONNECT:
                self.event_failed_to_connect()
            elif state == ConnectionStatus.DISCONNECTED_TIMEOUT:
                self.event_disconnected_timeout()
            elif state == ConnectionStatus.DISCONNECTED_ERROR:
                self.event_disconnected_error()
            else:
                raise Exception("Unhandled connection callback")

        self.connection.register_status_callback(connection_callback)

    def __set_connected_button(self):
        def connect_button_callback():
            self.connection.disconnect()

        self.connection.write(b"U")
        self.connection.write(b"\n")

        self.connect_button["command"] = connect_button_callback
        self.connect_button["text"] = "Disconnect"
        self.device_picker["state"] = "disabled"

    def __set_disconnected_button(self):
        def connect_button_callback():
            device = self.device_picker.get()
            self.connection.connect(device)

        self.connect_button["command"] = connect_button_callback
        self.connect_button["text"] = "Connect"

        self.device_picker["state"] = "normal"

    def __init__(self, main):
        self.main = main
        Frame.__init__(self, self.main.window, relief="ridge")

        self.__create_connection()

        self.device_label = ttk.Label(self, text="Device")
        self.device_label.grid(column=0, row=0, sticky="W")

        self.connection_label = ttk.Label(self, text="Connection")
        self.connection_label.grid(column=0, row=1, sticky="W")

        self.device_picker = ttk.Combobox(self, values=())
        self.device_picker.grid(column=1, row=0, sticky="WE", columnspan=2)

        self.connection_status_label = ttk.Label(self, text="")
        self.connection_status_label.grid(column=1, row=1, sticky="WE", columnspan=2)

        self.connect_button = ttk.Button(self, text="Connect")
        self.connect_button.grid(column=0, row=2, sticky="WE", columnspan=2)

        self.clear_button = ttk.Button(self, text="Clear all")
        self.clear_button.grid(column=2, row=2, sticky="WE")

        self.type_label = ttk.Label(self, text="Type : ")
        self.type_label.grid(column=0, row=4, sticky="W")

        self.type_entry = ttk.Entry(self)
        self.type_entry.grid(column=0, row=4, sticky="E")

        self.port_label = ttk.Label(self, text="Port : ")
        self.port_label.grid(column=1, row=4, sticky="W")

        self.port_entry = ttk.Entry(self)
        self.port_entry.grid(column=1, row=4, sticky="E")

        self.Uptime_button = ttk.Button(self, command = self.UptimeReturn, text="Uptime")
        self.Uptime_button.grid(column=2, row=4, sticky="WE")

        self.request_button = ttk.Button(self,command = self.SendRequest, text="Send Request")
        self.request_button.grid(column=0, row=5, sticky="WE", columnspan=3)

        self.return_text = Text(self)
        self.return_text.config(state='disabled')
        self.return_text.grid(column=0, row=6, sticky="WE", columnspan=3)
        self.return_text.see("end")
        self.clear()

        self.reset_button = ttk.Button(self,command = self.TripReset , text="Trip Reset")
        self.reset_button.config(state='disabled')
        self.reset_button.grid(column=0, row=7, sticky="WE", columnspan=3)

        self.voltage_label = ttk.Label(self, text="Voltage : ")
        self.voltage_label.grid(column=0, row=9, sticky="W")

        self.voltage_entry = ttk.Label(self, text= "")
        self.voltage_entry.grid(column=0, row=9, sticky="E")

        self.current_label = ttk.Label(self, text="Current : ")
        self.current_label.grid(column=0, row=10, sticky="W")

        self.current_entry = ttk.Label(self, text= "")
        self.current_entry.grid(column=0, row=10, sticky="E")

        self.phase_label = ttk.Label(self, text="Phase : ")
        self.phase_label.grid(column=0, row=11, sticky="W")

        self.phase_entry = ttk.Label(self, text= "")
        self.phase_entry.grid(column=0, row=11, sticky="E")

        self.trip_label = ttk.Label(self, text="")
        self.trip_label.grid(column=0, row=8, sticky="WE", columnspan=3)

        self.DEBUGMODE = False
        self.main.window.after(2000, self.refresh_debug)#self.printSerialReturn())
        self.main.window.after(500, self.refresh_stream)

        def clear_button_callback():
            self.clear()

        self.clear_button["command"] = clear_button_callback

    def refresh_debug(self):

        if self.DEBUGMODE == True and self.connection.is_connected():
            self.printSerialReturn()
        #else:
         #   self.DataStream()
        self.main.window.after(2000, self.refresh_debug)#self.printSerialReturn())
    
    def refresh_stream(self):

        if self.DEBUGMODE == False and self.connection.is_connected():
            self.DataStream()
        self.main.window.after(500, self.refresh_stream)#self.printSerialReturn())

    def event_connected(self):
        self.connection_label["text"] = "Connected"

        self.__set_connected_button()

    def event_disconnected(self):
        self.connection_label["text"] = "Disconnected"

        self.__set_disconnected_button()

    def event_disconnected_timeout(self):
        self.connection_label["text"] = "Disconnected (Timeout)"

        self.__set_disconnected_button()

    def event_disconnected_error(self):
        self.connection_label["text"] = "Disconnected (Error)"

        self.__set_disconnected_button()

    def event_failed_to_connect(self):
        self.connection_label["text"] = "Disconnected (Failed to connect)"

        self.__set_disconnected_button()

    def SendRequest(self):
        CommandType = self.type_entry.get()  #String is saved in Command
        CommandPort = self.port_entry.get()

        if not self.connection.is_connected():
            self.connection_status_label["text"] = "Cannot write when not connected"
            return

        # Entry validation:
        if CommandType not in ['0','1','2','X','x']:
            txt = "Please enter valid type (0,1,2,X)"
            self.connection_status_label["text"] = txt
            return

        else:
            self.connection_status_label["text"] = ''

        if CommandType == '1':
            if CommandPort not in ['0','1','2']:
                txt = "Please enter valid analogue port number (0,1,2)"
                self.connection_status_label["text"] = txt
                return

        elif CommandType == '2':
            if CommandPort not in ['0','1','2']:
                txt = "Please enter valid digital port number (0,1,2)"
                self.connection_status_label["text"] = txt
                return


        elif CommandType in ['x','X']:
            if CommandPort not in ['0','1']:
                txt = "Please enter 0 (debug off) or 1 (debug on) in port field"
                self.connection_status_label["text"] = txt
                return
            else:
                if CommandPort == '1':
                    self.DEBUGMODE = True
                    self.return_text.config(state='normal')
                    self.return_text.insert(END,"\n"+'Debug-Mode On')
                    self.return_text.config(state='disabled')
                    self.return_text.see("end")

                    self.connection.write(CommandType.encode('utf-8'))
                    self.connection.write(CommandPort.encode('utf-8'))
                else:
                    self.DEBUGMODE = False
                    self.type_entry.config(state='normal')

                    self.return_text.config(state='normal')
                    self.return_text.insert(END,"\n"+'Debug-Mode Off')
                    self.return_text.config(state='disabled')
                    self.return_text.see("end")

                    self.connection.write(CommandType.encode('utf-8'))
                    self.connection.write(CommandPort.encode('utf-8'))
        else:
            self.connection_status_label["text"] = ''

        self.connection.write(CommandType.encode('utf-8'))
        self.connection.write(CommandPort.encode('utf-8'))
        self.connection.write(b"\n")
        self.printSerialReturn()

    def printSerialReturn(self):
        sleep(0.02)
        OutputText = self.CleanList(self.connection.receive())

        if OutputText != '[]':
            self.return_text.config(state='normal')
            self.return_text.insert(END,"\n"+OutputText)
            self.return_text.config(state='disabled')
            self.return_text.see("end")

    def CleanList(self,InputList):
        OutputString = "["
        for returnstring in range(0,len(InputList)):
            if (returnstring != (len(InputList) - 1)):
                OutputString += str(InputList[returnstring][:-1]) + ', '
            else:
                OutputString += str(InputList[returnstring][:-1])

        OutputString += "]"
        return OutputString

    def UptimeReturn(self):
        if self.connection.is_connected():
            self.connection.write(b"U")
            self.connection.write(b"\n")
            self.printSerialReturn()
    
    def TripReset(self):
        if self.connection.is_connected():
            self.connection.write(b"R")
            self.connection.write(b"\n")
            self.printSerialReturn()
    
    def DataStream(self):
        sleep(0.02)
        dataArray = self.connection.receive()
        if len(dataArray) >= 4:
            self.voltage_entry["text"] = dataArray[0] + 'Vrms'
            #'%.3f'%(((int(dataArray[0])/1024)*(5/5.6)+(5/11))*23) + "V"
            self.current_entry["text"] = dataArray[1] + "mArms"
            #'%.3f'%(((((int(dataArray[1])/1024)*5)/14.6445)*1000)-6.5) + "mA"
            self.phase_entry["text"] = dataArray[2] + "degrees"
            #'%.3f'%(((int(dataArray[2])/1024)*5)/0.08712 - 1.3) + "°"
            if int(dataArray[4]) == 0:
                self.trip_label["text"] = "STATUS: Not Tripped"
                self.reset_button.config(state='disabled')
            else:
                self.trip_label["text"] = "STATUS: Tripped"
                self.reset_button.config(state='normal')
            

    def clear(self):

        if self.connection.is_connected():

            self.return_text.config(state='normal')
            self.return_text.delete(1.0,END)
            self.return_text.config(state='disabled')
            self.type_entry.delete(0,'end')
            self.port_entry.delete(0,'end')
            self.type_entry.config(state='normal')
            self.port_entry.config(state='normal')
            self.request_button.config(state='normal')
        else:
            self.return_text.config(state='normal')
            self.return_text.delete(1.0,END)
            self.return_text.config(state='disabled')
            self.type_entry.delete(0,'end')
            self.port_entry.delete(0,'end')
            self.type_entry.config(state='normal')
            self.port_entry.config(state='normal')
            self.request_button.config(state='normal')

            self.device_list = BeetleConnection.possible_connections()

            possible_values = [
                x.device for x in self.device_list if "Arduino" in str(x)
            ]
            self.device_picker["values"] = possible_values
            if len(possible_values) > 0:
                self.device_picker.current(0)
            self.event_disconnected()

class Main:

    def __init__(self):
        self.window = Tk()

        self.connection_frame = ConnectionFrame(self)
        self.connection_frame.grid(row=0, sticky="NWE", columnspan=3)

        self.window.title('Design (E)344 - Muthua - 21317682')
        self.window.iconbitmap(r'C:\Users\Alex Muthua\Pictures\e_e.ico')
        self.window.resizable(False, False)
        self.window.mainloop()


Main()
