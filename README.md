# <img src="https://github.com/user-attachments/assets/cac75d32-c147-4c2f-bfbc-c01fc7cb12d8" width="50" height="50" bottom-padding="0"> Project Title: linkedin-chatbot-job (Tiếng việt)

# 📌 Overview:
Dự án này được phát triển bởi nhóm MNT (Math and Technology), một nhóm đam mê công nghệ từ trường Đại học Khoa học Tự nhiên với mong muốn tìm hiểu và ứng dụng các công cụ AI phổ biến. Đây là một dự án nhỏ nhưng có mục tiêu rõ ràng: nghiên cứu, triển khai và tối ưu hóa các giải pháp sử dụng AI và công nghệ tiên tiến. Chúng tôi mong muốn tạo ra một nền tảng có tính thực tiễn cao, đồng thời học hỏi và chia sẻ kiến thức. 

# 🌟 Features: 
## 1. Web Scrapping:
Lấy tất cả thông tin từ job liên quan về từ khóa: Data, Data Science, Data Engineer, Data Analyst.

## 2. AI chatbot:
Dự án có các chức năng cơ bản như:
- Tạo new chat
- Xóa chat
- Chat về job mới nhất trên linkedin
- Chat với memory (tức là bạn có thể hỏi về thông tin của câu trước)
- Xem lịch sử chat

# 🎥 Demo website:
Later Update

# 🛠️ Installation:
## Clone project
```bash
git clone <link to github project>
```

## Installation necessary package
```python
pip install -r requiremnents
```

# ⚙️ Usage:
## Web Scrapping: 
```bash
cd "<current_path>/linkedin-chatbot-job-MNT-team/web_scrapping"
python main.py
```
or
```bash
cd "<current_path>/linkedin-chatbot-job-MNT-team/web_scrapping"
python "<current_path>/linkedin-chatbot-job-MNT-team/web_scrapping/main.py"
```
## AI chatbot:
```bash
streamlit run streamlit_app/app/main.py
```

# 🏗️ Architecture for this project:
## Web Scrapping
Later Update

## AI
Later Update

# 📊 Database schema:
## Database for job data:
Chúng tôi sử dụng Aiven platform, DBMS sử dụng là MySQL, với cấu hình là:
- 1 CPU
- 1 GB RAM (processing)
- 5 GB Storage

là bản free-plan hỗ trợ cho các dự án phi lợi nhuận, tham khảo tại đây: https://console.aiven.io/

## Connect to Aiven:
- Nếu bạn tự tạo database, thì bạn có thể vào service của bạn và nhấn vào quick connnect và chọn python.
- Còn nều bạn không phải owner, thì aiven có feature là add user vào.
- Aiven hiện tại không có feature view table trên chính nền tảng của họ, nên chỉ có thể sử dụng code với các command để check.

## Database for Memory Chat:
Chúng tôi sử dụng Mongo Atlas, là phiên bản mongodb nhưng trên cloud hỗ trợ rất nhiều cho developer phát triển.
Một số lưu ý khi bạn sử dụng mongo atlas:
- Nếu muốn connect thì bạn cần URI, và mongo atlas bảo mật rất tốt nên chỉ có thể sử dụng connection (0.0.0.0, tức là cho phép mọi địa chỉ IP truy cập vào), thông thường sẽ bị chặn toàn bộ IP, trừ IP local của bạn.
- Nên xem kĩ các dung lượng lưu trữ của Mongo atlas, vì free-plan nên giới hạn cũng khá nhiều, bạn không thể sử dụng VPC hay các cách kết nối nâng cao khác ngoài 0.0.0.0, nếu xài free-plan.

# 🤝 Contributing:
Leader: Hàng Tấn Tài
Member: Nguyễn Hoàng Nam
Member: Hồ Quốc Tuấn

# 📝 License:
![License](https://img.shields.io/badge/License-MIT-blue.svg)  
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
# 🙏 Thank you!
