# model setting
AI_MODEL_PATH = ""

# feature setting
FEATURE_COLUMNS = [
    'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'ABER_ZG_5_15', 'ABER_SG_5_15', 'ABER_XG_5_15', 'ABER_ATR_5_15', 
    'ACCBL_20', 'ACCBM_20', 'ACCBU_20', 'AD', 'ADOSC_3_10', 'ADX_14', 'DMP_14', 'DMN_14', 'ALMA_10_6.0_0.85', 'AMATe_LR_8_21_2', 
    'AMATe_SR_8_21_2', 'AO_5_34', 'OBV', 'OBV_min_2', 'OBV_max_2', 'OBVe_4', 'OBVe_12', 'AOBV_LR_2', 'AOBV_SR_2', 'APO_12_26', 
    'AROOND_14', 'AROONU_14', 'AROONOSC_14', 'ATRr_14', 'BBL_5_2.0', 'BBM_5_2.0', 'BBU_5_2.0', 'BBB_5_2.0', 'BBP_5_2.0', 
    'BIAS_SMA_26', 'BOP', 'AR_26', 'BR_26', 'CCI_14_0.015', 'CDL_2CROWS', 'CDL_3BLACKCROWS', 'CDL_3INSIDE', 'CDL_3LINESTRIKE', 
    'CDL_3OUTSIDE', 'CDL_3STARSINSOUTH', 'CDL_3WHITESOLDIERS', 'CDL_ABANDONEDBABY', 'CDL_ADVANCEBLOCK', 'CDL_BELTHOLD', 'CDL_BREAKAWAY', 
    'CDL_CLOSINGMARUBOZU', 'CDL_CONCEALBABYSWALL', 'CDL_COUNTERATTACK', 'CDL_DARKCLOUDCOVER', 'CDL_DOJI_10_0.1', 'CDL_DOJISTAR', 
    'CDL_DRAGONFLYDOJI', 'CDL_ENGULFING', 'CDL_EVENINGDOJISTAR', 'CDL_EVENINGSTAR', 'CDL_GAPSIDESIDEWHITE', 'CDL_GRAVESTONEDOJI', 
    'CDL_HAMMER', 'CDL_HANGINGMAN', 'CDL_HARAMI', 'CDL_HARAMICROSS', 'CDL_HIGHWAVE', 'CDL_HIKKAKE', 'CDL_HIKKAKEMOD', 
    'CDL_HOMINGPIGEON', 'CDL_IDENTICAL3CROWS', 'CDL_INNECK', 'CDL_INSIDE', 'CDL_INVERTEDHAMMER', 'CDL_KICKING', 
    'CDL_KICKINGBYLENGTH', 'CDL_LADDERBOTTOM', 'CDL_LONGLEGGEDDOJI', 'CDL_LONGLINE', 'CDL_MARUBOZU', 'CDL_MATCHINGLOW', 
    'CDL_MATHOLD', 'CDL_MORNINGDOJISTAR', 'CDL_MORNINGSTAR', 'CDL_ONNECK', 'CDL_PIERCING', 'CDL_RICKSHAWMAN', 
    'CDL_RISEFALL3METHODS', 'CDL_SEPARATINGLINES', 'CDL_SHOOTINGSTAR', 'CDL_SHORTLINE', 'CDL_SPINNINGTOP', 'CDL_STALLEDPATTERN', 
    'CDL_STICKSANDWICH', 'CDL_TAKURI', 'CDL_TASUKIGAP', 'CDL_THRUSTING', 'CDL_TRISTAR', 'CDL_UNIQUE3RIVER', 'CDL_UPSIDEGAP2CROWS', 
    'CDL_XSIDEGAP3METHODS', 'open_Z_30_1', 'high_Z_30_1', 'low_Z_30_1', 'close_Z_30_1', 'CFO_9', 'CG_10', 'CHOP_14_1_100', 
    'CKSPl_10_3_20', 'CKSPs_10_3_20', 'CMF_20', 'CMO_14', 'COPC_11_14_10', 'CTI_12', 'LDECAY_5', 'DEC_1', 'DEMA_10', 'DCL_20_20', 
    'DCM_20_20', 'DCU_20_20', 'DPO_20', 'EBSW_40_10', 'EFI_13', 'EMA_10', 'ENTP_10', 'EOM_14_100000000', 'ER_10', 'BULLP_13', 'BEARP_13', 
    'FISHERT_9_1', 'FISHERTs_9_1', 'FWMA_10', 'HA_open', 'HA_high', 'HA_low', 'HA_close', 'HILO_13_21', 'HILOl_13_21', 'HILOs_13_21', 
    'HL2', 'HLC3', 'HMA_10', 'HWM', 'HWU', 'HWL', 'HWMA_0.2_0.1_0.1', 'ISA_9', 'ISB_26', 'ITS_9', 'IKS_26', 'ICS_26', 'INC_1', 
    'INERTIA_20_14', 'JMA_7_0', 'KAMA_10_2_30', 'KCLe_20_2', 'KCBe_20_2', 'KCUe_20_2', 'K_9_3', 'D_9_3', 'J_9_3', 
    'KST_10_15_20_30_10_10_10_15', 'KSTs_9', 'KURT_30', 'KVO_34_55_13', 'KVOs_34_55_13', 'LR_14', 'LOGRET_1', 'MACD_12_26_9', 
    'MACDh_12_26_9', 'MACDs_12_26_9', 'MAD_30', 'MASSI_9_25', 'MCGD_10', 'MEDIAN_30', 'MFI_14', 'MIDPOINT_2', 'MIDPRICE_2', 'MOM_10', 
    'NATR_14', 'NVI_1', 'OHLC4', 'PDIST', 'PCTRET_1', 'PGO_14', 'PPO_12_26_9', 'PPOh_12_26_9', 'PPOs_12_26_9', 'PSARl_0.02_0.2', 
    'PSARs_0.02_0.2', 'PSARaf_0.02_0.2', 'PSARr_0.02_0.2', 'PSL_12', 'PVI_1', 'PVO_12_26_9', 'PVOh_12_26_9', 'PVOs_12_26_9', 'PVOL', 
    'PVR', 'PVT', 'PWMA_10', 'QQE_14_5_4.236', 'QQE_14_5_4.236_RSIMA', 'QQEl_14_5_4.236', 'QQEs_14_5_4.236', 'QS_10', 'QTL_30_0.5', 
    'RMA_10', 'ROC_10', 'RSI_14', 'RSX_14', 'RVGI_14_4', 'RVGIs_14_4', 'RVI_14', 'SINWMA_14', 'SKEW_30', 'SLOPE_1', 'SMA_10', 'SMI_5_20_5',
     'SMIs_5_20_5', 'SMIo_5_20_5', 'SQZ_20_2.0_20_1.5', 'SQZ_ON', 'SQZ_OFF', 'SQZ_NO', 'SQZPRO_20_2.0_20_2_1.5_1', 'SQZPRO_ON_WIDE', 
     'SQZPRO_ON_NORMAL', 'SQZPRO_ON_NARROW', 'SQZPRO_OFF', 'SQZPRO_NO', 'SSF_10_2', 'STC_10_12_26_0.5', 'STCmacd_10_12_26_0.5', 
     'STCstoch_10_12_26_0.5', 'STDEV_30', 'STOCHk_14_3_3', 'STOCHd_14_3_3', 'STOCHRSIk_14_14_3_3', 'STOCHRSId_14_14_3_3', 'SUPERT_7_3.0', 
     'SUPERTd_7_3.0', 'SUPERTl_7_3.0', 'SUPERTs_7_3.0', 'SWMA_10', 'T3_10_0.7', 'TEMA_10', 'THERMO_20_2_0.5', 'THERMOma_20_2_0.5', 
     'THERMOl_20_2_0.5', 'THERMOs_20_2_0.5', 'TOS_STDEVALL_LR', 'TOS_STDEVALL_L_1', 'TOS_STDEVALL_U_1', 'TOS_STDEVALL_L_2', 
     'TOS_STDEVALL_U_2', 'TOS_STDEVALL_L_3', 'TOS_STDEVALL_U_3', 'TRIMA_10', 'TRIX_30_9', 'TRIXs_30_9', 'TRUERANGE_1', 
     'TSI_13_25_13', 'TSIs_13_25_13', 'TTM_TRND_6', 'UI_14', 'UO_7_14_28', 'VAR_30', 'VHF_28', 'VIDYA_14', 'VTXP_14', 'VTXM_14', 
     'VWAP_D', 'VWMA_10', 'WCP', 'WILLR_14', 'WMA_10', 'ZL_EMA_10', 'ZS_30', 'CDL_2CROWS', 'CDL_3BLACKCROWS', 'CDL_3INSIDE', 
     'CDL_3LINESTRIKE', 'CDL_3OUTSIDE', 'CDL_3STARSINSOUTH', 'CDL_3WHITESOLDIERS', 'CDL_ABANDONEDBABY', 'CDL_ADVANCEBLOCK', 
     'CDL_BELTHOLD', 'CDL_BREAKAWAY', 'CDL_CLOSINGMARUBOZU', 'CDL_CONCEALBABYSWALL', 'CDL_COUNTERATTACK', 'CDL_DARKCLOUDCOVER', 
     'CDL_DOJI_10_0.1', 'CDL_DOJISTAR', 'CDL_DRAGONFLYDOJI', 'CDL_ENGULFING', 'CDL_EVENINGDOJISTAR', 'CDL_EVENINGSTAR', 
     'CDL_GAPSIDESIDEWHITE', 'CDL_GRAVESTONEDOJI', 'CDL_HAMMER', 'CDL_HANGINGMAN', 'CDL_HARAMI', 'CDL_HARAMICROSS', 'CDL_HIGHWAVE', 
     'CDL_HIKKAKE', 'CDL_HIKKAKEMOD', 'CDL_HOMINGPIGEON', 'CDL_IDENTICAL3CROWS', 'CDL_INNECK', 'CDL_INSIDE', 'CDL_INVERTEDHAMMER', 
     'CDL_KICKING', 'CDL_KICKINGBYLENGTH', 'CDL_LADDERBOTTOM', 'CDL_LONGLEGGEDDOJI', 'CDL_LONGLINE', 'CDL_MARUBOZU', 'CDL_MATCHINGLOW', 
     'CDL_MATHOLD', 'CDL_MORNINGDOJISTAR', 'CDL_MORNINGSTAR', 'CDL_ONNECK', 'CDL_PIERCING', 'CDL_RICKSHAWMAN', 'CDL_RISEFALL3METHODS', 
     'CDL_SEPARATINGLINES', 'CDL_SHOOTINGSTAR', 'CDL_SHORTLINE', 'CDL_SPINNINGTOP', 'CDL_STALLEDPATTERN', 'CDL_STICKSANDWICH', 'CDL_TAKURI', 
     'CDL_TASUKIGAP', 'CDL_THRUSTING', 'CDL_TRISTAR', 'CDL_UNIQUE3RIVER', 'CDL_UPSIDEGAP2CROWS', 'CDL_XSIDEGAP3METHODS'
]

TIMESERIES_WINDOWS_SIZE = 10

# trading setting
SYMBOL = "BTCUSDT"
QUANT = 0.00001
STOP_LOSS_RATE = 0.1
STOP_LOSS_TRIGGER_RATE = 0.08
TAKE_PROFIT_RATE = 0.2
TAKE_PROFIT_TRIGGER_RATE = 0.18
