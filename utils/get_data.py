import requests
import simplejson

# 创建一个session连接对象
session = requests.Session()
# base_url = 'https://zuihuimai.net/vrhr/index_jd_new.php?goods_id=100020062335'
# base_url = 'https://item.jd.com/100035225784.html'


class GetData(object):
    def __init__(self, asin):
        super(GetData, self).__init__()
        self.asin = asin

    def get_origin_data(self):
        # 1 拼接完整的url
        title_url = 'https://item.jd.com/{}.html'.format(self.asin)
        price_url = 'https://item-soa.jd.com/getWareBusiness?callback=jQuery5728754&skuId={}&cat=9987%2C653%2C655&' \
                    'area=1_2802_54745_0&shopId=1000004123&venderId=1000004123&paramJson=%7B%22platform2%22%3A%22100000000001%' \
                    '22%2C%22specialAttrStr%22%3A%22p0ppppppppp2p1p1ppppppppppp%22%2C%22skuMarkStr%22%3A%2200%22%7D&num=1'.format(self.asin)
        # 2 发送请求
        # 3 解析数据，拿到标题，价格
        resp = session.get(title_url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62'})
        connect = resp.text
        start_index = connect.index('<title>')
        end_index = connect.index('</title>')
        title = connect[start_index+7:end_index]
        # print(title)
        resp = session.get(price_url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62'})
        connect = resp.text
        # print(connect)
        start_index = connect.index('(') + 1
        # end_index = connect.
        # print(connect[start_index:len(connect)-1])
        price_json = simplejson.loads(connect[start_index:len(connect)-1])
        # print(price_json['price']['p'])
        # print(price_json)
        # return title, '2299', title_url
        return title, price_json['price']['p'], title_url

if __name__ == '__main__':
    data = GetData('aaa')
    data.get_origin_data()