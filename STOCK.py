#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/4/23 9:56
# @Author  : Bohan Li


import os
import math
import datetime
import pandas as pd
from WindPy import w
from pymongo import MongoClient
import pickle

import datetime
from WindPy import w
from pymongo import MongoClient


def df2dict(df, name_in_csv, name_in_db):
    df = df[['日期', name_in_csv]]
    df = df.rename(columns={'日期': 'DATE', name_in_csv: 'VALUE'})
    df['NAME'] = name_in_db
    df = df.dropna()
    df = df.astype(str)
    return [df.loc[i].to_dict() for i in df.index]


def get(codes, fields, options, name, note1=None, note2=None, flag=True):
    global date
    global data_dict
    d = w.wss(codes, fields, options)
    for c, v in zip(d.Codes, d.Data[0]):
        # 对于特殊返回类型的特殊处理
        if isinstance(v, datetime.datetime):
            v = v.date().strftime('%Y%m%d')
        if note2:
            data_dict[c].append({'DATE': str(date), 'NAME': str(name), 'VALUE': str(v), 'NOTE1': note1, 'NOTE2': note2})
        elif note1:
            data_dict[c].append({'DATE': str(date), 'NAME': str(name), 'VALUE': str(v), 'NOTE1': note1})
        elif flag:
            data_dict[c].append({'DATE': str(date), 'NAME': str(name), 'VALUE': str(v)})
        else:
            data_dict[c].append({'NAME': str(name), 'VALUE': str(v)})


if __name__ == '__main__':
    client = MongoClient(host='139.199.125.235', port=8888)
    '''
    # ////////// 行情指标, DATA SOURCE=行情序列
    data = {i: pd.read_csv(os.path.join('csv', i), encoding='cp936') for i in os.listdir('csv')}
    data_dict = {}
    for i, df in data.items():
        i = i.strip('.CSV')
        data_dict[i] = []

        # /// 前收盘价
        data_dict[i] += df2dict(df, '前收盘价(元)', '前收盘价')

        # /// 开盘价
        data_dict[i] += df2dict(df, '开盘价(元)', '开盘价')

        # /// 最高价
        data_dict[i] += df2dict(df, '最高价(元)', '最高价')

        # /// 最低价
        data_dict[i] += df2dict(df, '最低价(元)', '最低价')

        # /// 收盘价
        data_dict[i] += df2dict(df, '收盘价(元)', '收盘价')

        # /// 均价
        data_dict[i] += df2dict(df, '均价(元)', '均价')

        # /// 涨跌
        data_dict[i] += df2dict(df, '涨跌(元)', '涨跌')

        # /// 涨跌幅
        data_dict[i] += df2dict(df, '涨跌幅(%)', '涨跌幅')

        # /// 换手率
        # data_dict[i] += df2dict(df, '换手率(%)', '换手率')

        # /// 成交量
        data_dict[i] += df2dict(df, '成交量(股)', '成交量')

        # /// 成交额
        data_dict[i] += df2dict(df, '成交金额(元)', '成交额')
        
        # pickle.dump(data_dict, open('data_dict.pkl', 'wb'))
        print(i)

    # data_dict = pickle.load(open('data_dict.pkl', 'rb'))
    for code, docs in data_dict.items():
        client['STOCK'][code].insert_many(docs)
    '''

    # ////////// DATABASE(STOCK), COLLECTION(000001.SZ), DATE, TIME, NAME, VALUE, NOTE1, NOTE2
    w.start()
    date = datetime.date.today().strftime('%Y%m%d')
    codes = w.wset("sectorconstituent", "date={};sectorid=a001010100000000".format(date)).Data[1]  # 全部A股codes
    codes = codes[:10]  # 写代码时不用请求全部的
    data_dict = {code: [] for code in codes}

    # ////////// 基本资料
    # ////////// 股本指标
    # ////////// 股东指标
    # ////////// 行情指标
    # ////////// 估值指标
    # /// 总市值1
    get(codes, 'ev', 'unit=1;tradeDate={}'.format(date), '总市值1')
    
    ## ///每股收益
    get(codes,"eps_ttm","tradeDate={}".format(data),'每股收益')
    
    ## ///市现率
    get(codes,"pcf_ocf","tradeDate={};ruleType=2".format(data),'市现率经营现金流','上年年报')
    get(codes,"pcf_ncf","tradeDate={};ruleType=2".format(data),'市现率现金净流量','上年年报')
    
    ## ///市盈率
    get(codes, "qstmnote_insur_212530","unit=1;rptDate={}".format(date),'市盈率')
    
    ## ///股息率
    get(codes, "dividendyield","tradeDate={};rptYear=2018".format(date),'股息率')
    
   
    

    # ////////// 风险分析
    
    ## /// BETA
    get(codes,"beta_100w","tradeDate={}".format(data),'BETA')
    

    # ////////// 盈利预测
    
    ##///一致预测每股收益
    get(codes, "west_eps_FY1","tradeDate={}".format(date),'致预测每股收益(FY1)')
    get(codes, "west_eps_FY2","tradeDate={}".format(date),'致预测每股收益(FY2)')
    get(codes, "west_eps_FY3","tradeDate={}".format(date),'致预测每股收益(FY3)')
    
    # ////////// 财务分析
    
    ##/// 单季度基本每股收益 
    get(codes, "wgsd_qfa_eps_basic","rptDate={};rptType=1;currencyType=".format(date),'单季度基本每股收益 ','合并报表'）

    ## ///总资产净利率ROA
    get(codes,"roa","rptDate={}".format(date),'总资产净利率ROA') 
    
    ## /// 研发支出合计
    get(codes, "stmnote_RDexp","unit=1;rptDate={};rptType=1".format(date),'研发支出合计')
        
    ## /// 净现金流
    get(codes, "qstmnote_insur_212530","unit=1;rptDate={}".format(date),'净现金流')    
        
    ## ///净营运资本
    get(codes ,"networkingcapital","unit=1;rptDate={}".format(date),'净营运资本')    
        
        
    ## /// 每股现金流净额
    get(codes, "cfps","rptDate={};currencyType=".format(date),'每股现金流净额')    
    
    # ////////// 财务报表
    # /// 存货
    get(codes, 'inventories', 'unit=1;rptDate={};rptType=1'.format(date), '存货', '合并报表')

    # /// 资产总计
    get(codes, 'tot_assets', 'unit=1;rptDate={};rptType=1'.format(date), '资产总计', '合并报表')

    # /// 所有者权益合计
    get(codes, 'tot_equity', 'unit=1;rptDate={};rptType=1'.format(date), '所有者权益合计', '合并报表')

    # /// 净利润
    get(codes, 'net_profit_is', 'unit=1;rptDate={};rptType=1'.format(date), '净利润', '合并报表')

    # /// 营业总收入
    get(codes, 'tot_oper_rev', 'unit=1;rptDate={};rptType=1'.format(date), '营业总收入', '合并报表')

    # /// 营业收入
    get(codes, 'oper_rev', 'unit=1;rptDate={};rptType=1'.format(date), '营业收入', '合并报表')

    # /// 营业总成本
    get(codes, 'tot_oper_cost', 'unit=1;rptDate={};rptType=1'.format(date), '营业总成本', '合并报表')

    # /// 递延所得税
    get(codes, 'stmnote_incometax_5', 'unit=1;rptDate={};rptType=1'.format(date), '递延所得税', '合并报表')

    # /// 构建固定资产、无形资产和其他长期资产支付的现金
    get(codes, 'cash_pay_acq_const_fiolta', 'unit=1;rptDate={};rptType=1'.format(date), '构建固定资产、无形资产和其他长期资产支付的现金', '合并报表')

    ## /// 单季度净利润
    get(codes, 'wgsd_qfa_nogaapprofit','unit=1;rptDate={};rptType=1;currencyType='.format(date),'单季度净利润','合并报表')
    
    ## ///投资活动现金流出小计
    get(codes, "stot_cash_outflows_inv_act","unit=1;rptDate={};rptType=1".format(date),'投资活动现金流出小计')
       
    ## /// 销售费用  
    get(codes, "operateexpense_ttm2","unit=1;rptDate={}".format(date),'销售费用','合并报表')
     
    ## /// 资产总计
    get(codes, "tot_assets","unit=1;rptDate={};rptType=1".format(date),'资产总计','合并报表')  
    
    ## ///所有者权益合计
    get(codes, "tot_equity","unit=1;rptDate={};rptType=1".format(date),'所有者权益合计','合并报表')
        
    ## ///营业总收入
    get(codes, "tot_oper_rev","unit=1;rptDate={};rptType=1".format(date),'营业总收入','合并报表')

    ## /// 货币资金
    get(codes, "monetary_cap","unit=1;rptDate={};rptType=1".format(date),'货币资金','合并报表')
        
    ## /// 交易性金融资产
    get(codes,"wgsd_invest_trading","unit=1;rptDate={};rptType=1;currencyType=".format(date),'交易性金融资产','合并报表') 
        
    ## ///总资产
    get(codes, "wgsd_assets","unit=1;rptDate={};rptType=1;currencyType=".format(date),'总资产','合并报表')
        
    # ////////// 报表附注
    # /// 固定资产-累计折旧
    get(codes, 'stmnote_assetdetail_2', 'unit=1;rptDate={}'.format(date), '固定资产-累计折旧')

    # /// 投资性房地产-累计折旧
    get(codes, 'stmnote_assetdetail_6', 'unit=1;rptDate={}'.format(date), '投资性房地产-累计折旧')

    # /// 生产性生物资产-累计折旧
    get(codes, 'stmnote_assetdetail_10', 'unit=1;rptDate={}'.format(date), '生产性生物资产-累计折旧')

    # /// 油气资源-累计折耗
    get(codes, 'stmnote_assetdetail_14', 'unit=1;rptDate={}'.format(date), '油气资源-累计折耗')
        
        
    ## /// 广告宣传推广费
    get(codes, "stmnote_others_7633","unit=1;rptDate={};rptType=1".format(date),'广告宣传推广费','合并报表')
      
    ## ///商誉减值损失
    get(codes, "stmnote_ImpairmentLoss_6","unit=1;rptDate={};rptType=1".format(date),'商誉减值损失','合并报表')

    # ////////// 分红指标
    # ////////// 首发指标
    
    ## ///发行数量合计
    get(codes, "ipo_amount","unit=1",'发行数量合计')
        
    ## ///新股发行数量    
    get(codes ,"ipo_newshares","unit=1",'新股发行数量 ')
        
    ## ///首发上市日期
    get(codes ,"ipo_date",'首发上市日期')    
        
    # ////////// 增发指标
    # /// 增发上市日
    get(codes, 'fellow_listeddate', 'year=2018', '增发上市日', flag=False)

    # /// 公开发行日
    get(codes, 'fellow_issuedate', 'year=2018', '公开发行日', flag=False)

    # ////////// 配股指标
    # ////////// 可转债发行
    # ////////// 股权分置改革
    # ////////// 技术形态
    # ////////// 其他指标
    
    ## /// 增长率——利润总额
    get(codes, 'fa_tpgr_ttm','tradeDate={}'.format(date),'增长率——利润总额')
    
    ## /// 增长率——净利润
    get(codes, 'fa_npgr_ttm' ,'tradeDate={}'.format(date),'增长率——净利润')
    
    ##/// 20日收益方差
    get(codes,"risk_variance20",'tradeDate={}'.format(date),'20日收益方差')
     
    ##///现金流资产比——资产回报率
    get(codes,"fa_acca_ttm",'tradeDate={}'.format(date),'现金流资产比——资产回报率')

  
    
   
    

    for code, docs in data_dict.items():
        client['STOCK'][code].insert_many(docs)
