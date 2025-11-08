import numpy as np
from numpy import matlib
import adi
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal
import scipy.signal.signaltools as sigtool
import time
import math
from multiprocessing import Process, Queue as mpQueue, Value
import threading
import queue
import StellarSat_1_UI
import tkinter
from tkinter import *
from sk_dsp_comm.fec_conv import FECConv as fec_conv
import reedsolo as rs
from reedsolo import RSCodec, ReedSolomonError
import time
import pickle
import os
np.set_printoptions(threshold=np.inf)

#------|PARAMETERS|------#
fs=1.2e6 #Hz-- Frecuencia de muestreo
fc=435.299987e6 #Hz-- Frecuencia central tx
fc_rx=438.305e6 #Hz-- Frecuencia central rx
devf=10e3 #Hz-- Desviación en frecuencia (2*BW)
num_samps=50000 #Samples per time Pluto
sps=500#Samples per symbol
goldSeq=np.array([ 0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1
                ,1,0,1,0,0,1,1,0,1,1,1,0,0,0,1,0,0
                ,0,1,1,0,1,0,1,0,0,1,1,1,0,0,1,0,0
                ,0,1,0,1,1,1,1,1,0,1,0,1,0,1])
preamble=np.matlib.repmat([1,0],1,32)
size_tc=np.array([0,0,0,0,0,1,1,0])
CRC=[1,0,0,1,0,0,0,1,0,0,0,1,1,1,0,0]
data_undemodulated=mpQueue()
data_demodulated=mpQueue()
telemetry=mpQueue()
measoures=mpQueue()
packets_received=0
packets_proccessed=0
onTelemetry=Value('i',0)
BS_moduScheme=0
BS_codeScheme=1
BS_interleaver=0
SC_moduScheme=Value('i',0)
SC_codeScheme=Value('i',0)
SC_interleaver=Value('i',0)

boira_data={
    'SC_ID':0,
    'TM_TYPE':0,
    'OBC_APP_STATUS':0,
    'OBC_SYS_CHECK':0,
    'OBC_TIMESTAMP_D':0,
    'OBC_TIMESTAMP_MS':0,
    'OBC_TIME_REBOOT':0,
    'OBC_BOOTCOUNTER':0,
    'OBC_REBOOT_CAUSE':0,
    'OBC_SC_MODE':0,
    'OBC_LAST_MODE':0,
    'OBC_MODE_TIME':0,
    'OBC_MODE':0,
    'OBC_LAST_OB_TLE':0,
    'OBC_GPS_STATE':0,
    'OBC_GPS_TIME':0,
    'COM_TC_LIST':0,
    'COM_TC_COUNT':0,
    'COM_TM_COUNT':0,
    'COM_RSSI':0,
    'COM_LAST_ERR':0,
    'EPS_MODE':0,
    'EPS_BAT_SOC':0,
    'EPS_SP_CURRXP':0,
    'EPS_SP_CURRXM':0,
    'EPS_SP_CURRYP':0,
    'EPS_SP_CURRYM':0,
    'EPS_SP_CURRZP':0,
    'EPS_SP_VOLTXP':0,
    'EPS_SP_VOLTXM':0,
    'EPS_SP_VOLTYP':0,
    'EPS_SP_VOLTYM':0,
    'EPS_SP_VOLTZP':0,
    'EPS_PCDU_CURR':0,
    'EPS_PCDU_VOLT':0,
    'ADCS_MODE':0,
    'ADCS_IMU_OMEGA_X':0,
    'ADCS_IMU_OMEGA_Y':0,
    'ADCS_IMU_OMEGA_Z':0,
    'ADCS_IMU_MAG_X':0,
    'ADCS_IMU_MAG_Y':0,
    'ADCS_IMU_MAG_Z':0,
    'ADCS_Q_X':0,
    'ADCS_Q_Y':0,
    'ADCS_Q_Z':0,
    'ADCS_Q_W':0,
    'ADCS_X_ECEF':0,
    'ADCS_Y_ECEF':0,
    'ADCS_Z_ECEF':0,
    'THE_SP_TEMPXP':0,
    'THE_SP_TEMPXM':0,
    'THE_SP_TEMPYP':0,
    'THE_SP_TEMPYM':0,
    'THE_SP_TEMPZP':0,
    'THE_ADCS_TEMP':0,
    'THE_OBC_TEMP':0,
    'THE_RFBOARD_TEMP':0,
    'THE_PCDU_TEMP':0,
    'THE_HEATER_STATE':0,
    'THE_HEATER_TIME':0,
    'PAY_NUM':0,
    'PAY_TIME_LAST':0,
    'NUM_PACKETS':0,
    'PAY_MEAS_ID':0,
    'PAY_NB_TF':0,
    'PAY_MEAS_TIME':0,
    'MODU_SCHEME':0,
    'CODE_SCHEME':0,
    'INTERLEAVER':0
}

#Low Pass Filter 
b_filt,a_filt=signal.butter(5,12500/(fs/2),btype='low',analog=False)

#------|PLUTO CONFIG|------#
sdr = adi.Pluto('ip:192.168.2.1')
sdr.gain_control_mode_chan0 = 'manual'
sdr.rx_hardwaregain_chan0 = 70.0 # dB
sdr.rx_lo = int(fc_rx)
sdr.sample_rate = int(fs)
sdr.rx_rf_bandwidth = int(30e3)
sdr.rx_buffer_size = num_samps
sdr.tx_rf_bandwidth = int(fs)
sdr.tx_lo = int(fc)
sdr.tx_hardwaregain_chan0 = 0 # dB

#METHODS################################################################################
def bits_to_bytes(bit_list):
    try:
        if len(bit_list) % 8 != 0:
            raise ValueError("Bit list length must be a multiple of 8")

        byte_list = []
        for i in range(0, len(bit_list), 8):
            # Take 8 bits, convert to string, then to integer base 2
            byte_value = int("".join(map(str, bit_list[i : i + 8])), 2)
            byte_list.append(byte_value)
        return byte_list
    except Exception as e:
        print(f"Error converting bits to bytes: {e}")
        return None

def bytes_to_bits(byte_list):
    try:
        bit_list = []
        for byte_value in byte_list:
            # Convert int to 8-bit binary string, pad with zeros, then convert to list of ints
            bit_string = bin(byte_value)[2:].zfill(8)
            bit_list.extend([int(bit) for bit in bit_string])
        return bit_list
    except Exception as e:
        print(f"Error converting bytes to bits: {e}")
        return None

def intanddump(x, nSamp):
    # Integrate and dump function
    wid = x.shape[0]
    if wid == 1:
        x1 = x.flatten()
    else:
        x1 = x

    xRow, xCol = x1.shape
    x1 = x1.reshape(nSamp, xRow * xCol // nSamp).mean(axis=0)
    y1 = x1.reshape(xRow // nSamp, xCol)

    if wid == 1:
        return y1.T
    else:
        return y1

def fskdemod(y, M, freq_sep, nSamp, Fs, symbol_order='bin'):
    # --- Error checks ---
    y = np.atleast_2d(y)
    if not (M >= 2 and (M & (M - 1)) == 0):
        raise ValueError('M must be a power of 2 and >= 2')
    if freq_sep <= 0:
        raise ValueError('freq_sep must be positive')
    if not (nSamp > 1 and isinstance(nSamp, int)):
        raise ValueError('nSamp must be an integer greater than 1')
    if Fs <= 0:
        raise ValueError('Fs must be positive')

    maxFreq = ((M - 1) / 2) * freq_sep
    if maxFreq > Fs / 2:
        raise ValueError('Maximum frequency exceeds Fs/2 (Nyquist limit)')

    symbol_order = symbol_order.lower()
    if symbol_order not in ['bin', 'gray']:
        raise ValueError('symbol_order must be "bin" or "gray"')

    # --- Prepare the signal ---
    wid = y.shape[0]
    if wid == 1:
        y1 = y.flatten()[:, np.newaxis]
    else:
        y1 = y

    nRows, nChan = y1.shape
    z1 = np.zeros((nRows // nSamp, nChan), dtype=int)

    # --- Generate tones ---
    freqs = np.linspace(-(M-1)/2, (M-1)/2, M) * freq_sep
    t = np.arange(0, nSamp) / Fs
    phase = 2 * np.pi * np.outer(t, freqs)
    tones = np.exp(-1j * phase)  # Shape (nSamp, M)

    # --- Main loop ---
    for iChan in range(nChan):
        for iSym in range(nRows // nSamp):
            yTemp = y1[iSym*nSamp:(iSym+1)*nSamp, iChan]
            yTemp = np.tile(yTemp[:, np.newaxis], (1, M))
            yTemp = yTemp * tones
            yMag = np.abs(intanddump(yTemp, nSamp))
            maxIdx = np.argmax(yMag, axis=1)
            z1[iSym, iChan] = maxIdx[0]  # zero-based indexing

    # --- Restore output shape ---
    if wid == 1:
        z = z1.T
    else:
        z = z1

    # --- Gray decode if necessary ---
    if symbol_order == 'gray':
        z = gray2bin(z, M)

    return z

def gray2bin(z, M):
    # Gray decoding: reverse of Gray encoding
    gray_map = np.zeros(M, dtype=int)
    for k in range(M):
        gray_map[k] = k ^ (k >> 1)  # Gray encoding
    bin_map = np.zeros(M, dtype=int)
    for idx, val in enumerate(np.argsort(gray_map)):
        bin_map[val] = idx
    if z.ndim == 1:
        return bin_map[z]
    else:
        return np.vectorize(lambda x: bin_map[x])(z)

def frame_process(x):
    x=x.flatten()
    corr=signal.correlate(x[0:256], goldSeq,mode='full')
    lags=signal.correlation_lags(len(x),len(goldSeq),mode='full')
    inicio_trama=np.argmax(corr)-63
    inicio_data=inicio_trama+64
    demod_sync_word=x[inicio_trama:inicio_data]
    demod_data_withcrc=x[inicio_data:]
    packet_size=int(''.join(map(str,demod_data_withcrc[0:24])),2)
    #print("Packet_size="+str(packet_size))
    #packet_size=234
    demod_data=demod_data_withcrc[0:packet_size*8]
    demod_crc=demod_data_withcrc[packet_size*8:packet_size*8+16]
    return demod_sync_word, demod_data, demod_crc, lags, corr

def correlation_detect(onTelemetry_status, SC_codeScheme,SC_moduScheme,SC_interleaver):
    global packets_received

    while(1):
        #print(onTelemetry_status.value)
        samples_rx=sdr.rx()
        while(1):
            old_samples=samples_rx
            samples_rx=sdr.rx()
            samples_c=np.concatenate((old_samples,samples_rx))
            correlation=signal.correlate(((fskdemod(signal.filtfilt(b_filt,a_filt,samples_c),2,20000,sps,fs)).flatten()),goldSeq,mode='full')
            #print(np.max(correlation))
            if (np.max(correlation)>27):#idealmente 27-28 es que no hay errores
                break
        if(onTelemetry_status.value==0):
            samples2=sdr.rx()
            samples3=sdr.rx()
            samples4=sdr.rx()
            samples5=sdr.rx()
            samples6=sdr.rx()
            samples7=sdr.rx()
            samples8=sdr.rx()
            samples9=sdr.rx()
            samples10=sdr.rx()
            samples11=sdr.rx()
            samples12=sdr.rx()
            samples13=sdr.rx()
            samples14=sdr.rx()
            samples15=sdr.rx()
            samples16=sdr.rx()
            samples17=sdr.rx()
            samples18=sdr.rx()
            samples19=sdr.rx()
            samples20=sdr.rx()
            samples21=sdr.rx()
            samples22=sdr.rx()
            samples23=sdr.rx()
            samples24=sdr.rx()
            samples25=sdr.rx()
            samples26=sdr.rx()
            samples27=sdr.rx()
            samples28=sdr.rx()
            samples29=sdr.rx()
            samples30=sdr.rx()
            samples31=sdr.rx()
            samples32=sdr.rx()
            samples33=sdr.rx()
            samples34=sdr.rx()
            samples35=sdr.rx()
            samples36=sdr.rx()
            samples37=sdr.rx()
            samples38=sdr.rx()
            samples39=sdr.rx()
            samples40=sdr.rx()
            samples41=sdr.rx()
            samples42=sdr.rx()
            samples43=sdr.rx()#we need this amount of samples to recover the most large housekeeping
            samples44=sdr.rx()
            samples45=sdr.rx()
            samples=np.concatenate((samples_c,samples2,samples3,samples4,
                                    samples5,samples6,samples7,samples8,
                                    samples9,samples10,samples11,samples12,
                                    samples13,samples14,samples15,samples16,
                                    samples17,samples18,samples19,samples20,
                                    samples21,samples22,samples23,samples24,
                                    samples25,samples26,samples27,samples28,
                                    samples29,samples30,samples31,samples32,
                                    samples33,samples34,samples35,samples36,
                                    samples37,samples38,samples39,samples40,
                                    samples41,samples42,samples43,samples44,samples45))
        elif(onTelemetry_status.value==1):
            if(SC_codeScheme.value==1):
                num_additional_samples=110
            elif(SC_codeScheme.value==2):
                num_additional_samples=64
            elif(SC_codeScheme.value==3):
                num_additional_samples=126
            else:
                num_additional_samples=56
            sample_list = [samples_c]
            for _ in range(num_additional_samples):
                sample_list.append(sdr.rx())
            samples = np.concatenate(sample_list)
        data_undemodulated.put(samples)
        packets_received+=1
        #print("Packets detected:" + str(packets_received))
    return 1

def receive(onTelemetry, SC_codeScheme,SC_moduScheme,SC_interleaver):
    global packets_proccessed
    while(1):
        while(data_undemodulated.empty()):
            pass
        samples_detected=data_undemodulated.get()
        samples_detected=signal.filtfilt(b_filt,a_filt,samples_detected)
        #Take only the info
        #------|DEMODULATION|------#
        demodulated=(fskdemod(samples_detected, 2, 20000, sps, fs))#fsk demodulation
        d_sync_word, d_data, d_crc, lags, corr=frame_process(demodulated)
        #print("packet received!")
        #print(d_data)
        data_recover(d_data, onTelemetry,SC_codeScheme,SC_moduScheme,SC_interleaver)
        data_demodulated.put(d_data)
    return 1

def UI_init():
    StellarSat_1_UI.UI(data_demodulated, telemetry)

def data_recover(data_recovered, onTelemetry_status,SC_codeScheme,SC_moduScheme,SC_interleaver):
    global boira_data
    try:
        if(onTelemetry_status.value==0):
            header=data_recovered[0:8*15]
            beacon_size=header[0:8*3]
            modu_scheme=header[8*4:8*5]
            codi_scheme=header[8*5:8*6]
            SC_codeScheme.value=int(''.join(map(str,codi_scheme[0:8])),2)
            SC_moduScheme.value=int(''.join(map(str,modu_scheme[0:8])),2)
            #print("Code Scheme: "+str(int(''.join(map(str,codi_scheme[0:8])),2)))
            TM_TC=header[8*3:8*3+4]
            interleaver=header[8*3+4:8*4]
            boira_data['MODU_SCHEME']=modu_scheme
            boira_data['CODE_SCHEME']=codi_scheme
            boira_data['INTERLEAVER']=interleaver
            SC_interleaver.value=int(''.join(map(str,interleaver[0:4])),2)
            header_SC_ID=header[8*8:8*10]
            if(int(''.join(map(str,header_SC_ID[0:16])),2)!=53456):
                return 0
            if(int(''.join(map(str,TM_TC[0:4])),2)!=1):
                return 0
            version=header[8*10+4:8*11]
            header_crc=header[8*13:8*15]
            data_beacon=data_recovered[8*15:8*int(''.join(map(str,beacon_size[0:24])),2)]
            if(str(int(''.join(map(str,codi_scheme[0:8])),2))=="1"):
                data_beacon=conv_decoder(data_beacon)
                if(str(int(''.join(map(str,interleaver[0:4])),2))=="1"):
                    for i in range(0,len(data_beacon),64):
                        chunk_bytes=bits_to_bytes(data_beacon[i:i+64])
                        deint_bytes=block_deinterleave(chunk_bytes,2,4)
                        if deint_bytes is None:
                            return 
                        data_beacon[i:i+64]=bytes_to_bits(deint_bytes)
            elif(str(int(''.join(map(str,codi_scheme[0:8])),2))=="2"):
                data_beacon=rs_decoder(data_beacon)
                if(type(data_beacon)==type(None)):
                    return 0
                data_beacon=data_beacon[:8*200]
                if(str(int(''.join(map(str,interleaver[0:4])),2))=="1"):
                    for i in range(0,len(data_beacon),64):
                        chunk_bytes=bits_to_bytes(data_beacon[i:i+64])
                        deint_bytes=block_deinterleave(chunk_bytes,2,4)
                        if deint_bytes is None:
                            return 
                        data_beacon[i:i+64]=bytes_to_bits(deint_bytes)
            elif(str(int(''.join(map(str,codi_scheme[0:8])),2))=="3"):
                data_beacon=conv_decoder(data_beacon)
                if(str(int(''.join(map(str,interleaver[0:4])),2))=="1"): 
                    for i in range(0,len(data_beacon)-8,64): 
                        chunk_bytes=bits_to_bytes(data_beacon[i:i+64]) 
                        deint_bytes=block_deinterleave(chunk_bytes,2,4) 
                        if deint_bytes is None: 
                            break 
                        data_beacon[i:i+64]=bytes_to_bits(deint_bytes)
                data_beacon=data_beacon[:len(data_beacon)]
                #print(len(data_beacon))
                data_beacon=rs_decoder(data_beacon[:])
                if(type(data_beacon)==type(None)):
                    return 0
            elif(str(int(''.join(map(str,codi_scheme[0:8])),2))=="0"):
                if(str(int(''.join(map(str,interleaver[0:4])),2))=="1"):
                    for i in range(0,len(data_beacon),64):
                        chunk_bytes=bits_to_bytes(data_beacon[i:i+64])
                        deint_bytes=block_deinterleave(chunk_bytes,2,4)
                        if deint_bytes is None:
                            return 
                        data_beacon[i:i+64]=bytes_to_bits(deint_bytes)


            else:
                return 0
            #print(bits_to_bytes(data_beacon))
            boira_data['SC_ID']=data_beacon[0:8*2]
            boira_data['TM_TYPE']=data_beacon[8*2:8*3]
            boira_data['OBC_APP_STATUS']=data_beacon[8*3:8*5]
            boira_data['OBC_SYS_CHECK']=data_beacon[8*5:8*7]
            boira_data['OBC_TIMESTAMP_D']=data_beacon[8*7:8*9]
            boira_data['OBC_TIMESTAMP_MS']=data_beacon[8*9:8*13]
            boira_data['OBC_TIME_REBOOT']=data_beacon[8*13:8*17]
            boira_data['OBC_BOOTCOUNTER']=data_beacon[8*17:8*21]
            boira_data['OBC_REBOOT_CAUSE']=data_beacon[8*21:8*23]
            boira_data['OBC_SC_MODE']=data_beacon[8*23:8*24]
            boira_data['OBC_LAST_MODE']=data_beacon[8*24:8*25]
            boira_data['OBC_MODE_TIME']=data_beacon[8*25:8*29]
            boira_data['OBC_MODE']=data_beacon[8*29:8*30]
            boira_data['OBC_LAST_OB_TLE']=data_beacon[8*30:8*40]
            boira_data['OBC_GPS_STATE']=data_beacon[8*40:8*41]
            boira_data['OBC_GPS_TIME']=data_beacon[8*41:8*44]
            boira_data['COM_TC_LIST']=data_beacon[8*44:8*94]
            boira_data['COM_TC_COUNT']=data_beacon[8*94:8*98]
            boira_data['COM_TM_COUNT']=data_beacon[8*98:8*102]
            boira_data['COM_RSSI']=data_beacon[8*102:8*104]
            boira_data['COM_LAST_ERR']=data_beacon[8*104:8*106]
            boira_data['EPS_MODE']=data_beacon[8*106:8*107]
            boira_data['EPS_BAT_SOC']=data_beacon[8*107:8*108]
            boira_data['EPS_SP_CURRXP']=data_beacon[8*108:8*110]
            boira_data['EPS_SP_CURRXM']=data_beacon[8*110:8*112]
            boira_data['EPS_SP_CURRYP']=data_beacon[8*112:8*114]
            boira_data['EPS_SP_CURRYM']=data_beacon[8*114:8*116]
            boira_data['EPS_SP_CURRZP']=data_beacon[8*116:8*118]
            boira_data['EPS_SP_VOLTXP']=data_beacon[8*118:8*120]
            boira_data['EPS_SP_VOLTXM']=data_beacon[8*120:8*122]
            boira_data['EPS_SP_VOLTYP']=data_beacon[8*122:8*124]
            boira_data['EPS_SP_VOLTYM']=data_beacon[8*124:8*126]
            boira_data['EPS_SP_VOLTZP']=data_beacon[8*126:8*128]
            boira_data['EPS_PCDU_CURR']=data_beacon[8*128:8*130]
            boira_data['EPS_PCDU_VOLT']=data_beacon[8*130:8*132]
            boira_data['ADCS_MODE']=data_beacon[8*132:8*133]
            boira_data['ADCS_IMU_OMEGA_X']=data_beacon[8*133:8*137]
            boira_data['ADCS_IMU_OMEGA_Y']=data_beacon[8*137:8*141]
            boira_data['ADCS_IMU_OMEGA_Z']=data_beacon[8*141:8*145]
            boira_data['ADCS_IMU_MAG_X']=data_beacon[8*145:8*149]
            boira_data['ADCS_IMU_MAG_Y']=data_beacon[8*149:8*153]
            boira_data['ADCS_IMU_MAG_Z']=data_beacon[8*153:8*157]
            boira_data['ADCS_Q_X']=data_beacon[8*157:8*161]
            boira_data['ADCS_Q_Y']=data_beacon[8*161:8*165]
            boira_data['ADCS_Q_Z']=data_beacon[8*165:8*169]
            boira_data['ADCS_Q_W']=data_beacon[8*169:8*173]
            boira_data['ADCS_X_ECEF']=data_beacon[8*173:8*174]
            boira_data['ADCS_Y_ECEF']=data_beacon[8*174:8*175]
            boira_data['ADCS_Z_ECEF']=data_beacon[8*175:8*176]
            boira_data['THE_SP_TEMPXP']=data_beacon[8*176:8*178]
            boira_data['THE_SP_TEMPXM']=data_beacon[8*178:8*180]
            boira_data['THE_SP_TEMPYP']=data_beacon[8*180:8*182]
            boira_data['THE_SP_TEMPYM']=data_beacon[8*182:8*184]
            boira_data['THE_SP_TEMPZP']=data_beacon[8*184:8*186]
            boira_data['THE_ADCS_TEMP']=data_beacon[8*186:8*188]
            boira_data['THE_OBC_TEMP']=data_beacon[8*188:8*190]
            boira_data['THE_RFBOARD_TEMP']=data_beacon[8*190:8*192]
            boira_data['THE_PCDU_TEMP']=data_beacon[8*192:8*194]
            boira_data['THE_HEATER_STATE']=data_beacon[8*194:8*195]
            boira_data['THE_HEATER_TIME']=data_beacon[8*195:8*197]
            boira_data['PAY_NUM']=data_beacon[8*197:8*198]
            boira_data['PAY_TIME_LAST']=data_beacon[8*198:8*200]
            telemetry.put(boira_data)
        elif(onTelemetry_status.value==1):
            #print("ON Telemetry!!!!")
            header=data_recovered[0:8*15]
            telemetry_size=header[0:8*3]
            modu_scheme=header[8*4:8*5]
            codi_scheme=header[8*5:8*6]
            SC_codeScheme.value=int(''.join(map(str,codi_scheme[0:24])),2)
            SC_moduScheme.value=int(''.join(map(str,modu_scheme[0:24])),2)
            #print("Code Scheme: "+str(int(''.join(map(str,codi_scheme[0:8])),2)))
            interleaver=header[8*3:8*4]
            SC_interleaver.value=int(''.join(map(str,interleaver[0:24])),2)
            header_SC_ID=header[8*8:8*10]
            if(int(''.join(map(str,header_SC_ID[0:24])),2)!=53456):
                return 0
            version=header[8*10:8*11]
            header_crc=header[8*13:8*15]
            #print(int(''.join(map(str,telemetry_size)),2))
            #print(len(data_recovered)/8)
            data_telemetry=data_recovered[8*15:8*int(''.join(map(str,telemetry_size)),2)]
            if(str(int(''.join(map(str,codi_scheme[0:8])),2))=="1"):
                data_telemetry=conv_decoder(data_telemetry)
                if(str(int(''.join(map(str,interleaver[0:8])),2))=="1"):
                    for i in range(0,len(data_telemetry),64):
                        chunk_bytes=bits_to_bytes(data_telemetry[i:i+64])
                        deint_bytes=block_deinterleave(chunk_bytes,2,4)
                        if deint_bytes is None:
                            return 0
                        data_telemetry[i:i+64]=bytes_to_bits(deint_bytes)
            elif(str(int(''.join(map(str,codi_scheme[0:8])),2))=="2"):
                full_telemetry_rs=np.array([], dtype=int)
                for i in range(3):
                    data_telemetry_rs=rs_decoder(data_telemetry[i*255*8:(i+1)*255*8])
                    if(type(data_telemetry_rs)==type(None)):
                        return 0
                    full_telemetry_rs=np.concatenate((full_telemetry_rs,data_telemetry_rs))
                data_telemetry=full_telemetry_rs
                if(type(data_telemetry)==type(None)):
                    return 0
                if(str(int(''.join(map(str,interleaver[0:8])),2))=="1"):
                    for i in range(0,len(data_telemetry),64):
                        chunk_bytes=bits_to_bytes(data_telemetry[i:i+64])
                        deint_bytes=block_deinterleave(chunk_bytes,2,4)
                        if deint_bytes is None:
                            return 0
                        data_telemetry[i:i+64]=bytes_to_bits(deint_bytes)
            elif(str(int(''.join(map(str,codi_scheme[0:8])),2))=="3"):
                data_telemetry=conv_decoder(data_telemetry)
                if(str(int(''.join(map(str,interleaver[0:8])),2))=="1"):
                    for i in range(0,len(data_telemetry),64):
                        chunk_bytes=bits_to_bytes(data_telemetry[i:i+64])
                        deint_bytes=block_deinterleave(chunk_bytes,2,4)
                        if deint_bytes is None:
                            return 0
                        data_telemetry[i:i+64]=bytes_to_bits(deint_bytes)
                data_telemetry=data_telemetry[:len(data_telemetry)-(8*3)]
                #print(len(data_telemetry))
                full_telemetry_rs=np.array([], dtype=int)
                for i in range(3):
                    data_telemetry_rs=rs_decoder(data_telemetry[i*255*8:(i+1)*255*8])
                    full_telemetry_rs=np.concatenate((full_telemetry_rs,data_telemetry_rs))
                data_telemetry=full_telemetry_rs
                if(type(data_telemetry)==type(None)):
                    return 0
            elif(str(int(''.join(map(str,codi_scheme[0:8])),2))=="0"):
                if(str(int(''.join(map(str,interleaver[0:8])),2))=="1"):
                    for i in range(0,len(data_telemetry),64):
                        chunk_bytes=bits_to_bytes(data_telemetry[i:i+64])
                        deint_bytes=block_deinterleave(chunk_bytes,2,4)
                        if deint_bytes is None:
                            return 0
                        data_telemetry[i:i+64]=bytes_to_bits(deint_bytes)
            boira_data['SC_ID']=data_telemetry[0:8*2]
            boira_data['TM_TYPE']=data_telemetry[8*2:8*3]
            boira_data['OBC_TIMESTAMP_D']=data_telemetry[8*3:8*5]
            boira_data['OBC_TIMESTAMP_MS']=data_telemetry[8*5:8*9]
            boira_data['ADCS_IMU_OMEGA_X']=data_telemetry[8*9:8*13]
            boira_data['ADCS_IMU_OMEGA_Y']=data_telemetry[8*13:8*17]
            boira_data['ADCS_IMU_OMEGA_Z']=data_telemetry[8*17:8*21]
            boira_data['ADCS_IMU_MAG_X']=data_telemetry[8*21:8*25]
            boira_data['ADCS_IMU_MAG_Y']=data_telemetry[8*25:8*29]
            boira_data['ADCS_IMU_MAG_Z']=data_telemetry[8*29:8*33]
            boira_data['ADCS_Q_X']=data_telemetry[8*33:8*37]
            boira_data['ADCS_Q_Y']=data_telemetry[8*37:8*41]
            boira_data['ADCS_Q_Z']=data_telemetry[8*41:8*45]
            boira_data['ADCS_Q_W']=data_telemetry[8*45:8*49]
            boira_data['ADCS_X_ECEF']=data_telemetry[8*49:8*50]
            boira_data['ADCS_Y_ECEF']=data_telemetry[8*50:8*51]
            boira_data['ADCS_Z_ECEF']=data_telemetry[8*51:8*52]
            boira_data['PAY_MEAS_ID']=data_telemetry[8*52:8*54]
            boira_data['PAY_NB_TF']=data_telemetry[8*54:8*55]
            boira_data['PAY_MEAS_TIME']=data_telemetry[8*55:8*57]
            if(str(int(''.join(map(str,boira_data['PAY_NB_TF'].astype(int))),2))!="25"):
                return
            boira_measoures=np.array(data_telemetry[8*57:])
            measoures.put(((int(''.join(map(str,boira_data['PAY_MEAS_ID'])),2),boira_measoures)))
            print(str(int(''.join(map(str,boira_data['PAY_MEAS_ID'].astype(int))),2)))
    except Exception as e:
        print("Error: "+str(e)+". Reload the program")
        return

def create_TC_header(hdr,size):
    global BS_codeScheme
    global BS_interleaver
    global BS_moduScheme
    hdr[0:8]=[int(i)for i in bin(size+13)[2:].zfill(8)]
    if (BS_interleaver==1):
        hdr[8:8*2]=[0,0,1,0,0,0,0,1] #type 2 and interleaver
    else:
        hdr[8:8*2]=[0,0,1,0,0,0,0,0]
    hdr[8*2:8*3]=[int(i)for i in bin(BS_moduScheme)[2:].zfill(8)]
    hdr[8*3:8*4]=[int(i)for i in bin(BS_codeScheme)[2:].zfill(8)]
    hdr[8*4:8*6]=[1,1,0,1,0,0,0,0,1,1,0,1,0,0,0,0]
    hdr[8*6:8*8]=[1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
    hdr[8*8:8*9]=[0,0,1,0,0,0,0,1] #header type 2 and UC3Space version
    hdr[8*9:8*11]=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    hdr[8*11:]=[0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1]#~CALCULAR CRC
    return hdr

def TX_TC(tx_TC,tc_size):
    tx_TC=np.array(tx_TC)
    TC_expanded=np.repeat(tx_TC,sps)
    N=len(TC_expanded) # Samples to tx--> 500spls/bit *(64 preamble +64 sync_word + 8 + 6*8 Payload + 2*8 CRC)
    t=np.arange(0,N)/fs
    f=(2*TC_expanded-1)*devf
    Xfsk=np.exp(1j*2*math.pi*f*t)
    Xfsk*=2**14
    for i in range(1):
        sdr.tx(Xfsk)
    #receive()
    return 1

def conv_encoder(data_to_encode):
    G = ('111', '101')
    cc1 = fec_conv(G, 9) #Use the same as the spacecraft
    state = '00'
    data_to_encode=np.concatenate((data_to_encode,[0,0,0,0,0,0,0,0]))
    data_encoded_cnv, state = cc1.conv_encoder(data_to_encode, state)
    output=np.array(data_encoded_cnv).astype(int)
    return output

def conv_decoder(data_to_decode):
    G = ('111', '101') 
    cc1 = fec_conv(G, 9) #Use the same as the spacecraft
    state = '00'
    data_decoded_cnv = (cc1.viterbi_decoder(data_to_decode.astype(int), 'hard')).astype(int)
    return data_decoded_cnv

def rs_encoder(data_to_encode):
    rsc=rs.RSCodec(32,prim=0x187,fcr=1)
    padding= 8*223-int(len(data_to_encode))
    msg_padding=np.zeros(padding,dtype=int)
    data_to_encode=np.concatenate((data_to_encode,msg_padding))
    msg_bytes = bits_to_bytes(data_to_encode)
    encoded_bytes = rsc.encode(msg_bytes)
    data_encoded_rs = bytes_to_bits(encoded_bytes)
    return data_encoded_rs

def rs_decoder(data_to_decode):
    rsc=rs.RSCodec(32,prim=0x187,fcr=1)
    try:
        data_to_decode_B=bits_to_bytes(data_to_decode)
        if data_to_decode_B is None:
            print("Error al decodificar rs.")
            return data_to_decode[0:-32*8]
    except:
        print("No es multiplo de 8")
        return None
    try:
        decoded_bytearray, _, _ = rsc.decode(data_to_decode_B)
    except Exception as e:
        print("Demasiados errores en rs."+str(e))    
        return data_to_decode[0:-32*8]
    decoded_bytes = list(decoded_bytearray)
    data_decoded_rs = bytes_to_bits(decoded_bytes)
    return data_decoded_rs

def command_help():
    print("Lista de comandos:")
    print()
    print("beacon")
    print("    PAYLOAD")
    print("pay-tc-001: TC to start PAY Experiment(spectrometer)(Configuration 1)")
    print("pay-tc-002: TC to start PAY Experiment(spectrometer)(Configuration 2)")
    print("pay-tc-003: TC to start PAY Experiment(spectrometer)(Configuration 3)")
    print("pay-tc-004: TC to downlink the complete PAY Experiment(spectrometer)(Configuration 1)")
    print("pay-tc-005: TC to downlink the complete PAY Experiment(spectrometer)(Configuration 2)")
    print("pay-tc-006: TC to downlink the complete PAY Experiment(spectrometer)(Configuration 3)")
    print("pay-tc-007: TC to download PAY Experiment(spectrometer)(Configuration 1) from package N to M (will be asked after to get N and M)")
    print("pay-tc-008: TC to download PAY Experiment(spectrometer)(Configuration 2) from package N to M (will be asked after to get N and M)")
    print("pay-tc-009: TC to download PAY Experiment(spectrometer)(Configuration 3) from package N to M (will be asked after to get N and M)")
    print()
    print("    TTC")
    print("ttc-tc-001: TC for RF-Cessation")
    print("ttc-tc-002: TC for RF-Activation")
    print("ttc-tc-003: Handshake TC for first contact for a SC pass over the GS")
    print("ttc-tc-004: Goodbye TC for last contact for a SC pass over the GS")
    print()
    print("    OBC")
    print("obc-tc-001: TC to change from Operation to LEOP Mode")
    print("obc-tc-002: TC to change from LEOP to Operation Mode")
    print("obc-tc-003: TC to change from Operation to Safe Mode")
    print("obc-tc-004: TC to change from Safe to Operation Mode")
    print("obc-tc-005: TC to get the SC Events")
    print("obc-tc-006: TC to perform the EPS Reboot")
    print("obc-tc-007: TC to perform the ADCS Reboot")
    print("obc-tc-008: TC to perform the OBC-TTC Reboot")
    print("obc-tc-009: TC to perform the PAY Reboot")
    print("obc-tc-010: TC to return the OBSW Baseline")
    print("obc-tc-011: TC to activate the EOL-Skyfall Procedure")
    print("obc-tc-012: TC to abort the EOL-Skyfall Procedure")
    print("obc-tc-013: TC to abort Solution/Experiment(ADCS or PAY)")
    print("obc-tc-014: TC to abort Solution/Experiment queue(ADCS or PAY)")
    print()
    print("    ADCS")
    print("adcs-tc-001: TC to upload the TLE from GS to the SC")
    print("adcs-tc-002: TC to return to ADCS Baseline")
    print("adcs-tc-003: TC to start the ADCS Solution 1")
    print("adcs-tc-004: TC to start the ADCS Solution 2")
    print("adcs-tc-005: TC to start the ADCS Solution 3")
    print("adcs-tc-006: TC to download TBD hours of ADCS Solution 1")
    print("adcs-tc-007: TC to download TBD hours of ADCS Solution 2")
    print("adcs-tc-008: TC to download TBD hours of ADCS Solution 3")
    print("adcs-tc-009: TC to download ADCS Solution 1 from package N to M (will be asked after to get N and M)")
    print("adcs-tc-010: TC to download ADCS Solution 2 from package N to M (will be asked after to get N and M)")
    print("adcs-tc-011: TC to download ADCS Solution 3 from package N to M (will be asked after to get N and M)")
    print()
    print("    TTC-CONFIG")
    print("set code X: Change SC codification scheme")
    print("          X=0: No codification")
    print("          X=1: Convolutional 1/2")
    print("          X=2: Reed Solomon")
    print("          X=3: Convolutional + Reed Solomon")
    print("set modulation X")
    print("set interleaver X: Change SC interleaver settings")
    print("          X=0: No interleaver")
    print("          X=1: Interleaver")
    print()
    print("    BS-CONFIG")
    print("bs set code X: Change BS codification scheme")
    print("          X=0: No codification")
    print("          X=1: Convolutional 1/2")
    print("          X=2: Reed Solomon")
    print("          X=3: Convolutional + Reed Solomon")
    print("bs set modulation X")
    print("bs set interleaver X: Change BS interleaver settings")
    print("          X=0: No interleaver")
    print("          X=1: Interleaver")
    print()
    print("    GENERAL")
    print("exit/quit: Close program")
    print("help: Display the help menu")
    print()
    print()

def block_interleave(data, rows, cols):
    matrix = np.reshape(data, (rows, cols))
    interleaved = matrix.T.flatten()
    return interleaved

def block_deinterleave(data, rows, cols):
    try:
        matrix = np.reshape(data, (cols, rows)).T
        return matrix.flatten()
    except:
        return None

def telemetry_recover(onTelemetry):
    if os.path.exists("TM.pkl"):
        with open("TM.pkl","rb") as f:
            tm_received=pickle.load(f)
    else:
        tm_received={}
    complete_data=np.array([], dtype=int)
    esperados=set(range(0,25))
    start_time=time.time()
    timeout=150

    for i in sorted(tm_received.keys()):
        complete_data=np.concatenate((complete_data,tm_received[i]))


    while True:
        tiempo_restante=start_time + timeout - time.time()
        if(tiempo_restante<=0):
            onTelemetry.value=0
            break
        try:
            id,data=measoures.get(timeout=tiempo_restante)
            if id not in tm_received:
                tm_received[id]=data
                complete_data=np.concatenate((complete_data,data))
                if len(tm_received)==25:
                    break
            else:
                print("id duplicada")
        except:
            break
    faltantes=esperados-set(tm_received.keys())
        
    if faltantes:
        print(f"Faltan paquetes:{faltantes}")
        onTelemetry.value=0
        with open("TM.pkl","wb") as f:
            pickle.dump(tm_received,f)
        return
    else:
        print("TM succesfull")
        onTelemetry.value=0
        if(os.path.exists("TM.pkl")):
            os.remove("TM.pkl")
        with open("telemetria"+str(time.time())+".bin","wb") as f:
            f.write(complete_data)
        return

def codeTC(tx_TC):
    global BS_codeScheme
    global BS_interleaver
    global BS_moduScheme
    if(BS_codeScheme==1):
        if(BS_interleaver==1):
            tx_TC=block_interleave(tx_TC,2,4)
        tx_TC=conv_encoder(tx_TC)
    elif(BS_codeScheme==2):
        if(BS_interleaver==1):
            tx_TC=block_interleave(tx_TC,2,4)
        tx_TC=rs_encoder(tx_TC)
    elif(BS_codeScheme==3):
        tx_TC=rs_encoder(tx_TC)
        if(BS_interleaver==1):
            tx_TC=block_interleave(tx_TC,2,4)
        tx_TC=conv_encoder(tx_TC)
    else:
        pass
    #print(len(tx_TC)/8)
    return tx_TC
########################################################################################

#PROCESS################################################################################
print("Loading...")
time.sleep(5)
print("Ready!")
proceso_rx=Process(target=correlation_detect, args=(onTelemetry,SC_codeScheme,SC_interleaver,SC_moduScheme,))
proceso_rx.start()
proceso_demod=Process(target=receive, args=(onTelemetry,SC_codeScheme,SC_interleaver,SC_moduScheme,))
proceso_demod.start()
proceso_UI=Process(target=UI_init)
proceso_UI.start()

########################################################################################

#MAIN###################################################################################
#------|LOOP|------#
while(1):
    try:
        TC=[]
        TC_HEADER=[0,0,0,0,0,0,0,0,0,0,0,0,0]
        TC_PACKET=[]
        command=input("Introduzca comando: \n")
        if(command=="pay-tc-001"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="pay-tc-002"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="pay-tc-003"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="pay-tc-004"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
            onTelemetry.value=1
            proceso_telemetría=Process(target=telemetry_recover,args=(onTelemetry,)).start()
        elif(command=="pay-tc-005"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
            onTelemetry.value=1
            proceso_telemetría=Process(target=telemetry_recover,args=(onTelemetry,)).start()
        elif(command=="pay-tc-006"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
            onTelemetry.value=1
            proceso_telemetría=Process(target=telemetry_recover,args=(onTelemetry,)).start()
        elif(command=="pay-tc-007"):
            scalar_n=input("Valor N: \n")
            scalar_m=input("Valor M: \n")
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0]
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_n))[2:].zfill(8)]))
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_m))[2:].zfill(8)]))
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
            onTelemetry.value=1
            proceso_telemetría=Process(target=telemetry_recover,args=(onTelemetry,)).start()
        elif(command=="pay-tc-008"):
            scalar_n=input("Valor N: \n")
            scalar_m=input("Valor M: \n")
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_n))[2:].zfill(8)]))
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_m))[2:].zfill(8)]))
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
            onTelemetry.value=1
            proceso_telemetría=Process(target=telemetry_recover,args=(onTelemetry,)).start()
        elif(command=="pay-tc-009"):
            scalar_n=input("Valor N: \n")
            scalar_m=input("Valor M: \n")
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_n))[2:].zfill(8)]))
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_m))[2:].zfill(8)]))
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
            onTelemetry.value=1
            proceso_telemetría=Process(target=telemetry_recover,args=(onTelemetry,)).start()
        elif(command=="ttc-tc-001"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="ttc-tc-002"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="ttc-tc-003"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="ttc-tc-004"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-001"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-002"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-003"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-004"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-005"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-006"):
            create_TC_header(TC_HEADER,4)
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0]
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,360)
        elif(command=="obc-tc-007"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-008"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-009"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-010"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-011"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-012"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-013"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="obc-tc-014"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="adcs-tc-001"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="adcs-tc-002"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="adcs-tc-003"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="adcs-tc-004"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="adcs-tc-005"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="adcs-tc-006"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="adcs-tc-007"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="adcs-tc-008"):
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="adcs-tc-009"):
            scalar_n=input("Valor N: \n")
            scalar_m=input("Valor M: \n")
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0]
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_n))[2:].zfill(8)]))
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_m))[2:].zfill(8)]))
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="adcs-tc-010"):
            scalar_n=input("Valor N: \n")
            scalar_m=input("Valor M: \n")
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0]
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_n))[2:].zfill(8)]))
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_m))[2:].zfill(8)]))
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command=="adcs-tc-011"):
            scalar_n=input("Valor N: \n")
            scalar_m=input("Valor M: \n")
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0]
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_n))[2:].zfill(8)]))
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_m))[2:].zfill(8)]))
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command[:8]=="set code"):
            scalar_code=int(command[9])
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_code))[2:].zfill(8)]))
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command[:15]=="set interleaver"):
            scalar_inter=int(command[16])
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0]
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_inter))[2:].zfill(8)]))
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command[:14]=="set modulation"):
            scalar_modul=int(command[15])
            TC=[0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0]
            TC=np.concatenate((TC,[int(i)for i in bin(int(scalar_modul))[2:].zfill(8)]))
            TC=codeTC(TC)
            create_TC_header(TC_HEADER,int(len(TC)/8))
            TC_PACKET=np.concatenate((preamble.flatten(),goldSeq,TC_HEADER,TC,CRC))
            TX_TC(TC_PACKET,int(len(TC_PACKET)))
        elif(command[:11]=="bs set code"):
            BS_codeScheme=int(command[12])
        elif(command[:18]=="bs set interleaver"):
            BS_interleaver=int(command[19])
        elif(command[:17]=="bs set modulation"):
            BS_moduScheme=int(command[18])
        elif(command=="help" or command=="HELP"):
            command_help()
        elif(command=="quit" or command=="exit"):
            print("Closing SDR connection.")
            del sdr
            proceso_demod.terminate()
            proceso_rx.terminate()
            proceso_UI.terminate()
            data_demodulated.close()
            data_undemodulated.close()
            exit()
        elif(command=="clear"):
            os.system("clear")
        else:
            print("Comando no reconocido")
    except Exception as e:
        print(f"Error during update: {e}")
        proceso_demod.terminate()
        proceso_rx.terminate()
        proceso_UI.terminate()
        data_demodulated.close()
        data_undemodulated.close()
        del sdr
        exit()
    except KeyboardInterrupt:
        print("Closing SDR connection.")
        del sdr
        proceso_demod.terminate()
        proceso_rx.terminate()
        proceso_UI.terminate()
        data_demodulated.close()
        data_undemodulated.close()
        exit()
        

##################################################

