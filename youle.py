import datetime
import hashlib
import json
import logging
import sys
import time
from urllib import parse

import requests
from notify import send

# 每次循环间隔时间
range_time = 2
# 请求间隔时间
time_sleep = 0.05

authorization_list = [
    {
        'nick': '竹子173****4404',
        'yshUsrId': '206202036',
        'cookie': 'ul_vtk="uv=0420328103596740&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695128596741&&utl=1695128596741&&utc=1695128596741&&pf=319,198"; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aad89aed13ee-0e7b66546b98e6-48731f21-304500-18aad89aed2a28%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWQ4OWFlZDEzZWUtMGU3YjY2NTQ2Yjk4ZTYtNDg3MzFmMjEtMzA0NTAwLTE4YWFkODlhZWQyYTI4In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aad89aed13ee-0e7b66546b98e6-48731f21-304500-18aad89aed2a28%22%7D; ule_ck=934828914_1695128597_1695128596744_1695128596744; ule_usession=0240310085596744%7Cref_aHR0cHM6Ly95b3VzaGVuZ2h1by4xMTE4NS5jbg; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**206202036; ul_utk="MjNzZjNkd2lvfHRlaGIvMEtzSU5RUm9UOFRNNDQvaC96NkM3L1JZRDgrdWx5blhkM0hZVXZaSHNkR2V6TnFHN2QwSzFoTkFWWXdmR1F2alA5Z2ZWUnp4cWpYWTh5cmVVV0svNlFpaVIzdk4vcUt1aE1kUUpsZXl4RjdMa1JJdVM0WFI4NTE1ck42U1dRWW52cGJ1OXllTXI3RFM0Z0hac0taR0FOMXFOSm9LTUk2ZWVJcWdYbz18RGd0YzZXQ3V6d0E5WVhVeTNNWFR3ZDJYbEthQlh2dTIvQXMwYVpQWXBMZ25HcWxBRzc0QjBiVHVWQWh3TUhzOGxncGR5OWlXY0lDd2FPNEpNSWxxMVNzelJKd28zTDBnbXhPalZDTEsxRVh5SlNxL1M1NE9DU2dVTjFtK2N6T0xDL0FrR1lOWFJ1TE02TUt3dm96ZGp2bUVxdFBQY21zSSszNmFoSk9RMzNZclIvM3hyd3ZpeEouLg=="',
    },
    {
        'nick': '竹子191****4151',
        'yshUsrId': '206142841',
        'cookie': 'ul_vtk="uv=3759959238237988&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695129262774&&utl=1695129237989&&utc=1695129237989&&pf=335,261"; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aad93720d910-03289843fc590e4-48731f21-304500-18aad93720e98a%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWQ5MzcyMGQ5MTAtMDMyODk4NDNmYzU5MGU0LTQ4NzMxZjIxLTMwNDUwMC0xOGFhZDkzNzIwZTk4YSJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aad93720d910-03289843fc590e4-48731f21-304500-18aad93720e98a%22%7D; ule_ck=788020012_1695129238_1695129237995_1695129262777; ule_usession=0497418990237992%7Cylxdfx_merchant_yljf; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**206142841; ul_utk="MjNzZjNkd2lvfFRoL2V0bjdqaElDcjNvV21POWUrZFJkaG9DMWJPOHpzZVN4Q2tBQ01PcW9Ic3dGOE4zZzdrS3pTUnRvdVJ4YktLK0FCRnJZeEhkSGtSQTl2c0hDaEV1U3hSUHJKWkVvb2dGbDJyZ0kvVTRkelpkTjEyREd2V1ZGd3dnd3p4cUc3L3hUQ1BBQlEyVFh4ZGNsdVBrZWMzNXJzMERFWHRtTXZ6S3FJbmVQTjMzST18Qlk3aFJ5TTdqYmw3T2ZUNy94R2ZyQVQ1Tk5QaHN0WW8rRDJBWGo2RGxkbFlXZGhaWDFKejR2eXBFQ0EvOUVaQURGdzV6RE5MS3JxZkxhcFd6VFN4amJVekZPOFoyK0tJM2NacGp1K01FVEdxOUpiTzlOVzFEYUlVOU55cTNLYVJ5bUlYbzdpeGloOWNadUhLQ2pKUGdtOStEMnZtNGxoK3Q3bmh1OGpwY1JVQzFOMjBhS0pKcEouLg=="; ul_adid=ylxdfx_merchant_yljf; sajssdk_2015_cross_new_user=1',
    },
    {
        'nick': '竹子15555****1130',
        'yshUsrId': '205460893',
        'cookie': 'ul_vtk="uv=9155369949504908&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695129513061&&utl=1695129504909&&utc=1695129504909&&pf=344,246"; ule_ck=932524822_1695129505_1695129504913_1695129513066; ule_usession=7298110167504912%7Cylxdfx_merchant_yljf; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aad9785dd8d6-01fdf696b86eb01-48731f21-304500-18aad9785de7ee%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWQ5Nzg1ZGQ4ZDYtMDFmZGY2OTZiODZlYjAxLTQ4NzMxZjIxLTMwNDUwMC0xOGFhZDk3ODVkZTdlZSJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aad9785dd8d6-01fdf696b86eb01-48731f21-304500-18aad9785de7ee%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**205460893; ul_utk="MjNzZjNkd2lvfG5DcEc1R0VRb3c1R1NQMC9WWm1QSGE1K3BRaFZwVUJqa0svekkvMEtQY1dDN3FTKzhQamJPSUR5dnl3aUhidXRob1hQSGxIVUlXQkZsL2tobWlKN01odlZzSHBQVjNFME0rZGtBMy9qb0RsUWFsREo2TDVQSnZIYVVrbDJrOWt4SHo3SGlYQ05pdUJGaVI0YXNWSE9aRG5JdHhXNTBMVk1LUHhFQVlHNDRkQT18aGVCcHk0eUlZemtpOHh1dU9GWWlYY1VNWnl3S3dMWm14NWpuWEZSZ3pna3k3elM5alBiUk5PMzU2cE5Db3pxdGJNL2hsOW9WekoyWHRjUUZteklEWmFSQU1RT0RueTFybi9MTW13SVpMVVZWeWVMS0NPak05YXYwb3QxdFRabDQ1RG93ZUFwOFdwNU83SkxsdENCNUJwYkEyOGZ5Y29tdUdLQlFvUklEK042U2hWVU92SkJ3NlcuLg=="; ul_adid=ylxdfx_merchant_yljf; sajssdk_2015_cross_new_user=1',
    },
    {
        'nick': '竹子189****1840',
        'yshUsrId': '206142935',
        'cookie': 'ul_vtk="uv=0714064614626854&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695129642479&&utl=1695129626857&&utc=1695129626857&&pf=338,241"; ule_ck=613708330_1695129627_1695129626862_1695129642484; ule_usession=0620490552626860%7Cylxdfx_merchant_yljf; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aad99a2c4413-0286d905447a34a-48731f21-304500-18aad99a2c59b4%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWQ5OWEyYzQ0MTMtMDI4NmQ5MDU0NDdhMzRhLTQ4NzMxZjIxLTMwNDUwMC0xOGFhZDk5YTJjNTliNCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aad99a2c4413-0286d905447a34a-48731f21-304500-18aad99a2c59b4%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**206142935; ul_utk="MjNzZjNkd2lvfGYrTy9ONWRDNVRjMmRKNFpXdjlSUk1SZTdYZUpaYm5selI1UFE1Q2s3WFlTZ2Y4MEg3YlBXSjRjR0lQRUY5QUJVUVBZU3hyOHpWTmRmeFE4cDIreVlHUE5QbGRYTDUvblFMTXd4Mkg4aXB3MHAvY0lGRlpXMjdHVm1vd3RKWm9mOWxZN2JKYzFBYTZNWlVJQk9XQW1jTzRsdklOdjFvTS82eWZ6MEZGbFIrRT18OGJiR2VqTkM2UjJWQkRJbUtZdFBmcHllYTZWc2hLeUJQUFltU3gwc013eS8rdzFHN2x2cGZvVHNyQVBSanBCUjR5ak5Jck00TWpWbXR0QXBJMDEvUk9lOXhOL0xtcEtYNUluSHVMV1orWUNaZW0waUM5V2VGRmJqckM0L3JEK3hVN3EvcVA4MXF4QUsxREhpRXlhTDYxTEdJU1JwbHJzak5zdmhva21xbnJacTc5V2tpMlRCNkouLg=="; ul_adid=ylxdfx_merchant_yljf',
    },
    {
        'nick': '186****3727',
        'yshUsrId': '147504351',
        'cookie': 'ul_vtk="uv=6074244960730806&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695129741888&&utl=1695129730807&&utc=1695129730807&&pf=336,245"; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aad9af61e37f-0d4dd181709575-48731f21-304500-18aad9af61f9a7%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWQ5YWY2MWUzN2YtMGQ0ZGQxODE3MDk1NzUtNDg3MzFmMjEtMzA0NTAwLTE4YWFkOWFmNjFmOWE3In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aad9af61e37f-0d4dd181709575-48731f21-304500-18aad9af61f9a7%22%7D; ule_ck=618588611_1695129731_1695129730811_1695129741893; ule_usession=4569714402730808%7Cylxdfx_merchant_yljf; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**147504351; ul_utk="MjNzZjNkd2lvfERIb2dEZ1g0cTZPbEtTTkF5WUNPQkNWSTFUcTJkSjd1RjlpWDJ6SWlpeHVhL25lZlEzM0haMjlWN2hWR055d3hLSkNCbnk3LzdjVThQckYxM3NOWURTRTJQTWhrQ2dyZXpmYWVsc0xqV3gycVQ2VnhFYzMyMjA3QXI0MlpXamFqNlg0U1hlZmlacHpocGNRNmh0QjFSL0NRNlA5Sk1scEM3b3paV3Z1bkZLST18SFhEKzBWUTcvN1Ezd1dydUlhajFtUWphWnB3V1N6Y045YVJmZms0M0wxSWh6WS9zaGJvMlNvUkpIUlF6THdyT0NpZEtkRktBeHNvaE9iY3E1NVVHNEtSak9aTWFRS1JzcVlDSUovYUZGSXJzdjZ1djE5clpIQ2xBV1R2Sk40MTJNUEVqMnZCQmd2SVUyUXRhT2FqTXR1R1VDQ0Q2dUR6MjZCTnJGVTladzN5cGR4NkQ0Nm44U1cuLg=="; ul_wmid=oSwO04qP8SdIBSP2WKwhfmMQdt7k; ul_adid=ylxdfx_merchant_yljf; sajssdk_2015_cross_new_user=1',
    },
    {
        'nick': '竹子186****0098',
        'yshUsrId': '147273305',
        'cookie': 'ul_vtk="uv=6816074631834028&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695129880858&&utl=1695129873686&&utc=1695129834029&&pf=325,251"; ule_ck=1530943367_1695129834_1695129873691_1695129880862; ule_usession=1026548898834032%7Cylxdfx_merchant_yljf; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aad9c879ea5c-0ecd5ca338d1938-48731f21-304500-18aad9c879fa31%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWQ5Yzg3OWVhNWMtMGVjZDVjYTMzOGQxOTM4LTQ4NzMxZjIxLTMwNDUwMC0xOGFhZDljODc5ZmEzMSJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aad9c879ea5c-0ecd5ca338d1938-48731f21-304500-18aad9c879fa31%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**147273305; ul_utk="MjNzZjNkd2lvfHZmSmtDMGlzODJRTGdBZFRiRnBuMzloRzJSczRZeExraUxvSDgxL3cwOUhlK0Jvd3ZwcldxQlRRUkY1QmpObmI4M05jR1RLOGZDWUsrTTl1aitxV0FEMXJaZU5CbXBqM2ZrMTNBOEdWT3MybURIZnVhdXUrV0I4ckN0ZXlJQVBkeWdOc21PWUI2RGc4RWxUazRJMEl5bDJMZDVGY050dG5qVUJtbWd0SlNpdz18bmRDTEx6bGhMc045aEc5cjJuWk8xa2t4OU9LMGpjUDhabGxUeTFmNHBHK0hDOHl3OFFFUmc3ZkFaQWVVc1JvNnk0REM2NXUyS0wyMDU2MThRQThmZ2hkczE0dnVpVWJ5VjJXNHhqQzF1a0pQOHVOTDdyTWVEVStUa0t2VjROKytjanp5UVkvZ3VxcTVMT3BnRlJNQ0lmMVFVemF2dXZNVUs0R0lQWjhZcGVFT3VKN1dxdWdiaFcuLg=="; store_id=1094524589; ul_sch=app_ylxd',
    },
    {
        'nick': '竹子133****2939',
        'yshUsrId': '146869073',
        'cookie': 'ul_vtk="uv=0218279509057676&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695130073634&&utl=1695130057680&&utc=1695130057680&&pf=330,248"; ule_ck=746218709_1695130058_1695130057686_1695130073639; ule_usession=0184059727057684%7Cylxdfx_merchant_yljf; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aad9ff4e83de-0549d0a9aef36dc-48731f21-304500-18aad9ff4e9c34%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWQ5ZmY0ZTgzZGUtMDU0OWQwYTlhZWYzNmRjLTQ4NzMxZjIxLTMwNDUwMC0xOGFhZDlmZjRlOWMzNCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aad9ff4e83de-0549d0a9aef36dc-48731f21-304500-18aad9ff4e9c34%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**146869073; ul_utk="MjNzZjNkd2lvfE52b05yd0JSWm5CK0dTT1BTSjFzVXRjb3A4UnV1NDVkMTY3WFd5cnl0ODE5b2E4YWtNOE9mZ2lTTWhtQXRvRWRzRE44MGY5YklFRUlhNGhSc3JGSGtzVkNRZG9oZDVWU2lGR0cvcklnNGJJWEFXVjI1TmJrZ1Y1V0ZiZHZHcmJUR1pQQ2dYMzk4N20zditoRXhRNmpKNlhLWTZ5RHBYcWM2REY2YTIxVVk0MD18VDdQcmN2VWx0cjhOZWdIUVZCMW13RGxJa2VCSUpybU4xQnB5cmNyV3FlWjB3d0dXclVVOURhZnViQTBzVWVVR1hBSFNiNUxRMFZLQnlZM3ZwL2NCSUVlWWJxQmhwRmJCS0treTFRMSthTnVKdWhpQjRqTGxOYkUwdFY1UkpUaVRzMXJ3Tk0rNWt4Tkw1TDZmd25lMjhEZElvR2trZFFHTHNrUlI4MDFBaDZvendXY0krRC9Ic0ouLg=="; ul_adid=ylxdfx_merchant_yljf; sajssdk_2015_cross_new_user=1',
    },
    {
        'nick': '竹子151****5335',
        'yshUsrId': '206142431',
        'cookie': 'ul_vtk="uv=6453893437195548&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695130290871&&utl=1695130285476&&utc=1695130195547&&pf=342,248"; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aada215d263-03b32a35cc72e6e-48731f21-304500-18aada215d3cb5%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWRhMjE1ZDI2My0wM2IzMmEzNWNjNzJlNmUtNDg3MzFmMjEtMzA0NTAwLTE4YWFkYTIxNWQzY2I1In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aada215d263-03b32a35cc72e6e-48731f21-304500-18aada215d3cb5%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ule_ck=1570645243_1695130196_1695130285479_1695130290875; ule_usession=0925113805195548%7C230816_ysh_yqy2; ul_union=1016039307**206142431; ul_utk="MjNzZjNkd2lvfGFWQU1DbUhPeVZRSUhJQjBsNGNZRy9RNHBBTlIvUWZCZmRFazNoM1I4K3cxOXFRZ0N5UnZMNVlxQkZZV1RwTHJKL0RUQWxNSXJId1YwU0x2cUV0c3A5bjJlOU9QbnEwZEFYVEdLYTlVVk5QdWJUcXdDYTZ6WjRxWmp2VnRVc3JlZXQ1OTBYUjBCV1FSVjR4Uyt5L2M5dGsrRExkaVpPaWNkUEZySEFxVUdtMD18LzdjT3B0LzdEakl3bmlUdmZUQVNrYkhLTitRNkhZU3d6SHNpb3cwcXgwTnkzRDBVdWt0M0VwSm5PMVRPN2hxSDh1Z25qdUFiSUZWdlU3dkN1WlZjSHUvdUQyaTdCK05JckZGOHFHMzMzdFRNUUREVGFPSVM4TjVZVDVUd3VYa0NxanRpU3hOLzhEaUdGOWk1ZkQ1YTU3ME5QbFpRa1cvbmkxeFgyaUZjODRnaGltUUxyYlgwblIuLg=="; ul_adid=ylxdfx_merchant_yljf; crmMemberInfo="23sf3dwio|QeNKlUI6UpDSCAwMrEgjp07MxwXDgJVItY/9kcaV1EDHJa6DtSNISDAi57xcvyPc4ZhTroUj4OGZAsJ5fvxSxCdjRqnlRLI0eA1CkiT6Xhlgq3VsgYCJnLIYpIbZ7WcYtIbRHzo9epZOz2cqXMa31oIHqsrV3hOhrcj4aIz3lwU=|TNeqbnQMz949XJx2UsLhkv0fKcq9dyo81YirYiTtL/lXyPnOoLGuQyb+1CwNozUoWdHUJ3ymcvEVvZdejPD7i2moU4gKNu6G3jyjSubypptWb7QmGzDikgE8KTbJW0XWzijHvYNL48zRnfp0mBZUjjtPpbbSenuXITU2V1npiD79f1TrMwQ4B5oGb90eyelsNAPRaA74+McPyYzE1SVHU0nIwWQtof41EEWtGj2wNs7xVq77JTmlpb51sTCSm1LYTz+6jZBX5FY0qsitCOORudZWPYRxKgHMnx4IIA1HfV/oBdSQmLIsyCubhtt8yG0rcuXS3DFG/xhyrFMCfORlyjX1Wr90kI9IENH1Rm/KZSb."; yshNickName=151****5335',
    },
    {
        'nick': '131****0918',
        'yshUsrId': '206201769',
        'cookie': 'ul_vtk="uv=9520019800414504&&pv=f9e52c839b91de2194349bbb70d0c46f&&utn=1695130414508&&utl=1695130414508&&utc=1695130414508&&pf=326,248"; ul_union=1016039307**206201769; ul_utk="MjNzZjNkd2lvfHR1aXVGZm1JTWNUU3RydjY1Z2Z6eEtNRnpURSs2QjFGMFRvZ1FkZmt3bEttZTVkbXovcFVqb0pJNDhsVWI4U2FvM0tQcmFiNS9aVVdVWGwzbm15MWhGMGt4SklHTU52L1p1TllkWDkxVFU4TkpFWTVkLzg1enVVT0VBaGQycmMvYnNTZ2I1Sm1ZQ0Nabno5cGx5OHBiYVczTURCZHE5blRaSDdsd2pRMXJrUT18VU1xcnJrNjlRR2xwM3ZhSGJFNW0yTUcza1REeGhQTTZQSDBPeXB2UW5pcmZRYVRZZXJLZDlmSVJZMzBaNXpsU2JNMm1vRno0MlZDc1Z5YmpkV1RzL0JyU0ZibDl3SHBSVXorb3VPOUxmR2ZBanM4UG90Z1NWbWo5NzNjVjdsZmJ3U2dFeThPZzVGV2ZNTXpMQjI5cXRaYm16TGFZWWoyd0IvdVY5RTdIRzdZL3hCT1Z1MjNhUUEuLg=="; ul_adid=ylxdfx_merchant_yljf; ule_ck=518115063_1695130415_1695130414513_1695130414513; ule_usession=4906868398414512%7Cylxdfx_merchant_yljf; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aada565bbc15-09227c0825a51e8-48731f21-304500-18aada565bc9cf%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWRhNTY1YmJjMTUtMDkyMjdjMDgyNWE1MWU4LTQ4NzMxZjIxLTMwNDUwMC0xOGFhZGE1NjViYzljZiJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aada565bbc15-09227c0825a51e8-48731f21-304500-18aada565bc9cf%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%25E5%25BA%2595%25E9%2583%25A8TAB-%25E7%259B%25B4%25E6%2592%25AD%26storeid%3D1094524589%26shareId%3D496515317%26appName%3Dylxd%26adid%3Dylxdfx_merchant_yljf%26statistics%3DWX',
    },
    {
        'nick': '竹子130****0038',
        'yshUsrId': '156197936',
        'cookie': 'ul_vtk="uv=2607134911555376&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695130570533&&utl=1695130555379&&utc=1695130555379&&pf=335,238"; ule_ck=1145954791_1695130555_1695130555383_1695130570538; ule_usession=0256064848555380%7Cylxdfx_merchant_yljf; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aada785d9b3c-037eb3602634f4c-48731f21-304500-18aada785da94f%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWRhNzg1ZDliM2MtMDM3ZWIzNjAyNjM0ZjRjLTQ4NzMxZjIxLTMwNDUwMC0xOGFhZGE3ODVkYTk0ZiJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aada785d9b3c-037eb3602634f4c-48731f21-304500-18aada785da94f%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**156197936; ul_utk="MjNzZjNkd2lvfGxWOUd1d2J4M2tnbW5DL2dDcnpvemtBZ3RiYy96eDhpSUY1bndlUmJGbm13NTFoLzlpbExlaTY0cWJucC8vNjVpdERYbVpkK29nUzJTQ3NRbTdqRVBNSExSbXR0K0haMWkvM3QxTXp4MG9HUGxMY0VUbGd4RFBWeU9MbGhpbUZZSmhPR3VEVjBwR3RHVks1OUNBTjJWWEVmVGQ4cUJnTkpRM2JSWjJTbHY4RT18Qmp4TEwrYTEzbFZUNGgxbDgyMUoydmpkbHFqd3ZDc3pzWFkzZ3crQ0d1WmxMZzNxcmJGcGw3dTdNQk9UMmo1MGJSMVlyelhqOEFtTkZWRzU5UVZNOC80SGVjYTd6ZlBxUmpNbTZLL0ZOdHI4WndNUzFmbjE1diszcW1qRnloZUZlVGpaZWQ3aG1aTndwN29COFBIU2RPVjAyVTZycUl4SXdqOUxhZmxVbno2UHpLb0JWcjRvN0ouLg=="; ul_adid=ylxdfx_merchant_yljf; sajssdk_2015_cross_new_user=1',
    },
    {
        'nick': '130****9918',
        'yshUsrId': '157733717',
        'cookie': 'ul_vtk="uv=9147081850710376&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695130722119&&utl=1695130710380&&utc=1695130710380&&pf=333,250"; ule_ck=340958786_1695130710_1695130710385_1695130722123; ule_usession=0893258377710384%7Cylxdfx_merchant_yljf; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aada9ed2c1b2-0c9215c5b4d9b9-48731f21-304500-18aada9ed2d8a4%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWRhOWVkMmMxYjItMGM5MjE1YzViNGQ5YjktNDg3MzFmMjEtMzA0NTAwLTE4YWFkYTllZDJkOGE0In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aada9ed2c1b2-0c9215c5b4d9b9-48731f21-304500-18aada9ed2d8a4%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**157733717; ul_utk="MjNzZjNkd2lvfEFqYkpWdzM3R2VPZUJTNU0wZzhXbXJvSGNHTmFEaFZKdFBVV0FlVjMxeXNHZGNpc2xiSDZ6cnJjSGQzNUhJSnlVZzVZTTJVTEdLNWkxaXRLYnh5ZzEvNU5rc0c4VmpFTVRvTTFuVFlCeUFLcjFGQjBnUHFLZHU1NDBFMmF1bEM0V3ZsVTZTbTBaejM4SjBDYitnWWk1L2ExajNiNjRQd3VCUWs4VDZPeUFYVT18a1RrTSt0TmlwL2o4YWs0aGgwZjMwQlk2UGErdzlvSElKK2NVSFNFU0RGU0J2blRjRFUzWUd6VDRtVk92M2FpTFdvYXpyeUhCK2YvbnhpeTVBYStSd0ZobVlyVVJvYVB4bXlNWSs3WnFOODkvK1ZBL2pSak9sTnNQQ2xsUGtzWVNQRWhDc1pLaVliM2xxeUROVU04OTJBNXFhdnZiNG9RWllHYmdJTi9FdVJ3a25TR2NiUTlUckouLg=="; ul_adid=ylxdfx_merchant_yljf; sajssdk_2015_cross_new_user=1',
    },
    {
        'nick': '竹子130****1415',
        'yshUsrId': '157735032',
        'cookie': 'ul_vtk="uv=0217434094825828&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695130835635&&utl=1695130825829&&utc=1695130825829&&pf=329,255"; ule_ck=425594519_1695130826_1695130825835_1695130835638; ule_usession=0714163525825832%7Cylxdfx_merchant_yljf; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aadabd7fdae3-099574cc3cf661-48731f21-304500-18aadabd7fea2e%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWRhYmQ3ZmRhZTMtMDk5NTc0Y2MzY2Y2NjEtNDg3MzFmMjEtMzA0NTAwLTE4YWFkYWJkN2ZlYTJlIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aadabd7fdae3-099574cc3cf661-48731f21-304500-18aadabd7fea2e%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**157735032; ul_utk="MjNzZjNkd2lvfEhFRGpGYlpTNDYxY0JoQ09oQ0ZsS3NHZWVaYTV3dGd1TTByK0dnQ1RrcWNvQ3Q0ZEl4ZGhIMDZpVy9ST005aDkxUVRSL1RtdGlndC92ZGFmWXZrenJJZ2cxbUFsalg0SGpYTkFQQlp6alk5cis5enRVa3dMZTdrem5KelV5cWp5UlpBT2RQNW5LQisxUS81Rk9uS0dwK2lWS0QyQWVmZ0ZER21xa0pUMjhUUT18UlF0T1NHQ0MxTzRLUHd6S05NSDVMa0Z5UXNERVJkVmowcTc3cXpvd3lTTkpab2tDODhvQTd1a2w4WEdHZ2ErRE1sTlM3clFueDd3eHBZd0lXTGtQSE0wY2VkNXVUMHJqYnlQVzZLUWRreXlkQzV4SjlYWWowVUJnZy91OGtmYUFSQVdYQUxidHowWEFUV2dWZVdqTEJNWHhzQXVObzk5RERSd0lRRjlRdzhFWk1wTU5lbkVIU1cuLg=="; ul_adid=ylxdfx_merchant_yljf',
    },
    {
        'nick': '竹子191****7561',
        'yshUsrId': '147407047',
        'cookie': '_vtk="uv=0398243401941008&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695130957637&&utl=1695130941009&&utc=1695130941009&&pf=335,246"; ule_ck=177245936_1695130941_1695130941014_1695130957643; ule_usession=9512429758941012%7Cylxdfx_merchant_yljf; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aadadac821f6-0c062e36a43489-48731f21-304500-18aadadac83a00%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWRhZGFjODIxZjYtMGMwNjJlMzZhNDM0ODktNDg3MzFmMjEtMzA0NTAwLTE4YWFkYWRhYzgzYTAwIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aadadac821f6-0c062e36a43489-48731f21-304500-18aadadac83a00%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**147407047; ul_utk="MjNzZjNkd2lvfFJtZHlaUXpFYWllNHRoblR4empSRHBVTzJQSkNCWTNvdnZrV2VXVHZUTXNlQU5QeW84d0k4L1VXTFVyK2p5eUc1Z2VXSzF5ZEpqeFRCVjZoWEVLcHpSUVJyeHRqRmphWElhUVNISzBtVUgveGttRmQ4VWpwZDJQMG1TWG41ZGREOFZFRk96Q0RndDFmNStOZkVRVkFLelpjSFRnbnJJR003c1A0ZlgvY1BqUT18VmtqYkJjTmZkemQ5MjRnM2VJd1FGNnRBNkVDSmpWSmF2SXlaaGp2YnMyLy9YWWwwYkpzVDlZaWs3Y0YwSGNYTXZWRmVDZ0pFRTRhbXZkc0dRUEppWEZRL1Y4U1pYdTJSQXFjb0RMekVVU1pYY01yZ1Nqek8ybnAxTkpPV0tvRVg2Mm55Q3VqcWJkNld0UzNwYnF5Rm1ndnBMZ0Q4MEhBV2hTa2x5UFRnOUt6d1ZGRnlPVmhPU1IuLg=="; ul_adid=ylxdfx_merchant_yljf',
    },
    {
        'nick': '竹子155****0038',
        'yshUsrId': '202636486',
        'cookie': 'ul_vtk="uv=0154042820030640&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695131042870&&utl=1695131030642&&utc=1695131030642&&pf=323,249"; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aadaf02177d7-030f07a7c97fc12-48731f21-304500-18aadaf02189bb%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWRhZjAyMTc3ZDctMDMwZjA3YTdjOTdmYzEyLTQ4NzMxZjIxLTMwNDUwMC0xOGFhZGFmMDIxODliYiJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aadaf02177d7-030f07a7c97fc12-48731f21-304500-18aadaf02189bb%22%7D; ule_ck=827942341_1695131031_1695131030648_1695131042874; ule_usession=7181951480030644%7Cylxdfx_merchant_yljf; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**202636486; ul_utk="MjNzZjNkd2lvfENVM1UvS20zSkw3aVBBbkR4aUp6YXR4bG9qTkxwcWtheFBXU29Cak1aNEdCVDh1OUhlcG81SXgyNVhXQzdWN1RrRk1JT1JwSndVUU9hWGpGN2tET2RYYUkyamZ4ZHFQNU9wZ1o0Ty9yYUd3elJzSWxPZU5HY1lxS2pwOFZ0dnJFWklIV0FjN1RrS05JR0taRXlaUERQaEZjNnZyNFdCQktkTkk2aHluOFgzMD18ZzJ5R01zZFJyeHI0RERSK0xSdnR3OTArNnRQbWRUVE5CVWpNc0JHUENGQ0FjM0VhcmFDR211bG1NN1V2LzlyQmpKOTZYQzVxM3QxQmMxY3lIbFEwWEpzUEUycTRqUHJjMmg3R2pLK3M4aENVemFlaFVIZUlhOTRuV2RoR0FXb0FkeitkaWVjYnZBTTl6emorWWZTK2J0WUtYN3FvOXpwb0lTZlVWTU9GYTVBQ0V6aXZ0M2QrSkouLg=="; ul_adid=ylxdfx_merchant_yljf',
    },
    {
        'nick': '166****5707',
        'yshUsrId': '147670341',
        'cookie': 'ul_vtk="uv=7692718589163492&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695131175489&&utl=1695131163495&&utc=1695131163495&&pf=325,246"; ule_ck=874333998_1695131164_1695131163501_1695131175493; ule_usession=0874036790163500%7Cylxdfx_merchant_yljf; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aadb0cf503c1-0aa8b33c3099f38-48731f21-304500-18aadb0cf512c9%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWRiMGNmNTAzYzEtMGFhOGIzM2MzMDk5ZjM4LTQ4NzMxZjIxLTMwNDUwMC0xOGFhZGIwY2Y1MTJjOSJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aadb0cf503c1-0aa8b33c3099f38-48731f21-304500-18aadb0cf512c9%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**147670341; ul_utk="MjNzZjNkd2lvfG1ab0thelRpdFpNdU4rWE1Ca1lXRzB5NjR0cUN2byt4eUoySlBHV0xiVldJNHdkaEJRakVXVS8yRFd4Q2RJbTl3b3U0Tnlnd0RPeTRyOVRoWHA3cFBwRDNILzlDZG9xVkZEb1dYMnBkQTJUOWR0MGJRT3VMc1lONHBNQXJQc3lsVjVjdEtQM3VnMERMdERVdXhlSFJqUmRBL2NUNTZtYVB6Vk4vMzZBUzUrTT18WUk1VGsyV0JnYXVJb2l2QmEzUWYwNWRkaHFkM25BUC9TUGlkODJDYVA0RnVFUDJlRDNpcUZkenpIdXJURHd6WjlTYk5kN1pxc3FnaVVwdU82RzFEeFFva1ZkRUpYY3lGQW9qa3NSUzBIRjR2VERjRjlJY1dSSFdiMFJ0N2hhZXdmSS9NQS90WDRiT0doajBpOVd4dmlFbGY1VmRVKzd1R1l2U3pYdmF4UHBkL3FRSjViYlJiVUEuLg=="; ul_adid=ylxdfx_merchant_yljf; sajssdk_2015_cross_new_user=1',
    },
    {
        'nick': '竹子153****9901',
        'yshUsrId': '157439421',
        'cookie': 'ul_vtk="uv=0837309428246524&&pv=79c294015025c9f02ec966cf9e161c65&&utn=1695131259746&&utl=1695131246524&&utc=1695131246524&&pf=328,244"; ule_ck=912487900_1695131260_1695131259751_1695131259751; ule_usession=0960122492259748%7Cref_aHR0cHM6Ly95b3VzaGVuZ2h1by4xMTE4NS5jbg; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aadb24c5b78e-01e06522c3f35ba-48731f21-304500-18aadb24c5c9dc%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E5%BC%95%E8%8D%90%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fyoushenghuo.11185.cn%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWRiMjRjNWI3OGUtMDFlMDY1MjJjM2YzNWJhLTQ4NzMxZjIxLTMwNDUwMC0xOGFhZGIyNGM1YzlkYyJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aadb24c5b78e-01e06522c3f35ba-48731f21-304500-18aadb24c5c9dc%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%3F%3FTAB-%3F%3F; ul_union=1016039307**157439421; ul_utk="MjNzZjNkd2lvfGtuQjFvTTd1aTJhKzZJT3krVHRrSytYQkNlY3Z0R2FkcDMxelZPT3NaWE1SVnFsTGFMYVZvRzZ0dGlaZVVPOGw3c3hiWTA1ZTJZSzU5SlFqcmJrWkJ1S0VUdzR2c1FHRWVxUURXbGJzTDdkeU5VM3lXcmh4VkxCZnNRVHJScWhhNjZiN242bDFXZGZkK3dmSmo3UnNpeFpaaWpxZk9tMG9KTTRzYXI3bWtXaz18WHRyZTJnWTZ5RXhlOTlwczVQVVdyckgzNUQwR3pzaXExYm56TXNjWnlYa1NTL3ppb2V4UHBuYUdxT0NyK2I4b2VyMis4M3VDSDRiNm5WUUFlaFNGaEMvLzExTWFueHpsR0FDVVVTUFhhUE1aWU5LTllvdXVLY2pReFYzQmE4dWkyTm4wS25oRkJJVGQ2SzlvM1d2Z0EyVkgzKzJ0VC9rWGhIUW85QWdVNWw2VHg2QVJyWkIwQ0ouLg=="; ul_wmid=oSwO04lMbEsy4SMILroA3qc3h0wo',
    },
    {
        'nick': '180****0050',
        'yshUsrId': '147656033',
        'cookie': 'ul_vtk="uv=0549986496550816&&pv=f9e52c839b91de2194349bbb70d0c46f&&utn=1695131332554&&utl=1695120653663&&utc=1695120550818&&pf=333,242"; ul_adid=ylxdfx_merchant_yljf; ule_ck=669175541_1695120550_1695120653660_1695131332561; ule_usession=7460716769332558%7Cylxdfx_merchant_yljf; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218aad0eeafa747-043c0ca4587e6b8-48731f21-304500-18aad0eeafb644%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhYWQwZWVhZmE3NDctMDQzYzBjYTQ1ODdlNmI4LTQ4NzMxZjIxLTMwNDUwMC0xOGFhZDBlZWFmYjY0NCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218aad0eeafa747-043c0ca4587e6b8-48731f21-304500-18aad0eeafb644%22%7D; ul_acturl=https%3A%2F%2Fh5.ule.com%2Fbroadcast%2FbroadLive%2F11765%2F204834%3Ful_aid%3Duxdhome_%25E5%25BA%2595%25E9%2583%25A8TAB-%25E7%259B%25B4%25E6%2592%25AD%26storeid%3D1094524589%26shareId%3D496515317%26appName%3Dylxd%26adid%3Dylxdfx_merchant_yljf%26statistics%3DWX; sajssdk_2015_cross_new_user=1; ul_utk="MjNzZjNkd2lvfFdVOGtpT0lxZXZuK2dpeS9BazN0a3RENVI2eFVRODhZZi85cFBHblVOM3NyZkdHMFg3ckdYSnpHZCs1cmRCRm5adEI1R0h6QkFnTHUwMFY2MHBiNFpqMlVEL0k3REdoTlZkV01WT203MjhzYmJabFlsSlgrdDkrdm1RelV0ckIvR29ZWWsvQUlCYWtnMUJQZVFSd01ZTWY3TzZ0WVdvU0k2SU93TzY5b0pHWT18R3hGN2VlQXllOFFtajFMaUoxS2FyZDBBblZPUldEbEY4ejlVcUIwS1FYa2Jka3ZjV1hvc29vVHlhNlZjajBueEJlU3crZ3VTSENydGRTZnEvUm5FZjI3U0xCQkZjN2hvV3M5RlFGeUV5UXdHS2l1NXpmbXZBb0wvL3paSmNsUitTU2FJMEM4RmtHd3JCaUtwMDhUU08vRFZXYkRZMVdtMk00Q20rZHQ4cjFuaTMvUWVLTUY3VkouLg=="',
    },
]

DATE_FORMAT = "%Y-%m-%d %H:%M:%S "
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(message)s',  # 定义输出log的格式
                    stream=sys.stdout,
                    datefmt=DATE_FORMAT)
header_context = f'''
Connection: keep-alive
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1
Accept: application/json, text/plain, */*
Sec-Fetch-Site: same-site
Sec-Fetch-Mode: no-cors
Sec-Fetch-Dest: script
Referer: https://h5.ule.com/
Accept-Encoding: deflate, br
Accept-Language: zh-CN,zh;q=0.9
Content-Type: application/x-www-form-urlencoded
'''
headers = {}
for k in header_context.rstrip().lstrip().split("\n"):
    temp_l = k.split(': ')
    dict.update(headers, {temp_l[0]: temp_l[1]})


def getLiveRoom():
    roomNumbers = []
    url = f"https://pub.ule.com/live/tv/yxAndLsBoFangRooms?tvType=5"
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'pub.ule.com',
        'Referer': 'https://www.ule.com/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Mi 10 Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5197 MMWEBSDK/20230701 MMWEBID/4846 MicroMessenger/8.0.40.2420(0x2800283B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Dest': 'script',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua': ''
    }

    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        response = response.json()
    else:
        return
    roomeData = response['data']
    for data in roomeData:
        title = data['title']
        tvStatus = data['tvStatus']
        sceneType = data['sceneType']  # 2回放
        roomNumber = data['roomNumber']
        if sceneType == 2 and tvStatus == 0:
            logging.debug(f'当前直播间:{title} {roomNumber}, 状态: 待开播')
        elif sceneType == 1 and tvStatus == 0:
            logging.debug(f'当前直播间:{title} {roomNumber}, 状态: 待开播')
        elif sceneType == 2 and tvStatus == 1:
            logging.debug(f'当前直播间:{title} {roomNumber}, 状态: 回放中')
        elif sceneType == 1 and tvStatus == 1:
            logging.info(f'当前直播间:{title} {roomNumber} , 状态: 已开播 √√√')
            roomNumbers.append(roomNumber)
        else:
            logging.info(f'当前直播间:{title} {roomNumber}, 状态: sceneType {sceneType}  tvStatus {tvStatus}\n')
    print("")
    logging.info(f'当前开播的直播间:{roomNumbers}')
    return roomNumbers


def getPrizeId(roomId):
    n_time = int(time.time())
    headers = {
        'authority': 'ustatic.ulecdn.com',
        'method': 'GET',
        'scheme': 'https',
        'Accept': '*application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://h5.ule.com/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Mi 10 Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5197 MMWEBSDK/20230701 MMWEBID/4846 MicroMessenger/8.0.40.2420(0x2800283B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Dest': 'script',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua': '',
        # 'content-type': 'application/javascript;charset=UTF-8'

    }
    url = f"https://ustatic.ulecdn.com/ulelivebarrage/api/v1/room/static/refresh/{roomId}/{n_time}"

    response = requests.get(url=url, headers=headers)
    text = response.text
    # print(response.text)
    response = response.json()
    blessing_bag_info = response['data']['blessing_bag_info']
    if blessing_bag_info:
        blessing_bag_setting = blessing_bag_info['blessing_bag_setting']
        if blessing_bag_setting:
            print("")

            lucky_name = blessing_bag_setting['lucky_name']
            coupon_remark = blessing_bag_setting['coupon_remark']
            start_time = blessing_bag_setting['start_time']
            end_time = blessing_bag_setting['end_time']
            key = blessing_bag_setting['key']
            status = blessing_bag_setting['status']
            winners = blessing_bag_setting['winners']
            if blessing_bag_setting['winners']:
                logging.info(
                    f'{roomId} {lucky_name} 福袋抽奖关键字:{key} ,status {status}, 开始时间: {start_time},结束时间: {end_time}')
                logging.info(f'{roomId} 当前福袋抽奖已结束')

                logging.info(winners)
                format_pattern = "%Y-%m-%d %H:%M:%S"
                now_time = datetime.datetime.now().strftime(format_pattern)
                difference = (
                        datetime.datetime.strptime(now_time, format_pattern) - datetime.datetime.strptime(end_time,
                                                                                                          format_pattern))
                if difference.seconds < (range_time + 10):
                    logging.info(f'{roomId} 查询福袋中奖记录...')
                    for winner in winners:
                        if winner in nick_list:
                            print(winner,
                                  f"中奖啦===========================================\n直播间 {roomId}",
                                  lucky_name)
                            send(title=f"邮生活福袋抽奖",
                                 content=f"{winner}\n\n中奖啦====================\n直播间{roomId} \n{blessing_bag_setting}")

            else:
                content = parse.quote(key.encode('utf-8'))
                logging.info(
                    f'{roomId} {lucky_name} {coupon_remark} -- 福袋抽奖关键字:{key} , status {status}, 开始时间: {start_time},结束时间: {end_time}')
                pinglinu(roomId, content)
    luck_v2 = response['data']['luck_v2']
    if luck_v2:
        id = luck_v2['id']
        status = luck_v2['status']
        winners = luck_v2['winners']
        key = luck_v2['key']
        start_time = luck_v2['start_time']
        end_time = luck_v2['end_time']
        content = parse.quote(key.encode('utf-8'))
        print("")
        logging.info(f'{roomId} 互动抽奖关键字:{key} ,status {status}, 开始时间: {start_time},结束时间: {end_time}')
        # if len(winners) > 0 or end_time is not None:
        if status == '3':
            # status 2
            logging.info(f'{roomId} 当前关键字抽奖已结束')
            logging.info(winners)
        else:
            logging.info(f'开始关键字抽奖:{key} , roomId {roomId}')
            pinglinu(roomId, content)

        # 查询中奖
        if end_time:
            format_pattern = "%Y-%m-%d %H:%M:%S"
            now_time = datetime.datetime.now().strftime(format_pattern)
            difference = (datetime.datetime.strptime(now_time, format_pattern) - datetime.datetime.strptime(end_time,
                                                                                                            format_pattern))
            if difference.seconds < (range_time + 10):
                luck(id, roomId)


# 关键字抽奖中奖查询
def luck(id, roomId):
    n_time = int(time.time())

    url = f"https://pub.ule.com/ulelivebarrage/api/v1/room/luck/user/{roomId}/338555375/luck?t={n_time}&jsonp=luck&jsonpcallback=luck&luck=luck"
    for authorization in authorization_list:
        dict.update(headers, {"cookie": authorization['cookie']})
        dict.update(headers, {"Accept": "application/json, text/plain, */*"})

        response = requests.get(url=url, headers=headers).text
        response = response.replace('luck({', '{')
        response = response.replace('}})', '}}')
        response = json.loads(response)

        lucks = response['data']['lucks']
        for luck in lucks:
            if luck['flag'] == '1':
                end_time = luck['end_time']
                format_pattern = "%Y-%m-%d %H:%M:%S"
                now_time = datetime.datetime.now().strftime(format_pattern)
                difference = (
                        datetime.datetime.strptime(now_time, format_pattern) - datetime.datetime.strptime(end_time,
                                                                                                          format_pattern))
                if difference.seconds < (range_time + 10):
                    print(authorization['nick'],
                          f"中奖啦===========================================\nhttps://h5.ule.com/broadcast/broadLive/{id}/{roomId}?ul_aid=ulehome_%E9%82%AE%E4%B9%90%E7%9B%B4%E6%92%AD_8",
                          luck)
                    send(title=f"邮生活弹幕抽奖",
                         content=f"{authorization['nick']}\n\n中奖啦====================\nhttps://h5.ule.com/broadcast/broadLive/{id}/{roomId}?ul_aid=ulehome_%E9%82%AE%E4%B9%90%E7%9B%B4%E6%92%AD_8 \n{luck}")

        time.sleep(time_sleep)


def getSign():
    appId = "10020"
    secret = "b82a976aebe35eb4"
    timestamp = int(time.time() * 1000)
    # timestamp = "1692356065726"
    m = appId + secret + str(timestamp)
    sign = hashlib.md5(m.encode()).hexdigest()
    signData = "&appId=" + appId + "&timestamp=" + str(timestamp) + "&sign=" + sign
    # print(signData)
    return signData


# 评论抽奖
def pinglinu(room_name, content):
    for authorization in authorization_list:
        url = "https://pub.ule.com/ulelivebarrage/api/v1/barrage/submit?" + getSign()
        dict.update(headers, {"cookie": authorization['cookie']})
        dict.update(headers, {"Accept": "application/json;_p=mall;_c=yzs;"})
        data = f"room_name={room_name}&content={content}"
        response = requests.post(url=url, data=data, headers=headers).json()
        print(authorization['nick'], response)


if __name__ == '__main__':
    nick_list =[]
    for authorization in authorization_list:
        nick_list.append(authorization['nick'])
    roomIds = getLiveRoom()
    for roomId in roomIds:
        try:
            getPrizeId(roomId)
            time.sleep(time_sleep)
            print(roomId, "------------------------------------------------------------------------------------")
        except Exception as e:
            logging.info(f'{roomId} 异常了----- {e}')
    print("")
    logging.info(f'完毕，等待下一轮')

