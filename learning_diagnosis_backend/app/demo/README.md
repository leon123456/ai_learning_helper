# 题目识别完整工程示例

该项目为RecognizeEduQuestionOcr的完整工程示例。

该示例**无法在线调试**，如需调试可下载到本地后替换 [AK](https://usercenter.console.aliyun.com/#/manage/ak) 以及参数后进行调试。

## 运行条件

- 下载并解压需要语言的代码;


- 在阿里云帐户中获取您的 [凭证](https://usercenter.console.aliyun.com/#/manage/ak) 并通过它替换下载后代码中的 ACCESS_KEY_ID 以及 ACCESS_KEY_SECRET;

- 执行对应语言的构建及运行语句

## 执行步骤

下载的代码包，在根据自己需要更改代码中的参数和 AK 以后，可以在**解压代码所在目录下**按如下的步骤执行：

- *Python 版本要求 Python3*
```sh
python3 setup.py install && python ./alibabacloud_sample/sample.py
```
## 使用的 API

-  RecognizeEduQuestionOcr：可对题目进行有效识别。通过对题目的元素进行打标，提升题目的识别效果。 更多信息可参考：[文档](https://next.api.aliyun.com/document/ocr-api/2021-07-07/RecognizeEduQuestionOcr)

## API 返回示例

*实际输出结构可能稍有不同，属于正常返回；下列输出值仅作为参考，以实际调用为准*


- JSON 格式 
```js
{
  "RequestId": "43A29C77-405E-4CC0-BC55-EE694AD00655",
  "Data": "{\n      \"content\": \"√技能提升练 √拓展创新练 12.对于同一平面内的三条直线，给出下列5个论断：15.「2018春·如皋期末]在一个三角形中,如果一个角 ①a//b;②b∥c;③a⊥b;④a∥c;⑤a⊥c ,以其中两是另一个角的3倍,这样的三角形我们称之为“智个论断为条件,一个论断为结论,组成一个你认为慧三角形”.如三个内角分别为 1 2 0 ^ { \\\\circ } , 4 0 ^ { \\\\circ } , 2 0 ^ { \\\\circ } 的三角正确的命题. 形是“智慧三角形”. 已知:,结论: 如图 1 - 2 - 2 , \\\\angle M O N = 6 0 ^ { \\\\circ } , 在射线OM上找一点 13.指出命题“同旁内角互补”的条件和结论,并说明这 A,过点A作 AB⊥OM 交ON于点B,以A为端点个命题是正确的命题还是错误的命题. 作射线AD 交射线OB于点C(点C不与点O重合). M A B N 图 1- -2一2 14.如图 1-2-1, 点B,A,E在同一条直线上,已知①AD (1) ∠ABC 的度数为°, △AOB ∥BC,②∠B=∠C,③AD 平分 ∠EAC. 请你用其中两(填“是”或“不是”)智慧三角形; 个作为条件,另一个作为结论,构造命题,并说明你构 (2)若 \\\\angle O A C = 2 0 ^ { \\\\circ } ，试说明:：△AOC 为\"智慧三角形的命题是正确的命题还是错误的命题. 形”; E D B C 图 1-2-1 (3)当 △ABC 为“智慧三角形”时,求 ∠OAC 的度数. 第1章三角形的初步知识A5 \",\n      \"figure\": [\n            {\n                  \"type\": \"subject_pattern\",\n                  \"x\": 1605,\n                  \"y\": 3087,\n                  \"w\": 645,\n                  \"h\": 804,\n                  \"box\": {\n                        \"x\": 0,\n                        \"y\": 0,\n                        \"w\": 0,\n                        \"h\": 0,\n                        \"angle\": 0\n                  },\n                  \"points\": [\n                        {\n                              \"x\": 1605,\n                              \"y\": 3087\n                        },\n                        {\n                              \"x\": 2250,\n                              \"y\": 3087\n                        },\n                        {\n                              \"x\": 2250,\n                              \"y\": 3891\n                        },\n                        {\n                              \"x\": 1605,\n                              \"y\": 3891\n                        }\n                  ]\n            }\n      ],\n      \"height\": 7000,\n      \"orgHeight\": 7000,\n      \"orgWidth\": 4716,\n      \"prism_version\": \"1.0.9\",\n      \"prism_wnum\": 64,\n      \"prism_wordsInfo\": [\n            {\n                  \"angle\": 0,\n                  \"direction\": 0,\n                  \"height\": 85,\n                  \"pos\": [\n                        {\n                              \"x\": 207,\n                              \"y\": 508\n                        },\n                        {\n                              \"x\": 826,\n                              \"y\": 506\n                        },\n                        {\n                              \"x\": 826,\n                              \"y\": 592\n                        },\n                        {\n                              \"x\": 208,\n                              \"y\": 594\n                        }\n                  ],\n                  \"prob\": 96,\n                  \"recClassify\": 0,\n                  \"width\": 618,\n                  \"word\": \"√技能提升练\",\n                  \"x\": 207,\n                  \"y\": 506\n            }\n      ],\n      \"width\": 4716\n}",
  "Code": "noPermission",
  "Message": "You are not authorized to perform this operation."
}
```

