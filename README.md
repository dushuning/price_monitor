# price_monitor
一个使用pyqt编写的价格监控小程序，作为自己学习的锻炼，欢迎各位来讨论交流

打包命令：pyinstaller -w -F main.py -i utils\head.ico

使用说明：
1.如果需要邮件报警功能，那么请先配置窗口上的邮件报警配置，需要发件人，收件人，以及发件人的密钥和1服务器地址
2. 接下来就是添加数据，需要在窗口的添加哪一行添加需要监控的商品的序号，这个序号可以自己从网上找，然后把序号和价格按实列的要求添加，然后点击添加按钮即可
3. 点击开始按钮即可，然后程序会自动监控，如果最新的价格小于设置的底价，那么就会收到邮件报警邮件
