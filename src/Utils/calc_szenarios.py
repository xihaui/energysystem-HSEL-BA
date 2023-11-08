import numpy as np
import pandas as pd
from hplib import hplib as hpl

def calc_kpi(p_consumtion, p_production, p_gas):
    p_dif=p_production-p_consumtion
    p_gridfeed = np.maximum(0,p_dif)
    p_gridsupply = np.minimum(0,p_dif)
    return-p_dif.min()/1000, p_gridfeed.mean()*8.76, -p_gridsupply.mean()*8.76, p_gas.mean()*8.76, p_gas.max()/1000 # maximaler Netzbezug in kW , Netzeinspeisung [kWh], Netzbezug [kWh], Gasbezug [kWh], Leistung gas[kW]


def calculate_df(df, wka, bhkw, pv, wp, gas, vorlauf_temp):
    new_df=pd.DataFrame(index=df.index)
    new_df['Stromverbrauch [W]']=df['Gesamtverbrauch Hochschule [W]']
    new_df['Raumwämebedarf [W]']=df['Raumwämebedarf [W]']
    if wka=='Aus':
        new_df['WKA-Leistung [W]']=0
    else:
        new_df['WKA-Leistung [W]']=df['WKA-Leistung [W]']
    if pv=='25 kWp':
        new_df['PV [W]']=df['PV - Vorhanden [W]']*1000
    elif pv== '500 kWp':
        new_df['PV [W]']=df['PV - Vorhanden [W]']*1000+df['PV_Süd [W]']+df['PV_Ost [W]']+df['PV_West [W]']
    elif pv== '1.000 kWp':
        new_df['PV [W]']=df['PV - Vorhanden [W]']*1000+(df['PV_Süd [W]']+df['PV_Ost [W]']+df['PV_West [W]'])*2
    elif pv== '1.500 kWp':
        new_df['PV [W]']=df['PV - Vorhanden [W]']*1000+(df['PV_Süd [W]']+df['PV_Ost [W]']+df['PV_West [W]'])*3
    elif pv== '2.000 kWp':
        new_df['PV [W]']=df['PV - Vorhanden [W]']*1000+(df['PV_Süd [W]']+df['PV_Ost [W]']+df['PV_West [W]'])*4

    if (bhkw=='Ein'):
        new_df['BHKW Strom [W]']=df['BHKW Strom [W]']
    elif (bhkw=='Lastspitzen (mit Wärmepumpe)' and wp=='Aus'):
        P_el_chp = []
        for timestamp in df.index:
            wärmebedarf=df.loc[timestamp,'Raumwämebedarf [W]']
            strombedarf=df.loc[timestamp,'Gesamtverbrauch Hochschule [W]']-new_df.loc[timestamp, 'WKA-Leistung [W]'] - new_df.loc[timestamp, 'PV [W]']
            if (strombedarf> 0) and (wärmebedarf > 0):
                P_el_chp.append(np.minimum(np.minimum(wärmebedarf, 101_000*1.13)/1.13, strombedarf))
            else:
                P_el_chp.append(0)
        new_df['BHKW Strom [W]']=P_el_chp

    elif bhkw=='Aus':
        new_df['BHKW Strom [W]']=0
    
    if wp!='Aus':
        brine=hpl.HeatingSystem()
        if wp.startswith('Luft'):
            group_id=1
        else:
            group_id=5
        P_el_hp = []
        P_th_hp = []
        P_el_chp = []
        heat_pump=hpl.HeatPump(hpl.get_parameters('Generic',group_id,-7,52,int(wp.split(' ')[1])*1000))
        for timestamp in df.index:
            try:
                wärmebedarf=df.loc[timestamp,'Raumwämebedarf [W]']-new_df.loc[timestamp, 'BHKW Strom [W]']*1.13
                strombedarf=df.loc[timestamp,'Gesamtverbrauch Hochschule [W]'] - new_df.loc[timestamp, 'BHKW Strom [W]']-new_df.loc[timestamp, 'WKA-Leistung [W]'] - new_df.loc[timestamp, 'PV [W]']
                bhkw_on=1
            except:
                wärmebedarf=df.loc[timestamp,'Raumwämebedarf [W]']
                strombedarf=df.loc[timestamp,'Gesamtverbrauch Hochschule [W]']-new_df.loc[timestamp, 'WKA-Leistung [W]'] - new_df.loc[timestamp, 'PV [W]']
                bhkw_on=0
            if group_id==5:
                t_in=brine.calc_brine_temp(df.loc[timestamp,'Tages-Durchschnittstemperatur [°C]'])
            else:
                t_in=df.loc[timestamp,'Temperatur Luft [°C]']
            if wärmebedarf>0:
                res=heat_pump.simulate(t_in,vorlauf_temp-5,df.loc[timestamp,'Temperatur Luft [°C]'])
                if res['COP']>3: # Wärmegestehung eigentlich Bedingung ökonomisch zu betrachten (if strompreis/cop < gaspreis/wirkungsgrad brenner :)
                    p_th_hp=np.minimum(wärmebedarf, res['P_th'])
                else:
                    if strombedarf<0: # Überschussstrom zu Wärme
                        p_th_hp=np.minimum(np.minimum(wärmebedarf, strombedarf*-1*res['COP']),res['P_th'])
                    else:
                        p_th_hp=0
                        res['P_el']=0      
                p_el_hp=p_th_hp/res['COP']
                p_el_hp_hp_dif=p_el_hp-res['P_el']
                strombedarf+=p_el_hp
                wärmebedarf=wärmebedarf-p_th_hp
            else:
                p_th_hp=0
                p_el_hp=0
                p_el_hp_hp_dif=0
            if (strombedarf+p_el_hp_hp_dif > 0) and (wärmebedarf > 0):
                P_el_chp.append(np.minimum(np.minimum(wärmebedarf, 101_000*1.13)/1.13, strombedarf+p_el_hp_hp_dif))
                strombedarf=strombedarf-np.minimum(np.minimum(wärmebedarf, 101_000*1.13)/1.13, strombedarf+p_el_hp_hp_dif)
                wärmebedarf=wärmebedarf-(np.minimum(np.minimum(wärmebedarf, 101_000*1.13)/1.13, strombedarf+p_el_hp_hp_dif))*1.13
                if wärmebedarf>0:
                    p_el_hp=p_el_hp + np.minimum(p_el_hp_hp_dif*-1, wärmebedarf/res['COP'])
                    p_th_hp = p_th_hp + np.minimum(p_el_hp_hp_dif*-1*res['COP'], wärmebedarf)
            else:
                P_el_chp.append(0)
            P_el_hp.append(p_el_hp)
            P_th_hp.append(p_th_hp)
        new_df['Wärmepumpe Strom [W]']=P_el_hp
        new_df['Wärmepumpe Wärme [W]']=P_th_hp
        if bhkw_on==0:
            new_df['BHKW Strom [W]']=P_el_chp
    else:
        new_df['Wärmepumpe Strom [W]']=0
        new_df['Wärmepumpe Wärme [W]']=0
    new_df['BHKW Wärme [W]']=new_df['BHKW Strom [W]']*1.13
    new_df['Gaskessel [W]'] = new_df['Raumwämebedarf [W]']-new_df['BHKW Wärme [W]']-new_df['Wärmepumpe Wärme [W]']
    if gas.startswith('Zwei'):
        new_df['Gasverbrauch [W]'] = new_df['Gaskessel [W]']/0.915 + new_df['BHKW Strom [W]']/0.3232
    else:
        new_df['Gasverbrauch [W]'] = new_df['Gaskessel [W]']/0.9 + new_df['BHKW Strom [W]']/0.3232
    p_el_max, E_gf, E_gs, E_gas,p_gas_max=calc_kpi(new_df['Stromverbrauch [W]']+new_df['Wärmepumpe Strom [W]'],new_df['BHKW Strom [W]']+new_df['PV [W]']+new_df['WKA-Leistung [W]'],new_df['Gasverbrauch [W]'])
    #return new_df
    return p_el_max, E_gf, E_gs, E_gas,p_gas_max, new_df['BHKW Strom [W]'].mean()*8.76/101, (new_df['Wärmepumpe Wärme [W]'].mean()*8.76) / (new_df['Wärmepumpe Strom [W]'].mean()*8.76), (new_df['BHKW Strom [W]']+new_df['PV [W]']+new_df['WKA-Leistung [W]']).mean()*8.76, new_df['Wärmepumpe Strom [W]'].mean()*8.76 
