#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/4/28 11:01
# @Author  : Bohan Li


import datetime
from WindPy import w
from pymongo import MongoClient


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

    # ////////// DATABASE(FUND), COLLECTION(122015.SH), DATE, TIME, NAME, VALUE, NOTE1, NOTE2
    w.start()
    date = '20190423'  # date = datetime.date.today().strftime('%Y%m%d')
    codes = ['XT1609837.XT', 'XT1708850.XT', 'XT1713629.XT']
    data_dict = {code: [] for code in codes}

    # ////////// 基本资料
    # ////////// 分级基金指标
    # ////////// 业绩表现
    # /// 复权单位净值
    get(codes, 'NAV_adj', 'tradeDate={}'.format(date), '复权单位净值')

    # ////////// 行情指标
    # ////////// 货币市场基金收益
    # ////////// 绩效评估
    # ////////// 基金分红
    # ////////// 基金规模
    # ////////// 持有人结构
    # ////////// 投资组合
    # ////////// 财务指标
    # ////////// 财务报表

    for code, docs in data_dict.items():
        client['FUND'][code].insert_many(docs)
