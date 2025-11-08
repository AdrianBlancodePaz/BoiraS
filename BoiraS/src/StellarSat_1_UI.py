import tkinter
from tkinter import *
import customtkinter
import queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

np.set_printoptions(threshold=np.inf)

PACKET_RECEIVED_STATUS_DATA = None
NUM_PACKETS = None
data_queue_for_ui = None
telemetry_for_ui = None
ventana = None
label_data_var = None
SC_ID_DATA = None
TM_TYPE_DATA = None
OBC_APP_STATUS_DATA = None
OBC_SYS_CHECK_DATA = None
OBC_TIMESTAMP_D_DATA = None
OBC_TIMESTAMP_MS_DATA = None
OBC_TIME_REBOOT_DATA = None
OBC_BOOTCOUNTER_DATA = None
OBC_REBOOT_COUSE_DATA = None
OBC_SC_MODE_DATA = None
OBC_LAST_MODE_DATA = None
OBC_MODE_TIME_DATA = None
OBC_MODE_DATA = None
OBC_LAST_OB_TLE_DATA = None
OBC_GPS_STATE_DATA = None
OBC_GPS_TIME_DATA = None
COM_TC_LIST_DATA = None
COM_TC_COUNT_DATA = None
COM_TM_COUNT_DATA = None
COM_RSSI_DATA = None
COM_LAST_ERR_DATA = None
EPS_MODE_DATA = None
EPS_BAT_SOC_DATA = None
EPS_SP_CURRXP_DATA = None
EPS_SP_CURRXM_DATA = None
EPS_SP_CURRYP_DATA = None
EPS_SP_CURRYM_DATA = None
EPS_SP_CURRZP_DATA = None
EPS_SP_VOLTXP_DATA = None
EPS_SP_VOLTXM_DATA = None
EPS_SP_VOLTYP_DATA = None
EPS_SP_VOLTYM_DATA = None
EPS_SP_VOLTZP_DATA = None
EPS_PCDU_CURR_DATA = None
EPS_PCDU_VOLT_DATA = None
ADCS_MODE_DATA = None
ADCS_IMU_OMEGA_X_DATA = None
ADCS_IMU_OMEGA_Y_DATA = None
ADCS_IMU_OMEGA_Z_DATA = None
ADCS_IMU_MAG_X_DATA = None
ADCS_IMU_MAG_Y_DATA = None
ADCS_IMU_MAG_Z_DATA = None
ADCS_Q_X_DATA = None
ADCS_Q_Y_DATA = None
ADCS_Q_Z_DATA = None
ADCS_Q_W_DATA = None
ADCS_X_ECEF_DATA = None
ADCS_Y_ECEF_DATA = None
ADCS_Z_ECEF_DATA = None
THE_SP_TEMPXP_DATA = None
THE_SP_TEMPXM_DATA = None
THE_SP_TEMPYP_DATA = None
THE_SP_TEMPYM_DATA = None
THE_SP_TEMPZP_DATA = None
THE_ADCS_TEMP_DATA = None
THE_OBC_TEMP_DATA = None
THE_RFBOARD_TEMP_DATA = None
THE_PCDU_TEMP_DATA = None
THE_HEATER_STATE_DATA = None
THE_HEATER_TIME_DATA = None
PAY_NUM_DATA = None
PAY_TIME_LAST_DATA = None
MODU_SCHEME_DATA = None
CODE_SCHEME_DATA = None
INTERLEAVER_DATA = None
figure_frame = None
num_packets_ui = 0



def actualizar_variable():
    global num_packets_ui
    try:
        if data_queue_for_ui and label_data_var: 
            new_data_item = data_queue_for_ui.get_nowait()
            label_data_var.set(str(new_data_item))
            num_packets_ui+=1 
    except queue.Empty:
        pass
    except Exception as e:
        print(f"Error in UI update: {e}") 

    # Actualizamos mientras esté abierta la ventana
    if ventana and ventana.winfo_exists():
        ventana.after(200, actualizar_variable)

def actualizar_etiquetas():
    global num_packets_ui
    try:
        if telemetry_for_ui and TM_TYPE_DATA: 
            boira_data_for_ui = telemetry_for_ui.get_nowait()
            SC_ID_DATA.set(str(int(''.join(map(str,boira_data_for_ui['SC_ID'][0:16])),2)))
            TM_TYPE_DATA.set(str(int(''.join(map(str,boira_data_for_ui['TM_TYPE'][0:8])),2)))
            OBC_APP_STATUS_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_APP_STATUS'][0:16])),2)))
            OBC_SYS_CHECK_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_SYS_CHECK'][0:16])),2)))
            OBC_TIMESTAMP_D_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_TIMESTAMP_D'][0:16])),2)))
            OBC_TIMESTAMP_MS_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_TIMESTAMP_MS'][0:32])),2)))
            OBC_TIME_REBOOT_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_TIME_REBOOT'][0:32])),2)))
            OBC_BOOTCOUNTER_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_BOOTCOUNTER'][0:32])),2)))
            OBC_REBOOT_COUSE_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_REBOOT_CAUSE'][0:16])),2)))
            OBC_SC_MODE_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_SC_MODE'][0:8])),2)))
            OBC_LAST_MODE_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_LAST_MODE'][0:8])),2)))
            OBC_MODE_TIME_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_MODE_TIME'][0:32])),2)))
            OBC_MODE_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_MODE'][0:8])),2)))
            OBC_LAST_OB_TLE_DATA.set("received")
            OBC_GPS_STATE_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_GPS_STATE'][0:8])),2)))
            OBC_GPS_TIME_DATA.set(str(int(''.join(map(str,boira_data_for_ui['OBC_GPS_TIME'][0:32])),2)))
            COM_TC_LIST_DATA.set(str(int(''.join(map(str,boira_data_for_ui['COM_TC_LIST'][0:16])),2)))
            COM_TC_COUNT_DATA.set(str(int(''.join(map(str,boira_data_for_ui['COM_TC_COUNT'][0:32])),2)))
            COM_TM_COUNT_DATA.set(str(int(''.join(map(str,boira_data_for_ui['COM_TM_COUNT'][0:32])),2)))
            COM_RSSI_DATA.set(str(int(''.join(map(str,boira_data_for_ui['COM_RSSI'][0:16])),2)))
            COM_LAST_ERR_DATA.set(str(int(''.join(map(str,boira_data_for_ui['COM_LAST_ERR'][0:16])),2)))
            EPS_MODE_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_MODE'][0:8])),2)))
            EPS_BAT_SOC_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_BAT_SOC'][0:8])),2)))
            EPS_SP_CURRXM_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_SP_CURRXM'][0:16])),2)))
            EPS_SP_CURRXP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_SP_CURRXP'][0:16])),2)))
            EPS_SP_CURRYM_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_SP_CURRYM'][0:16])),2)))
            EPS_SP_CURRYP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_SP_CURRYP'][0:16])),2)))
            EPS_SP_CURRZP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_SP_CURRZP'][0:16])),2)))
            EPS_SP_VOLTXM_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_SP_VOLTXM'][0:16])),2)))
            EPS_SP_VOLTXP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_SP_VOLTXP'][0:16])),2)))
            EPS_SP_VOLTYM_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_SP_VOLTYM'][0:16])),2)))
            EPS_SP_VOLTYP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_SP_VOLTYP'][0:16])),2)))
            EPS_SP_VOLTZP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_SP_VOLTZP'][0:16])),2)))
            EPS_PCDU_CURR_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_PCDU_CURR'][0:16])),2)))
            EPS_PCDU_VOLT_DATA.set(str(int(''.join(map(str,boira_data_for_ui['EPS_PCDU_VOLT'][0:16])),2)))
            ADCS_MODE_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_MODE'][0:8])),2)))
            ADCS_IMU_OMEGA_X_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_IMU_OMEGA_X'][0:32])),2)))
            ADCS_IMU_OMEGA_Y_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_IMU_OMEGA_Y'][0:32])),2)))
            ADCS_IMU_OMEGA_Z_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_IMU_OMEGA_Z'][0:32])),2)))
            ADCS_IMU_MAG_X_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_IMU_MAG_X'][0:32])),2)))
            ADCS_IMU_MAG_Y_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_IMU_MAG_Y'][0:32])),2)))
            ADCS_IMU_MAG_Z_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_IMU_MAG_Z'][0:32])),2)))
            ADCS_Q_X_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_Q_X'][0:32])),2)))
            ADCS_Q_Y_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_Q_Y'][0:32])),2)))
            ADCS_Q_Z_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_Q_Z'][0:32])),2)))
            ADCS_Q_W_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_Q_W'][0:32])),2)))
            ADCS_X_ECEF_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_X_ECEF'][0:8])),2)))
            ADCS_Y_ECEF_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_Y_ECEF'][0:8])),2)))
            ADCS_Z_ECEF_DATA.set(str(int(''.join(map(str,boira_data_for_ui['ADCS_Z_ECEF'][0:8])),2)))
            THE_SP_TEMPXP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['THE_SP_TEMPXP'][0:16])),2)))
            THE_SP_TEMPXM_DATA.set(str(int(''.join(map(str,boira_data_for_ui['THE_SP_TEMPXM'][0:16])),2)))
            THE_SP_TEMPYP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['THE_SP_TEMPYP'][0:16])),2)))
            THE_SP_TEMPYM_DATA.set(str(int(''.join(map(str,boira_data_for_ui['THE_SP_TEMPYM'][0:16])),2)))
            THE_SP_TEMPZP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['THE_SP_TEMPZP'][0:16])),2)))
            THE_ADCS_TEMP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['THE_ADCS_TEMP'][0:16])),2)))
            THE_OBC_TEMP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['THE_OBC_TEMP'][0:16])),2)))
            THE_RFBOARD_TEMP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['THE_RFBOARD_TEMP'][0:16])),2)))
            THE_PCDU_TEMP_DATA.set(str(int(''.join(map(str,boira_data_for_ui['THE_PCDU_TEMP'][0:16])),2)))
            THE_HEATER_STATE_DATA.set(str(int(''.join(map(str,boira_data_for_ui['THE_HEATER_STATE'][0:8])),2)))
            THE_HEATER_TIME_DATA.set(str(int(''.join(map(str,boira_data_for_ui['THE_HEATER_TIME'][0:16])),2)))
            PAY_NUM_DATA.set(str(int(''.join(map(str,boira_data_for_ui['PAY_NUM'][0:8])),2)))
            PAY_TIME_LAST_DATA.set(str(int(''.join(map(str,boira_data_for_ui['PAY_TIME_LAST'][0:16])),2)))
            PACKET_RECEIVED_STATUS_DATA.set("Packet received!")
            NUM_PACKETS.set(str(num_packets_ui))
            MODU_SCHEME_DATA.set(str(int(''.join(map(str,boira_data_for_ui['MODU_SCHEME'][0:8])),2)))
            CODE_SCHEME_DATA.set(str(int(''.join(map(str,boira_data_for_ui['CODE_SCHEME'][0:8])),2)))
            INTERLEAVER_DATA.set(str(int(''.join(map(str,boira_data_for_ui['INTERLEAVER'][0:8])),2)))
            ventana.after(2000, lambda: PACKET_RECEIVED_STATUS_DATA.set("Awaiting packet..."))
            
    except queue.Empty:
        pass
    except Exception as e:
        print(f"Error in UI update: {e}") 
    # Actualizamos mientras esté abierta la ventana
    if ventana and ventana.winfo_exists():
        ventana.after(200, actualizar_etiquetas)


def UI(queue_data_demodulated, telemetry):
    global ventana, label_data_var, data_queue_for_ui, telemetry_for_ui, figure_frame, SC_ID_DATA, TM_TYPE_DATA, OBC_APP_STATUS_DATA, OBC_SYS_CHECK_DATA, OBC_TIMESTAMP_D_DATA, OBC_TIMESTAMP_MS_DATA, OBC_TIME_REBOOT_DATA,OBC_REBOOT_COUSE_DATA, OBC_BOOTCOUNTER_DATA, OBC_SC_MODE_DATA
    global OBC_LAST_MODE_DATA, OBC_MODE_TIME_DATA, OBC_MODE_DATA, OBC_LAST_OB_TLE_DATA, OBC_GPS_STATE_DATA, OBC_GPS_TIME_DATA, COM_TC_LIST_DATA, COM_TC_COUNT_DATA, COM_TM_COUNT_DATA, COM_RSSI_DATA, COM_LAST_ERR_DATA, EPS_MODE_DATA, EPS_BAT_SOC_DATA
    global EPS_SP_CURRXP_DATA, EPS_SP_CURRXM_DATA, EPS_SP_CURRYP_DATA, EPS_SP_CURRYM_DATA, EPS_SP_CURRZP_DATA, EPS_SP_VOLTXP_DATA, EPS_SP_VOLTXM_DATA, EPS_SP_VOLTYP_DATA, EPS_SP_VOLTYM_DATA, EPS_SP_VOLTZP_DATA, EPS_PCDU_CURR_DATA, EPS_PCDU_VOLT_DATA
    global ADCS_MODE_DATA, ADCS_IMU_OMEGA_X_DATA, ADCS_IMU_OMEGA_Y_DATA, ADCS_IMU_OMEGA_Z_DATA, ADCS_IMU_MAG_X_DATA, ADCS_IMU_MAG_Y_DATA, ADCS_IMU_MAG_Z_DATA, ADCS_Q_X_DATA, ADCS_Q_Y_DATA, ADCS_Q_Z_DATA, ADCS_Q_W_DATA, ADCS_X_ECEF_DATA, ADCS_Y_ECEF_DATA, ADCS_Z_ECEF_DATA, THE_SP_TEMPXP_DATA, THE_SP_TEMPXM_DATA
    global THE_SP_TEMPYP_DATA, THE_SP_TEMPYM_DATA, THE_SP_TEMPZP_DATA, THE_ADCS_TEMP_DATA, THE_OBC_TEMP_DATA, THE_RFBOARD_TEMP_DATA, THE_PCDU_TEMP_DATA, THE_HEATER_STATE_DATA, THE_HEATER_TIME_DATA, PAY_NUM_DATA, PAY_TIME_LAST_DATA
    global PACKET_RECEIVED_STATUS_DATA, NUM_PACKETS, MODU_SCHEME_DATA, CODE_SCHEME_DATA, INTERLEAVER_DATA

    data_queue_for_ui = queue_data_demodulated
    telemetry_for_ui = telemetry

    ventana = Tk()
    ventana.title("StellarSat Boira GS")
    ventana.geometry("1300x500")
    ventana.configure(bg="#73967c")
    PACKET_RECEIVED_STATUS_DATA = tkinter.StringVar() 
    PACKET_RECEIVED_STATUS_DATA.set("Awaiting packet...") 
    label_data_var = tkinter.StringVar()
    label_data_var.set("Waiting...")
    NUM_PACKETS = tkinter.StringVar()
    NUM_PACKETS.set("0")
    SC_ID_DATA = tkinter.StringVar()
    SC_ID_DATA.set("UNKNOWN")
    TM_TYPE_DATA = tkinter.StringVar()
    TM_TYPE_DATA.set("UNKNOWN")
    OBC_APP_STATUS_DATA = tkinter.StringVar()
    OBC_APP_STATUS_DATA.set("UNKNOWN")
    OBC_SYS_CHECK_DATA = tkinter.StringVar()
    OBC_SYS_CHECK_DATA.set("UNKNOWN")
    OBC_TIMESTAMP_D_DATA = tkinter.StringVar()
    OBC_TIMESTAMP_D_DATA.set("UNKNOWN")
    OBC_TIMESTAMP_MS_DATA = tkinter.StringVar()
    OBC_TIMESTAMP_MS_DATA.set("UNKNOWN")
    OBC_TIME_REBOOT_DATA = tkinter.StringVar()
    OBC_TIME_REBOOT_DATA.set("UNKNOWN")
    OBC_BOOTCOUNTER_DATA = tkinter.StringVar()
    OBC_BOOTCOUNTER_DATA.set("UNKNOWN")
    OBC_REBOOT_COUSE_DATA = tkinter.StringVar()
    OBC_REBOOT_COUSE_DATA.set("UNKNOWN")
    OBC_SC_MODE_DATA = tkinter.StringVar()
    OBC_SC_MODE_DATA.set("UNKNOWN")
    OBC_LAST_MODE_DATA = tkinter.StringVar()
    OBC_LAST_MODE_DATA.set("UNKNOWN")
    OBC_MODE_TIME_DATA = tkinter.StringVar()
    OBC_MODE_TIME_DATA.set("UNKNOWN")
    OBC_MODE_DATA = tkinter.StringVar()
    OBC_MODE_DATA.set("UNKNOWN")
    OBC_LAST_OB_TLE_DATA = tkinter.StringVar()
    OBC_LAST_OB_TLE_DATA.set("UNKNOWN")
    OBC_GPS_STATE_DATA = tkinter.StringVar()
    OBC_GPS_STATE_DATA.set("UNKNOWN")
    OBC_GPS_TIME_DATA = tkinter.StringVar()
    OBC_GPS_TIME_DATA.set("UNKNOWN")
    COM_TC_LIST_DATA = tkinter.StringVar()
    COM_TC_LIST_DATA.set("UNKNOWN")
    COM_TC_COUNT_DATA = tkinter.StringVar()
    COM_TC_COUNT_DATA.set("UNKNOWN")
    COM_TM_COUNT_DATA = tkinter.StringVar()
    COM_TM_COUNT_DATA.set("UNKNOWN")
    COM_RSSI_DATA = tkinter.StringVar()
    COM_RSSI_DATA.set("UNKNOWN")
    COM_LAST_ERR_DATA = tkinter.StringVar()
    COM_LAST_ERR_DATA.set("UNKNOWN")
    EPS_MODE_DATA = tkinter.StringVar()
    EPS_MODE_DATA.set("UNKNOWN")
    EPS_BAT_SOC_DATA = tkinter.StringVar()
    EPS_BAT_SOC_DATA.set("UNKNOWN")
    EPS_SP_CURRXP_DATA = tkinter.StringVar()
    EPS_SP_CURRXP_DATA.set("UNKNOWN")
    EPS_SP_CURRXM_DATA = tkinter.StringVar()
    EPS_SP_CURRXM_DATA.set("UNKNOWN")
    EPS_SP_CURRYP_DATA = tkinter.StringVar()
    EPS_SP_CURRYP_DATA.set("UNKNOWN")
    EPS_SP_CURRYM_DATA = tkinter.StringVar()
    EPS_SP_CURRYM_DATA.set("UNKNOWN")
    EPS_SP_CURRZP_DATA = tkinter.StringVar()
    EPS_SP_CURRZP_DATA.set("UNKNOWN")
    EPS_SP_VOLTXP_DATA = tkinter.StringVar()
    EPS_SP_VOLTXP_DATA.set("UNKNOWN")
    EPS_SP_VOLTXM_DATA = tkinter.StringVar()
    EPS_SP_VOLTXM_DATA.set("UNKNOWN")
    EPS_SP_VOLTYP_DATA = tkinter.StringVar()
    EPS_SP_VOLTYP_DATA.set("UNKNOWN")
    EPS_SP_VOLTYM_DATA = tkinter.StringVar()
    EPS_SP_VOLTYM_DATA.set("UNKNOWN")
    EPS_SP_VOLTZP_DATA = tkinter.StringVar()
    EPS_SP_VOLTZP_DATA.set("UNKNOWN")
    EPS_PCDU_CURR_DATA = tkinter.StringVar()
    EPS_PCDU_CURR_DATA.set("UNKNOWN")
    EPS_PCDU_VOLT_DATA = tkinter.StringVar()
    EPS_PCDU_VOLT_DATA.set("UNKNOWN")
    ADCS_MODE_DATA = tkinter.StringVar()
    ADCS_MODE_DATA.set("UNKNOWN")
    ADCS_IMU_OMEGA_X_DATA = tkinter.StringVar()
    ADCS_IMU_OMEGA_X_DATA.set("UNKNOWN")
    ADCS_IMU_OMEGA_Y_DATA = tkinter.StringVar()
    ADCS_IMU_OMEGA_Y_DATA.set("UNKNOWN")
    ADCS_IMU_OMEGA_Z_DATA = tkinter.StringVar()
    ADCS_IMU_OMEGA_Z_DATA.set("UNKNOWN")
    ADCS_Q_X_DATA = tkinter.StringVar()
    ADCS_Q_X_DATA.set("UNKNOWN")
    ADCS_Q_Y_DATA = tkinter.StringVar()
    ADCS_Q_Y_DATA.set("UNKNOWN")
    ADCS_Q_Z_DATA = tkinter.StringVar()
    ADCS_Q_Z_DATA.set("UNKNOWN")
    ADCS_Q_W_DATA = tkinter.StringVar()
    ADCS_Q_W_DATA.set("UNKNOWN")
    ADCS_IMU_MAG_X_DATA = tkinter.StringVar()
    ADCS_IMU_MAG_X_DATA.set("UNKNOWN")
    ADCS_IMU_MAG_Y_DATA = tkinter.StringVar()
    ADCS_IMU_MAG_Y_DATA.set("UNKNOWN")
    ADCS_IMU_MAG_Z_DATA = tkinter.StringVar()
    ADCS_IMU_MAG_Z_DATA.set("UNKNOWN")
    ADCS_X_ECEF_DATA = tkinter.StringVar()
    ADCS_X_ECEF_DATA.set("UNKNOWN")
    ADCS_Y_ECEF_DATA = tkinter.StringVar()
    ADCS_Y_ECEF_DATA.set("UNKNOWN")
    ADCS_Z_ECEF_DATA = tkinter.StringVar()
    ADCS_Z_ECEF_DATA.set("UNKNOWN")
    THE_SP_TEMPXP_DATA = tkinter.StringVar()
    THE_SP_TEMPXP_DATA.set("UNKNOWN")
    THE_SP_TEMPXM_DATA = tkinter.StringVar()
    THE_SP_TEMPXM_DATA.set("UNKNOWN")
    THE_SP_TEMPYP_DATA = tkinter.StringVar()
    THE_SP_TEMPYP_DATA.set("UNKNOWN")
    THE_SP_TEMPYM_DATA = tkinter.StringVar()
    THE_SP_TEMPYM_DATA.set("UNKNOWN")
    THE_SP_TEMPZP_DATA = tkinter.StringVar()
    THE_SP_TEMPZP_DATA.set("UNKNOWN")
    THE_ADCS_TEMP_DATA = tkinter.StringVar()
    THE_ADCS_TEMP_DATA.set("UNKNOWN")
    THE_OBC_TEMP_DATA = tkinter.StringVar()
    THE_OBC_TEMP_DATA.set("UNKNOWN")
    THE_RFBOARD_TEMP_DATA = tkinter.StringVar()
    THE_RFBOARD_TEMP_DATA.set("UNKNOWN")
    THE_PCDU_TEMP_DATA = tkinter.StringVar()
    THE_PCDU_TEMP_DATA.set("UNKNOWN")
    THE_HEATER_STATE_DATA = tkinter.StringVar()
    THE_HEATER_STATE_DATA.set("UNKNOWN")
    THE_HEATER_TIME_DATA = tkinter.StringVar()
    THE_HEATER_TIME_DATA.set("UNKNOWN")
    PAY_NUM_DATA = tkinter.StringVar()
    PAY_NUM_DATA.set("UNKNOWN")
    PAY_TIME_LAST_DATA = tkinter.StringVar()
    PAY_TIME_LAST_DATA.set("UNKNOWN")
    MODU_SCHEME_DATA = tkinter.StringVar()
    MODU_SCHEME_DATA.set("UNKNOWN")
    CODE_SCHEME_DATA = tkinter.StringVar()
    CODE_SCHEME_DATA.set("UNKNOWN")
    INTERLEAVER_DATA = tkinter.StringVar()
    INTERLEAVER_DATA.set("UNKNOWN")

    lbl_packet = customtkinter.CTkLabel(master=ventana, textvariable=label_data_var,
                                font=("Arial",6),text_color="#000000",height=460,
                                width=440,corner_radius=10,bg_color="#73967c",fg_color="#badec3",)
    lbl_packet.place(x=840,y=20)
    figure_frame=tkinter.Frame(ventana)
    figure_frame.configure(bg="#badec3", width=790, height=460)
    figure_frame.place(x=20,y=20)

    Label_PACKET_RECEIVED_STATUS = customtkinter.CTkLabel(
        master=ventana,
        textvariable=PACKET_RECEIVED_STATUS_DATA,
        font=("Arial", 10, "bold"),
        text_color="#000000",      # Black text
        height=20,
        width=130,                 # Adjusted width
        corner_radius=0,
        bg_color="#73967c",        
        fg_color="#768c6e"         )
    Label_PACKET_RECEIVED_STATUS.place(x=560, y=380)
    Label_NUM_PACKETS = customtkinter.CTkLabel(
        master=ventana,
        textvariable=NUM_PACKETS,
        font=("Arial", 10, "bold"),
        text_color="#000000",      # Black text
        height=20,
        width=100,                 # Adjusted width
        corner_radius=0,
        bg_color="#73967c",        
        fg_color="#768c6e"         )
    Label_NUM_PACKETS.place(x=690, y=380)
    Label_MODU_SCHEME = customtkinter.CTkLabel(
        master=ventana,
        text="MODU_SCHEME",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",)
    Label_MODU_SCHEME.place(x=560, y=420)
    Label_MODU_SCHEME_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=MODU_SCHEME_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",)
    Label_MODU_SCHEME_DATA.place(x=690, y=420)
    Label_CODE_SCHEME = customtkinter.CTkLabel(
        master=ventana,
        text="CODE_SCHEME",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",)
    Label_CODE_SCHEME.place(x=560, y=440)
    Label_CODE_SCHEME_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=CODE_SCHEME_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",)
    Label_CODE_SCHEME_DATA.place(x=690, y=440)
    Label_INTERLEAVER = customtkinter.CTkLabel(
        master=ventana,
        text="INTERLEAVER",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",)
    Label_INTERLEAVER.place(x=560, y=460)
    Label_INTERLEAVER_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=INTERLEAVER_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",)
    Label_INTERLEAVER_DATA.place(x=690, y=460)
    Label_SC_ID = customtkinter.CTkLabel(
        master=ventana,
        text="SC_ID",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e", #ESO
        )
    Label_SC_ID.place(x=20, y=20)
    Label_SC_ID_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=SC_ID_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_SC_ID_DATA.place(x=150, y=20)
    Label_TM_TYPE = customtkinter.CTkLabel(
        master=ventana,
        text="TM_TYPE",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_TM_TYPE.place(x=20, y=40)
    Label_TM_TYPE_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=TM_TYPE_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_TM_TYPE_DATA.place(x=150, y=40)
    Label_OBC_APP_STATUS = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_APP_STATUS",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_APP_STATUS.place(x=20, y=60)
    Label_OBC_APP_STATUS_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_APP_STATUS_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_APP_STATUS_DATA.place(x=150, y=60)
    Label_OBC_SYS_CHECK = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_SYS_CHECK",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_SYS_CHECK.place(x=20, y=80)
    Label_OBC_SYS_CHECK_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_SYS_CHECK_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_SYS_CHECK_DATA.place(x=150, y=80)
    Label_OBC_TIMESTAMP_D = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_TIMESTAMP_D",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_TIMESTAMP_D.place(x=20, y=100)
    Label_OBC_TIMESTAMP_D_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_TIMESTAMP_D_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_TIMESTAMP_D_DATA.place(x=150, y=100)
    Label_OBC_TIMESTAMP_MS = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_TIMESTAMP_MS",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_TIMESTAMP_MS.place(x=20, y=120)
    Label_OBC_TIMESTAMP_MS_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_TIMESTAMP_MS_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_TIMESTAMP_MS_DATA.place(x=150, y=120)
    Label_OBC_TIME_REBOOT = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_TIME_REBOOT",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_TIME_REBOOT.place(x=20, y=140)
    Label_OBC_TIME_REBOOT_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_TIME_REBOOT_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_TIME_REBOOT_DATA.place(x=150, y=140)
    Label_OBC_BOOTCOUNTER = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_BOOTCOUNTER",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_BOOTCOUNTER.place(x=20, y=160)
    Label_OBC_BOOTCOUNTER_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_BOOTCOUNTER_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_BOOTCOUNTER_DATA.place(x=150, y=160)
    Label_OBC_REBOOT_COUSE = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_REBOOT_COUSE",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_REBOOT_COUSE.place(x=20, y=180)
    Label_OBC_REBOOT_COUSE_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_REBOOT_COUSE_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_REBOOT_COUSE_DATA.place(x=150, y=180)
    Label_OBC_SC_MODE = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_SC_MODE",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_SC_MODE.place(x=20, y=200)
    Label_OBC_SC_MODE_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_SC_MODE_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_SC_MODE_DATA.place(x=150, y=200)
    Label_OBC_LAST_MODE = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_LAST_MODE",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_LAST_MODE.place(x=20, y=220)
    Label_OBC_LAST_MODE_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_LAST_MODE_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_LAST_MODE_DATA.place(x=150, y=220)
    Label_OBC_MODE_TIME = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_MODE_TIME",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_MODE_TIME.place(x=20, y=240)
    Label_OBC_MODE_TIME_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_MODE_TIME_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_MODE_TIME_DATA.place(x=150, y=240)
    Label_OBC_MODE = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_MODE",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_MODE.place(x=20, y=260)
    Label_OBC_MODE_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_MODE_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_MODE_DATA.place(x=150, y=260)
    Label_OBC_LAST_OB_TLE = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_LAST_OB_TLE",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_LAST_OB_TLE.place(x=20, y=280)
    Label_OBC_LAST_OB_TLE_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_LAST_OB_TLE_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_LAST_OB_TLE_DATA.place(x=150, y=280)
    Label_OBC_GPS_STATE = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_GPS_STATE",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_GPS_STATE.place(x=20, y=300)
    Label_OBC_GPS_STATE_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_GPS_STATE_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_GPS_STATE_DATA.place(x=150, y=300)
    Label_OBC_GPS_TIME = customtkinter.CTkLabel(
        master=ventana,
        text="OBC_GPS_TIME",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_OBC_GPS_TIME.place(x=20, y=320)
    Label_OBC_GPS_TIME_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=OBC_GPS_TIME_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_OBC_GPS_TIME_DATA.place(x=150, y=320)
    Label_COM_TC_LIST = customtkinter.CTkLabel(
        master=ventana,
        text="COM_TC_LIST",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_COM_TC_LIST.place(x=20, y=340)
    Label_COM_TC_LIST_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=COM_TC_LIST_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_COM_TC_LIST_DATA.place(x=150, y=340)
    Label_COM_TC_COUNT = customtkinter.CTkLabel(
        master=ventana,
        text="TC_COUNT",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_COM_TC_COUNT.place(x=20, y=360)
    Label_COM_TC_COUNT_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=COM_TC_COUNT_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_COM_TC_COUNT_DATA.place(x=150, y=360)
    Label_COM_TM_COUNT = customtkinter.CTkLabel(
        master=ventana,
        text="TM_COUNT",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_COM_TM_COUNT.place(x=20, y=380)
    Label_COM_TM_COUNT_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=COM_TM_COUNT_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_COM_TM_COUNT_DATA.place(x=150, y=380)
    Label_COM_RSSI = customtkinter.CTkLabel(
        master=ventana,
        text="COM_RSSI",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_COM_RSSI.place(x=20, y=400)
    Label_COM_RSSI_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=COM_RSSI_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_COM_RSSI_DATA.place(x=150, y=400)
    Label_COM_LAST_ERR = customtkinter.CTkLabel(
        master=ventana,
        text="COM_LAST_ERR",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_COM_LAST_ERR.place(x=20, y=420)
    Label_COM_LAST_ERR_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=COM_LAST_ERR_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_COM_LAST_ERR_DATA.place(x=150, y=420)
    Label_EPS_MODE = customtkinter.CTkLabel(
        master=ventana,
        text="EPS_MODE",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_EPS_MODE.place(x=20, y=440)
    Label_EPS_MODE_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=EPS_MODE_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_EPS_MODE_DATA.place(x=150, y=440)
    Label_EPS_BAT_SOC = customtkinter.CTkLabel(
        master=ventana,
        text="EPS_BAT_SOC",
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=130,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#768c6e",
        )
    Label_EPS_BAT_SOC.place(x=20, y=460)
    Label_EPS_BAT_SOC_DATA = customtkinter.CTkLabel(
        master=ventana,
        textvariable=EPS_BAT_SOC_DATA,
        font=("Arial", 11),
        text_color="#000000",
        height=20,
        width=100,
        corner_radius=0,
        bg_color="#73967c",
        fg_color="#FFFFFF",
        )
    Label_EPS_BAT_SOC_DATA.place(x=150, y=460)
    Label_EPS_SP_CURRXP = customtkinter.CTkLabel(
        master=ventana, text="EPS_SP_CURRXP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_SP_CURRXP.place(x=290, y=20)
    Label_EPS_SP_CURRXP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_SP_CURRXP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_SP_CURRXP_DATA.place(x=420, y=20)
    Label_EPS_SP_CURRXM = customtkinter.CTkLabel(
        master=ventana, text="EPS_SP_CURRXM", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_SP_CURRXM.place(x=290, y=40)
    Label_EPS_SP_CURRXM_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_SP_CURRXM_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_SP_CURRXM_DATA.place(x=420, y=40)
    Label_EPS_SP_CURRYP = customtkinter.CTkLabel(
        master=ventana, text="EPS_SP_CURRYP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_SP_CURRYP.place(x=290, y=60)
    Label_EPS_SP_CURRYP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_SP_CURRYP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_SP_CURRYP_DATA.place(x=420, y=60)
    Label_EPS_SP_CURRYM = customtkinter.CTkLabel(
        master=ventana, text="EPS_SP_CURRYM", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_SP_CURRYM.place(x=290, y=80)
    Label_EPS_SP_CURRYM_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_SP_CURRYM_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_SP_CURRYM_DATA.place(x=420, y=80)
    Label_EPS_SP_CURRZP = customtkinter.CTkLabel(
        master=ventana, text="EPS_SP_CURRZP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_SP_CURRZP.place(x=290, y=100)
    Label_EPS_SP_CURRZP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_SP_CURRZP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_SP_CURRZP_DATA.place(x=420, y=100)
    Label_EPS_SP_VOLTXP = customtkinter.CTkLabel(
        master=ventana, text="EPS_SP_VOLTXP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_SP_VOLTXP.place(x=290, y=120)
    Label_EPS_SP_VOLTXP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_SP_VOLTXP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_SP_VOLTXP_DATA.place(x=420, y=120)
    Label_EPS_SP_VOLTXM = customtkinter.CTkLabel(
        master=ventana, text="EPS_SP_VOLTXM", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_SP_VOLTXM.place(x=290, y=140)
    Label_EPS_SP_VOLTXM_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_SP_VOLTXM_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_SP_VOLTXM_DATA.place(x=420, y=140)
    Label_EPS_SP_VOLTYP = customtkinter.CTkLabel(
        master=ventana, text="EPS_SP_VOLTYP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_SP_VOLTYP.place(x=290, y=160)
    Label_EPS_SP_VOLTYP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_SP_VOLTYP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_SP_VOLTYP_DATA.place(x=420, y=160)
    Label_EPS_SP_VOLTYM = customtkinter.CTkLabel(
        master=ventana, text="EPS_SP_VOLTYM", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_SP_VOLTYM.place(x=290, y=180)
    Label_EPS_SP_VOLTYM_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_SP_VOLTYM_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_SP_VOLTYM_DATA.place(x=420, y=180)
    Label_EPS_SP_VOLTZP = customtkinter.CTkLabel(
        master=ventana, text="EPS_SP_VOLTZP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_SP_VOLTZP.place(x=290, y=200)
    Label_EPS_SP_VOLTZP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_SP_VOLTZP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_SP_VOLTZP_DATA.place(x=420, y=200)
    Label_EPS_PCDU_CURR = customtkinter.CTkLabel(
        master=ventana, text="EPS_PCDU_CURR", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_PCDU_CURR.place(x=290, y=220)
    Label_EPS_PCDU_CURR_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_PCDU_CURR_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_PCDU_CURR_DATA.place(x=420, y=220)
    Label_EPS_PCDU_VOLT = customtkinter.CTkLabel(
        master=ventana, text="EPS_PCDU_VOLT", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_EPS_PCDU_VOLT.place(x=290, y=240)
    Label_EPS_PCDU_VOLT_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=EPS_PCDU_VOLT_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_EPS_PCDU_VOLT_DATA.place(x=420, y=240)
    Label_ADCS_MODE = customtkinter.CTkLabel(
        master=ventana, text="ADCS_MODE", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_MODE.place(x=290, y=260)
    Label_ADCS_MODE_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_MODE_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_MODE_DATA.place(x=420, y=260)
    Label_ADCS_IMU_OMEGA_X = customtkinter.CTkLabel(
        master=ventana, text="ADCS_IMU_OMEGA_X", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_IMU_OMEGA_X.place(x=290, y=280)
    Label_ADCS_IMU_OMEGA_X_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_IMU_OMEGA_X_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_IMU_OMEGA_X_DATA.place(x=420, y=280)
    Label_ADCS_IMU_OMEGA_Y = customtkinter.CTkLabel(
        master=ventana, text="ADCS_IMU_OMEGA_Y", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_IMU_OMEGA_Y.place(x=290, y=300)
    Label_ADCS_IMU_OMEGA_Y_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_IMU_OMEGA_Y_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_IMU_OMEGA_Y_DATA.place(x=420, y=300)
    Label_ADCS_IMU_OMEGA_Z = customtkinter.CTkLabel(
        master=ventana, text="ADCS_IMU_OMEGA_Z", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_IMU_OMEGA_Z.place(x=290, y=320)
    Label_ADCS_IMU_OMEGA_Z_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_IMU_OMEGA_Z_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_IMU_OMEGA_Z_DATA.place(x=420, y=320)
    Label_ADCS_IMU_MAG_X = customtkinter.CTkLabel(
        master=ventana, text="ADCS_IMU_MAG_X", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_IMU_MAG_X.place(x=290, y=340)
    Label_ADCS_IMU_MAG_X_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_IMU_MAG_X_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_IMU_MAG_X_DATA.place(x=420, y=340)
    Label_ADCS_IMU_MAG_Y = customtkinter.CTkLabel(
        master=ventana, text="ADCS_IMU_MAG_Y", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_IMU_MAG_Y.place(x=290, y=360)
    Label_ADCS_IMU_MAG_Y_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_IMU_MAG_Y_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_IMU_MAG_Y_DATA.place(x=420, y=360)
    Label_ADCS_IMU_MAG_Z = customtkinter.CTkLabel(
        master=ventana, text="ADCS_IMU_MAG_Z", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_IMU_MAG_Z.place(x=290, y=380)
    Label_ADCS_IMU_MAG_Z_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_IMU_MAG_Z_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_IMU_MAG_Z_DATA.place(x=420, y=380)
    Label_ADCS_Q_X = customtkinter.CTkLabel(
        master=ventana, text="ADCS_Q_X", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_Q_X.place(x=290, y=400)
    Label_ADCS_Q_X_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_Q_X_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_Q_X_DATA.place(x=420, y=400)
    Label_ADCS_Q_Y = customtkinter.CTkLabel(
        master=ventana, text="ADCS_Q_Y", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_Q_Y.place(x=290, y=420)
    Label_ADCS_Q_Y_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_Q_Y_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_Q_Y_DATA.place(x=420, y=420)
    Label_ADCS_Q_Z = customtkinter.CTkLabel(
        master=ventana, text="ADCS_Q_Z", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_Q_Z.place(x=290, y=440)
    Label_ADCS_Q_Z_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_Q_Z_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_Q_Z_DATA.place(x=420, y=440)
    Label_ADCS_Q_W = customtkinter.CTkLabel(
        master=ventana, text="ADCS_Q_W", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_Q_W.place(x=290, y=460)
    Label_ADCS_Q_W_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_Q_W_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_Q_W_DATA.place(x=420, y=460)
    Label_ADCS_X_ECEF = customtkinter.CTkLabel(
        master=ventana, text="ADCS_X_ECEF", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_X_ECEF.place(x=560, y=20)
    Label_ADCS_X_ECEF_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_X_ECEF_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_X_ECEF_DATA.place(x=690, y=20)
    Label_ADCS_Y_ECEF = customtkinter.CTkLabel(
        master=ventana, text="ADCS_Y_ECEF", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_Y_ECEF.place(x=560, y=40)
    Label_ADCS_Y_ECEF_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_Y_ECEF_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_Y_ECEF_DATA.place(x=690, y=40)
    Label_ADCS_Z_ECEF = customtkinter.CTkLabel(
        master=ventana, text="ADCS_Z_ECEF", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_ADCS_Z_ECEF.place(x=560, y=60)
    Label_ADCS_Z_ECEF_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=ADCS_Z_ECEF_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_ADCS_Z_ECEF_DATA.place(x=690, y=60)
    Label_THE_SP_TEMPXP = customtkinter.CTkLabel(
        master=ventana, text="THE_SP_TEMPXP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_THE_SP_TEMPXP.place(x=560, y=80)
    Label_THE_SP_TEMPXP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=THE_SP_TEMPXP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_THE_SP_TEMPXP_DATA.place(x=690, y=80)
    Label_THE_SP_TEMPXM = customtkinter.CTkLabel(
        master=ventana, text="THE_SP_TEMPXM", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_THE_SP_TEMPXM.place(x=560, y=100)
    Label_THE_SP_TEMPXM_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=THE_SP_TEMPXM_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_THE_SP_TEMPXM_DATA.place(x=690, y=100)
    Label_THE_SP_TEMPYP = customtkinter.CTkLabel(
        master=ventana, text="THE_SP_TEMPYP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_THE_SP_TEMPYP.place(x=560, y=120)
    Label_THE_SP_TEMPYP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=THE_SP_TEMPYP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_THE_SP_TEMPYP_DATA.place(x=690, y=120)
    Label_THE_SP_TEMPYM = customtkinter.CTkLabel(
        master=ventana, text="THE_SP_TEMPYM", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_THE_SP_TEMPYM.place(x=560, y=140)
    Label_THE_SP_TEMPYM_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=THE_SP_TEMPYM_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_THE_SP_TEMPYM_DATA.place(x=690, y=140)
    Label_THE_SP_TEMPZP = customtkinter.CTkLabel(
        master=ventana, text="THE_SP_TEMPZP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_THE_SP_TEMPZP.place(x=560, y=160)
    Label_THE_SP_TEMPZP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=THE_SP_TEMPZP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_THE_SP_TEMPZP_DATA.place(x=690, y=160)
    Label_THE_ADCS_TEMP = customtkinter.CTkLabel(
        master=ventana, text="THE_ADCS_TEMP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_THE_ADCS_TEMP.place(x=560, y=180)
    Label_THE_ADCS_TEMP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=THE_ADCS_TEMP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_THE_ADCS_TEMP_DATA.place(x=690, y=180)
    Label_THE_OBC_TEMP = customtkinter.CTkLabel(
        master=ventana, text="THE_OBC_TEMP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_THE_OBC_TEMP.place(x=560, y=200)
    Label_THE_OBC_TEMP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=THE_OBC_TEMP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_THE_OBC_TEMP_DATA.place(x=690, y=200)
    Label_THE_RFBOARD_TEMP = customtkinter.CTkLabel(
        master=ventana, text="THE_RFBOARD_TEMP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_THE_RFBOARD_TEMP.place(x=560, y=220)
    Label_THE_RFBOARD_TEMP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=THE_RFBOARD_TEMP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_THE_RFBOARD_TEMP_DATA.place(x=690, y=220)
    Label_THE_PCDU_TEMP = customtkinter.CTkLabel(
        master=ventana, text="THE_PCDU_TEMP", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_THE_PCDU_TEMP.place(x=560, y=240)
    Label_THE_PCDU_TEMP_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=THE_PCDU_TEMP_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_THE_PCDU_TEMP_DATA.place(x=690, y=240)
    Label_THE_HEATER_STATE = customtkinter.CTkLabel(
        master=ventana, text="THE_HEATER_STATE", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_THE_HEATER_STATE.place(x=560, y=260)
    Label_THE_HEATER_STATE_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=THE_HEATER_STATE_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_THE_HEATER_STATE_DATA.place(x=690, y=260)
    Label_THE_HEATER_TIME = customtkinter.CTkLabel(
        master=ventana, text="THE_HEATER_TIME", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_THE_HEATER_TIME.place(x=560, y=280)
    Label_THE_HEATER_TIME_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=THE_HEATER_TIME_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_THE_HEATER_TIME_DATA.place(x=690, y=280)
    Label_PAY_NUM = customtkinter.CTkLabel(
        master=ventana, text="PAY_NUM", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_PAY_NUM.place(x=560, y=300)
    Label_PAY_NUM_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=PAY_NUM_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_PAY_NUM_DATA.place(x=690, y=300)
    Label_PAY_TIME_LAST = customtkinter.CTkLabel(
        master=ventana, text="PAY_TIME_LAST", font=("Arial", 11), text_color="#000000",
        height=20, width=130, corner_radius=0, bg_color="#73967c", fg_color="#768c6e"
        )
    Label_PAY_TIME_LAST.place(x=560, y=320)
    Label_PAY_TIME_LAST_DATA = customtkinter.CTkLabel(
        master=ventana, textvariable=PAY_TIME_LAST_DATA, font=("Arial", 11), text_color="#000000",
        height=20, width=100, corner_radius=0, bg_color="#73967c", fg_color="#FFFFFF"
        )
    Label_PAY_TIME_LAST_DATA.place(x=690, y=320)





    actualizar_variable()
    actualizar_etiquetas()
    ventana.mainloop()
