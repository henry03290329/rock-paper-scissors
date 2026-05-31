# 🎮 石头剪刀布——AI 必赢版

一个使用计算机视觉进行手势识别的交互式游戏。通过摄像头实时识别用户手势，并由 AI 计算出必胜手势，让你体验“逢赌必输”的乐趣。

## 🎯 项目亮点

- **实时手势识别**：基于 MediaPipe 手部关键点检测，毫秒级识别响应
- **AI 必胜逻辑**：程序根据规则自动出克制的拳，保证每次都赢
- **稳定状态检测**：连续 15 帧手势稳定后触发，有效避免抖动误判
- **镜像画面显示**：画面水平翻转，像照镜子一样自然

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.7+ | 项目开发语言 |
| OpenCV | 摄像头视频流捕获与图像处理 |
| MediaPipe | 手部 21 个关键点检测与手势识别 |

## 🚀 快速开始（Windows）

1. **打开命令提示符**（Win + R → 输入 `cmd` → 回车）

2. **克隆或下载本仓库**
   - 直接下载 ZIP：点击仓库首页绿色的 `<> Code` → `Download ZIP` 并解压
   - 或使用 Git 克隆：`git clone https://github.com/henry03290329/rock-paper-scissors.git`

3. **进入项目文件夹**
   ```bash
   cd rock-paper-scissors
安装依赖库

bash
pip install opencv-python mediapipe
如果遇到权限问题，可以尝试 pip install --user opencv-python mediapipe

运行游戏

bash
python RPS.py
退出游戏：在摄像头画面窗口中按下键盘上的 q 键

📂 文件说明
RPS.py：游戏主程序（完整源代码）

rock.png / paper.png / scissors.png：游戏界面图片资源（当前版本未使用，可忽略）

Iriun Webcam/：（个人备份文件夹） 手机摄像头电脑客户端安装包，与本游戏项目无关

📝 注意事项
请确保电脑有可用的摄像头

手势识别时保持手部正对镜头、光线充足

每轮需要稳定手势约 0.5 秒（连续 15 帧）才会触发结果

📄 许可证
本仓库仅用于个人作品展示与学习交流。
