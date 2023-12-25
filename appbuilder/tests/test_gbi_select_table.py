"""
Copyright (c) 2023 Baidu, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import unittest
import os
import appbuilder
from appbuilder.core.message import Message
from appbuilder.core.components.gbi.basic import GBILocalSession


SUPER_MARKET_SCHEMA = """
```
CREATE TABLE `超市营收明细` (
  `订单编号` varchar(32) DEFAULT NULL,
  `订单日期` date DEFAULT NULL,
  `邮寄方式` varchar(32) DEFAULT NULL,
  `地区` varchar(32) DEFAULT NULL,
  `省份` varchar(32) DEFAULT NULL,
  `客户类型` varchar(32) DEFAULT NULL,
  `客户名称` varchar(32) DEFAULT NULL,
  `商品类别` varchar(32) DEFAULT NULL,
  `制造商` varchar(32) DEFAULT NULL,
  `商品名称` varchar(32) DEFAULT NULL,
  `数量` int(11) DEFAULT NULL,
  `销售额` int(11) DEFAULT NULL,
  `利润` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
```
"""

PRODUCT_SALES_INFO = """
现有 mysql 表 product_sales_info, 
该表的用途是: 产品收入表
```
CREATE TABLE `product_sales_info` (
  `年` int,
  `月` int,
  `产品名称` varchar,
  `收入` decimal,
  `非交付成本` decimal,
  `含交付毛利` decimal
)
```
"""

os.environ["APPBUILDER_TOKEN"] = "bce-v3/ALTAK-tpJqnbAvTivWEAclPibrT/4ac0ef025903f00e9252a0c41b803b41372a4862"
# os.environ["GATEWAY_URL"] = "http://127.0.0.1:8919"
os.environ["GATEWAY_URL"] = "http://10.216.119.167:8919"


class TestGBISelectTable(unittest.TestCase):

    def setUp(self):
        """
        设置环境变量及必要数据。
        """
        model_name = "ERNIE-Bot 4.0"

        self.select_table_node = \
            appbuilder.GBISelectTable(model_name=model_name,
                                      table_descriptions={"超市营收明细": "超市营收明细表，包含超市各种信息等",
                                                          "product_sales_info": "产品销售表"})

    def test_run_with_default_param(self):
        """测试 run 方法使用有效参数"""
        query = "列出超市中的所有数据"
        msg = Message(query)
        session = GBILocalSession(session_id="1")
        result_message = self.select_table_node(message=msg, session=session)
        print(result_message.content)
        self.assertIsNotNone(result_message)
        self.assertEqual(len(result_message.content), 1)
        self.assertEqual(result_message.content[0], "超市营收明细表")

    def test_run_with_prompt_template(self):
        """测试 run 方法使用有效参数"""
        query = "列出超市中的所有数据"
        msg = Message(query)
        session = GBILocalSession(session_id="1")
        result_message = self.select_table_node(message=msg, session=session)
        self.assertIsNotNone(result_message)
        self.assertEqual(len(result_message.content), 1)
        self.assertEqual(result_message.content[0], "超市营收明细表")


if __name__ == '__main__':
    unittest.main()
