# 阿里云 OCR 测试总结

## ✅ 当前状态

### 已解决的问题
1. ✅ **401 权限问题** - RAM 权限已正确配置
2. ✅ **URL 方式正常工作** - 使用图片 URL 可以成功识别

### 待解决的问题
1. ❌ **Body 方式 415 错误** - 使用 base64 上传图片时格式不支持

## 📊 测试结果

### 测试 1: URL 方式 ✅
```bash
python test/test_url_only.py
```

**结果：成功！**
- 图片 URL: https://i.ibb.co/9knYcZdV/Screen-Shot-2025-11-16-173004-542.png
- 识别到 1 道题目
- 内容：北斗卫星导航系统...

### 测试 2: Body 方式（base64）❌
```bash
python test/convert_and_test.py ~/Downloads/ScreenShot_2025-11-16_173004_542.png
```

**结果：415 错误**
- 错误信息：The image format or content is not supported
- 已尝试：转换为标准 JPG，仍然失败

## 🎯 推荐方案

### 方案 A：使用 URL 方式（推荐）✅

**优点：**
- ✅ 已验证可用
- ✅ 稳定可靠
- ✅ 性能更好（阿里云直接下载）
- ✅ 不受 base64 编码影响

**使用方法：**
```python
# 1. 上传图片到图床（如 ImgBB, 阿里云 OSS 等）
# 2. 获取公网可访问的 URL
# 3. 使用 URL 调用 OCR
ocr_payload = {
    "image_url": "https://your-image-url.com/image.png",
    "image_base64": None
}
```

### 方案 B：继续调试 Body 方式（可选）

如果必须使用 base64 上传，需要进一步调试：

```bash
# 运行调试脚本（需要在正确的虚拟环境中）
cd learning_diagnosis_backend
python test/quick_test_body.py ~/Downloads/image.png
```

## 🚀 当前最佳实践

### 1. 使用阿里云 OCR（URL 方式）

**测试脚本：** `test/test_diagnostic.py`

```bash
python test/test_diagnostic.py
```

**特点：**
- ✅ 使用图片 URL
- ✅ 完整的 OCR + 诊断流程
- ✅ 详细的输出格式
- ✅ 完善的错误处理

### 2. 本地图片 URL 化方案

如果有本地图片，可以：

**选项 1：使用图床服务**
```bash
# 上传到 ImgBB（免费）
curl -F "image=@/path/to/image.png" \
  "https://api.imgbb.com/1/upload?key=YOUR_API_KEY"
```

**选项 2：使用阿里云 OSS**
```bash
# 上传到阿里云对象存储
ossutil cp /path/to/image.png oss://your-bucket/
```

**选项 3：临时本地服务器**
```bash
# 启动简单的文件服务器
cd /path/to/images
python -m http.server 8001

# 然后使用 URL: http://localhost:8001/image.png
```

## 📝 配置说明

### .env 配置（URL 方式）

```env
# 阿里云 OCR 配置
ALIYUN_ACCESS_KEY_ID=LTAI5tRm...
ALIYUN_ACCESS_KEY_SECRET=your_secret
ALIYUN_OCR_ENDPOINT=cn-hangzhou.aliyuncs.com

# OCR 提供者：优先阿里云，失败回退 LLM
OCR_PROVIDER=auto
```

### RAM 权限要求

确保 AccessKey 对应的用户拥有以下权限：
- `AliyunOCRFullAccess` 或
- `AliyunOCRReadOnlyAccess`

## 🔧 故障排查

### 401 错误
- 检查 RAM 权限是否正确配置
- 等待 1-2 分钟让权限生效

### 400 错误（URL unavailable）
- 确保图片 URL 公网可访问
- 检查 URL 格式正确
- 验证图片大小 < 10MB

### 415 错误（body 方式）
- 暂时使用 URL 方式替代
- 等待进一步调试结果

## 📚 相关文档

- [阿里云 OCR 官方文档](https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-recognizeeduquestionocr)
- [RAM 权限配置](https://ram.console.aliyun.com/)
- [错误码说明](https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-errorcodes)

## ✅ 结论

**当前建议：**
1. ✅ **生产环境使用 URL 方式**
2. ✅ **已验证可用且稳定**
3. ⏸️ **body 方式暂时搁置，非关键功能**

如需使用本地图片，建议将图片上传到 OSS 或图床后再调用 OCR API。

