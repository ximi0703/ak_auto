# gmTestPlc
python操作下位机PLC（基恩士）

python操作云台（HY-LW18-02B）

python操作双目相机（大恒）测距

![485521c124acb1306958bffd8e96e40](https://user-images.githubusercontent.com/43095279/157668074-d3c9e405-ce1f-4276-b21b-d6e68c0396f7.jpg)
![20b1798859716dac466a99b45ea0e03](https://user-images.githubusercontent.com/43095279/157668097-2478c729-955d-44e4-8670-f81fc69746b1.jpg)
![09e658f6bf9b7ea753c95bf7db17c13](https://user-images.githubusercontent.com/43095279/157668108-69fe59f2-2334-4d0e-8df4-1aec27586ead.jpg)
![f1556de1b38cfe1aae7c58fbcf63358](https://user-images.githubusercontent.com/43095279/157668125-efd33c9d-6641-404d-b4d9-57a6386772f9.jpg)
![5bb5a20b05db67be41f11d2a62731f4](https://user-images.githubusercontent.com/43095279/157668149-c21e46dc-3912-4b97-a293-957655743835.jpg)
![473c643b5051d6e9306a78f09e4a42b](https://user-images.githubusercontent.com/43095279/157668159-36c2a1d6-dc12-4733-b913-aa23e57d4d8b.jpg)


一、背景
1.	需求来源
由于目前AK精度测试和AF精度测试都是需要大量人工测试，人工测试存在误差（卷尺、角度以及人为误差）；并且会耗费大量人力时间
二、功能描述
1. 搭配滑轨、云台，可实现不同投影尺寸和不同侧投角度（高精度）；
2. 搭配双摄工具，可实现摄像头拍照识别投影面的长宽及对角线，计算出次投影面的精度（高精度、高效率）；
3. 搭配AF可靠性工具和摄像头，可实现摄像头拍照识别此次对焦的精度、清晰度（高精度、高效率）
三、设计方案
4. 总体架构采用三层架构设计模式：接口封装层、业务封装层、用户行为层
4.1 接口封装层：主要实现底层接口封装、通信
4.1.1 Frame（云台控制）
4.1.1.1 通信方式
通过UDP（6666）端口，使用标准Pelco-D协议通信。
4.1.1.2 接口
接口名	功能	参数	返回值
Frame类	封装标准Pelco-D命令格式	默认参数：
Ip地址、端口号、云台地址	
_checksum	获取crc检验码	字节1到字节5值	None
send_command	向云台下发命令	command2：命令指令
data1：数据1
data2：数据2	返回命令回显16进制

4.1.2 TrackControl(轨道控制)
4.1.2.1 通信方式
通过Qna兼容3E帧协议实现（二进制通讯，套接字实现）。
4.1.2.2 接口
主要实现接口为：X轴、Y轴定向移动和归位、移动到指定位置、自检等功能接口。
接口名BasicConnect类	功能	参数	返回值
connect_plc()	实现连接PLC滑轨，进行通信	None，使用BasicConnect类变量	plc_server通讯对象，包含read、write、readBool、writeBool等接口
protect_safe()	打开安全光栅保护，默认为关闭状态	None，plc_server通讯对象	返回安全光栅当前状态bool值


is_high_speed()	打开高速运行（只针对手动控制，不针对定位运行），默认低速为15.6mm/s，高速默认为上一次设置	None，plc_server通讯对象	返回当前状态bool值
X、Yoperation类	继承BasicConnect类，并且默认打开高速模式		
set_forward	实现前进，下发命令之后会一直前进，知道到最大位置处	None，plc_server通讯对象	返回当前状态bool值
set_back	实现后退，下发命令之后会一直后退，知道到最小位置处	None，plc_server通讯对象	返回当前状态bool值
stop	停止运行	None，plc_server通讯对象	返回当前状态bool值
reset	回到原点处	None，plc_server通讯对象	返回当前状态bool值
is_reseted	回零完成	None，plc_server通讯对象	返回当前状态bool值
in_alarm	告警中	None，plc_server通讯对象	返回当前状态bool值
clear_alarm	清除告警，只有当走到最大或者最小位置后，还继续走，会有告警，不清除告警，无法进行下一步操作	None，plc_server通讯对象	返回当前状态bool值
get_cur_location	查询当前所在位置	None，plc_server通讯对象	返回当前位置，int类型
set_location	设置目标位置	目标位置值, 范围-60~3495	返回设置位置值
set_speed	设置目标速度	目标速度， 范围0~200	返回设置速度值
running	定位运行，需要先设置目标位置，和运行速度，才能触发定位运行	None，plc_server通讯对象	返回当前状态bool值
in_running	定位中（运行中）	None，plc_server通讯对象	返回当前状态bool值
is_finish_running	完成定位，运行完成	None，plc_server通讯对象	返回当前状态bool值
get_high_speed	获取当前高速速度	None，plc_server通讯对象	返回当前速度值
set_high_speed	设置当前高速速度	高速速度， 范围0~150	返回设置速度值


4.1.3 ProjectControl(投影控制)
4.1.3.1 通信方式
通过串口或者adb实现通信。
4.1.3.2 接口
主要实现接口为：调用AK，调用AF，AK、AF存图文件、STR开机AK、AF，重启AK、AF、抓取指定日志等接口。
4.2 业务封装层：主要实现一些基本功能的封装
4.2.1 PTZControl（云台控制）
PTZControl类	封装云端一些功能接口	Frame类的实例化对象	
stop_run	停止云台转动		
reset	云台归位		
query_cur_angle	查询当前位置	默认参数：axis水平轴	返回int当前角度
turn_to_angle	转动云台至某个角度	默认参数：
Axis：水平轴
Angle：角度15°	True or False
4.2.2 TrackControl(轨道控制)
接口名	功能	参数	返回值
TrackControl类	实现滑轨业务层接口封装		
move_to ()	移动滑轨至指定位置，默认从原点出发	*args:  x -> int, y -> int, 
speed -> int,默认150
direction -> str，默认+方向	
reset	实现默认回到原点		
check_length	校验参数长度合法性	*args:  x -> int, y -> int, 
speed -> int,默认150
direction -> str，默认+方向	x_move,  x轴移动距离
y_move,  y轴移动距离
 speed   移动速度
check_type	校验参数类型合法性	*args:  x -> int, y -> int, 
speed -> int,默认150
direction -> str，默认+方向	x_move,  x轴移动距离
y_move,  y轴移动距离
 speed   移动速度
check_value	校验参数值合法性	*args:  x -> int, y -> int, 
speed -> int,默认150
direction -> str，默认+方向	x_move,  x轴移动距离
y_move,  y轴移动距离
 speed   移动速度
init_parmas	校验参数	*args:  x -> int, y -> int, 
speed -> int,默认150
direction -> str，默认+方向	x_move,  x轴移动距离
y_move,  y轴移动距离
 speed   移动速度


ProjectControl(投影控制)
XXX
5. 设计方法
5.1 思路
目前我们可以通过代码控制滑轨、云台设备、投影仪以及双摄工具。
初步思路就是，先实现单个尺寸测试AK精度；具体思路如下：
1.	先通过控制滑轨走到指定的尺寸
2.	通过云台旋转指定角度
3.	通过控制投影做一次AK
4.	通过控制双摄工具进行拍图计算
5.	得出计算结果，导入到excel或者数据库中
5.2 方法
通过业务层封装的接口，调用需要的接口实现
5.3 算法
 
1．	指定距离换算为尺寸：滑轨四边到投影面距离，滑轨总距离，再通过投影尺寸相减得出需要移动的距离
2．	滑轨运行时间计算：通过获取滑轨当前位置和目标位置之间的距离差，再除以相应的速度（自己设定）
3．	云台当前角度：通过命令可以直接回显云台当前水平方向和垂直方向的角度，但是需要换算
4．	云台旋转等待时间：通过获取当前角度和目标角度，再除以角速度，可获取最大时间


5.4 流程
由接口封装层的一些底层接口，可以控制滑轨、云台、投影仪、双摄工具。
 
6. 参数指标
1．	滑轨的IP和端口
2．	云台的IP和端口
3．	投影仪的串口端口
7. 效率对比
按照目前AK测试精度表格，需要两台机器三个尺寸，平均9个角度，人工成本大约是（2*40*60+10*60）*2= 18000s；自动化工具：
	轨道：
80寸： 4450 – 2120 = 2330 /150 = 15+2 = 17s
100寸：4450 – 2660 = 1790 /150 = 12+2 = 14s
120寸：4450 – 3170 = 1280/150 = 9+2 =11s
总计17+17+14+14+11 = 73s
	云台：
		90s
	设备：
		20s
总计：127+141+135 = 403s

18000 / 403 = 45倍


四、开发计划
事项	责任人	完成时间
云台控制底层接口封装	
轨道控制底层接口封装	
云台控制业务层功能接口封装	
轨道控制业务层功能接口封装
投影仪设备控制底层接口、业务层功能接口封装	
AK双摄工具dll库接口封装	
AF精度、可靠性测试工具接口封装	

五、问题和风险
1.	问题及风险
1.1	目前双摄工具状态不太清楚研发端的情况（更换过一次摄像头），更换摄像头之前是可以通过调用dll库实现拍图计算的
1.2	AF工具需要研发端支持，由于之前的工具是apk方式，现在需要更改下算法流程以及封装为我们可用的dll库的方式并且输出接口文档

2.	对策
需要研发端协助一起解决
六、参考文件及附件
（参考文件、相关数据资料附件）
    
